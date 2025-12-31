from fastapi import APIRouter, Request, Response, BackgroundTasks
from pathlib import Path
from typing import Any, Optional
import asyncio

from app.config import get_configuracao
from app.models import WebhookPayload, TextMessage, AudioMessage
from app.services.whatsapp_service import WhatsAppService
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["webhook"])


@router.get("/whatsapp")
async def webhook_verify(request: Request) -> Response:
    """
    Endpoint para verificação do webhook do WhatsApp.

    Args:
        request: Request HTTP com parâmetros de verificação

    Returns:
        Response: Resposta com challenge token se verificação bem-sucedida
    """
    try:
        hub_mode = request.query_params.get("hub.mode")
        hub_challenge = request.query_params.get("hub.challenge")
        hub_verify_token = request.query_params.get("hub.verify_token")

        logger.debug(
            f"Parâmetros recebidos: hub.mode={hub_mode}, hub.challenge={hub_challenge}, hub.verify_token={hub_verify_token}"
        )

        config = get_configuracao()

        if not hub_challenge:
            logger.warning("hub.challenge não fornecido")
            return Response(status_code=403)

        if hub_mode != "subscribe":
            logger.warning(f"hub.mode inválido: {hub_mode}")
            return Response(status_code=403)

        if hub_verify_token != config.whatsapp_verify_token:
            logger.warning(f"hub.verify_token inválido: {hub_verify_token}")
            return Response(status_code=403)

        logger.info("Verificação do webhook bem-sucedida")
        return Response(content=hub_challenge, media_type="text/plain")

    except Exception as e:
        logger.error(f"Erro na verificação do webhook: {str(e)}")
        return Response(status_code=500)


def _extrair_dados_base(mensagem_dict: dict[str, Any]) -> dict[str, Any]:
    """Extrai dados base comuns a todos os tipos de mensagem."""
    return {
        "telefone": mensagem_dict.get("from"),
        "mensagem_id": mensagem_dict.get("id"),
        "timestamp": mensagem_dict.get("timestamp"),
    }


def _processar_texto(mensagem_dict: dict[str, Any]) -> dict[str, Any]:
    """Processa mensagem de texto e retorna dados extraídos."""
    text_message = TextMessage.model_validate(mensagem_dict)
    dados = _extrair_dados_base(mensagem_dict)
    dados["tipo"] = "text"
    dados["conteudo"] = text_message.body
    return dados


def _processar_audio(mensagem_dict: dict[str, Any]) -> dict[str, Any]:
    """Processa mensagem de áudio e retorna dados extraídos."""
    audio_message = AudioMessage.model_validate(mensagem_dict)
    dados = _extrair_dados_base(mensagem_dict)
    dados["tipo"] = "audio"
    dados["media_id"] = audio_message.audio_id
    dados["mime_type"] = audio_message.mime_type
    return dados


def _processar_tipo_desconhecido(mensagem_dict: dict[str, Any]) -> dict[str, Any]:
    """Processa mensagem de tipo desconhecido e retorna dados extraídos."""
    dados = _extrair_dados_base(mensagem_dict)
    dados["tipo"] = mensagem_dict.get("type") or "unknown"
    return dados


async def _salvar_integracao(
    whatsapp_service: WhatsAppService,
    tipo_mensagem: str,
    dados_extraidos: dict[str, Any],
    arquivo_audio: Optional[Path] = None,
) -> None:
    """Salva resultado de integração."""
    result_dir = whatsapp_service.salvar_resultado_integracao(
        tipo_mensagem=tipo_mensagem,
        dados_extraidos=dados_extraidos,
        arquivo_audio=arquivo_audio,
    )
    if result_dir:
        logger.info(f"Resultado de integração salvo em {result_dir}")


async def _baixar_audio_para_integracao(
    whatsapp_service: WhatsAppService,
    media_id: str,
) -> Optional[Path]:
    """Baixa áudio para integração."""
    try:
        arquivo_audio = await whatsapp_service.baixar_audio(media_id)
        logger.info(f"Áudio baixado para integração: {arquivo_audio}")
        return arquivo_audio
    except Exception as e:
        logger.error(f"Erro ao baixar áudio para integração: {str(e)}")
        return None


def _criar_resposta(
    status: str,
    message: str,
    dados_extraidos: dict[str, Any],
) -> dict[str, Any]:
    """Cria resposta padronizada do webhook."""
    return {
        "status": status,
        "message": message,
        "data": dados_extraidos,
    }


@router.post("/whatsapp")
async def webhook_receive(request: Request, background_tasks: BackgroundTasks) -> dict[str, Any]:
    """
    Endpoint para receber mensagens do webhook do WhatsApp.

    Args:
        request: Request HTTP com payload da mensagem

    Returns:
        dict: Confirmação de recebimento com dados processados
    """
    try:
        config = get_configuracao()

        # Reuse shared service instance created at startup
        whatsapp_service: WhatsAppService = request.app.state.whatsapp_service

        payload_data = await request.json()
        logger.debug(f"Payload recebido: {payload_data}")

        payload = WebhookPayload.model_validate(payload_data)
        mensagem_dict = payload.extrair_mensagem()
        
        if not mensagem_dict:
            logger.warning("Nenhuma mensagem encontrada no payload")
            return {"status": "error", "message": "Nenhuma mensagem encontrada"}

        mensagem_tipo = mensagem_dict.get("type")
        logger.info(
            f"Mensagem recebida - Tipo: {mensagem_tipo}, "
            f"Telefone: {mensagem_dict.get('from')}, ID: {mensagem_dict.get('id')}"
        )
        # Schedule heavy processing in background to return immediately
        async def _process_message_bg(mensagem: dict[str, Any]):
            try:
                whatsapp_svc: WhatsAppService = request.app.state.whatsapp_service
                gladia_svc = request.app.state.gladia_service
                mistral_svc = request.app.state.mistral_service
                murf_svc = request.app.state.murf_service

                telefone = mensagem.get("from")
                tipo = mensagem.get("type")

                if tipo == "text":
                    # Extract and process text (run sync stubs in threadpool)
                    dados = _processar_texto(mensagem)
                    texto_usuario = dados.get("conteudo", "")
                    # Call LLM service (blocking stub) in thread
                    resposta = await asyncio.to_thread(mistral_svc.continuar_conversa, "default", texto_usuario)
                    # Send response
                    await whatsapp_svc.enviar_mensagem_texto(telefone, resposta)

                elif tipo == "audio":
                    dados = _processar_audio(mensagem)
                    media_id = dados.get("media_id")
                    # Baixar audio (async, non-blocking file I/O inside service)
                    arquivo = await whatsapp_svc.baixar_audio(media_id)
                    # Transcrever (blocking stub) in thread
                    texto_transcrito = await asyncio.to_thread(gladia_svc.transcrever_audio, arquivo)
                    # Process via LLM
                    resposta_texto = await asyncio.to_thread(mistral_svc.continuar_conversa, "default", texto_transcrito)
                    # Generate TTS (blocking) in thread
                    caminho_audio, _dur = await asyncio.to_thread(murf_svc.gerar_audio, resposta_texto)
                    # Send audio response
                    await whatsapp_svc.enviar_mensagem_audio(telefone, caminho_audio)

                else:
                    logger.warning(f"Tipo de mensagem em background não suportado: {tipo}")

            except Exception as e:
                logger.exception(f"Erro no processamento em background: {str(e)}")

        # Processar conforme tipo de mensagem (enqueue background task)
        if mensagem_tipo == "text":
            dados_extraidos = _processar_texto(mensagem_dict)
            # Save integration artifacts in test mode, still schedule background
            if config.integration_test_mode:
                await _salvar_integracao(whatsapp_service, "text", dados_extraidos)
            # schedule background processing and return immediately
            background_tasks.add_task(asyncio.create_task, _process_message_bg(mensagem_dict))
            return _criar_resposta("received", "Mensagem de texto recebida e agendada", dados_extraidos)

        if mensagem_tipo == "audio":
            dados_extraidos = _processar_audio(mensagem_dict)
            if config.integration_test_mode:
                # download for integration storage
                arquivo_audio: Optional[Path] = await _baixar_audio_para_integracao(whatsapp_service, dados_extraidos["media_id"])
                await _salvar_integracao(whatsapp_service, "audio", dados_extraidos, arquivo_audio)
            # schedule background processing and return immediately
            background_tasks.add_task(asyncio.create_task, _process_message_bg(mensagem_dict))
            return _criar_resposta("received", "Mensagem de áudio recebida e agendada", dados_extraidos)
        
        # Tipo não suportado
        dados_extraidos = _processar_tipo_desconhecido(mensagem_dict)
        logger.warning(f"Tipo de mensagem não suportado: {dados_extraidos['tipo']}")
        if config.integration_test_mode:
            await _salvar_integracao(whatsapp_service, dados_extraidos["tipo"], dados_extraidos)
        return _criar_resposta("received", f"Tipo de mensagem não suportado: {dados_extraidos['tipo']}", dados_extraidos)

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return {"status": "error", "message": "Erro ao processar webhook"}


@router.get("/health")
async def webhook_health() -> dict[str, str]:
    """
    Endpoint de health check para o webhook.

    Returns:
        dict: Status do serviço de webhook
    """
    return {"status": "ok", "service": "webhook"}
