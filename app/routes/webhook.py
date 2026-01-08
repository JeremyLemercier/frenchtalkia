import asyncio
from pathlib import Path
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Request, Response

from app.config import get_configuracao
from app.models import AudioMessage, TextMessage, WebhookPayload
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
    arquivo_audio: Path | None = None,
) -> None:
    """Salva resultado de integração."""
    cfg = get_configuracao()
    if getattr(cfg, "integration_whatsapp", False):
        try:
            from tests.integration.whatsapp_webhook import (
                salvar_resultado_integracao as _salvar_integ,
            )

            # run sync saving in threadpool
            result_dir = await asyncio.to_thread(
                _salvar_integ, tipo_mensagem, dados_extraidos, arquivo_audio
            )
            if result_dir:
                logger.info(f"Resultado de integração salvo em {result_dir}")
            return
        except Exception as e:
            logger.exception(f"Erro ao salvar integração via módulo de testes: {e}")

    # fallback to service method
    result_dir = whatsapp_service.salvar_resultado_integracao(
        tipo_mensagem=tipo_mensagem,
        dados_extraidos=dados_extraidos,
        arquivo_audio=arquivo_audio,
    )
    if result_dir:
        logger.info(f"Resultado de integração salvo em {result_dir}")


def _schedule_create_task(coro):
    """Helper to schedule coroutine tasks. Tests may monkeypatch this to run
    coroutines on a background loop when BackgroundTasks executes callables
    in a threadpool.
    """
    return asyncio.create_task(coro)


async def _baixar_audio_para_integracao(
    whatsapp_service: WhatsAppService,
    media_id: str,
) -> Path | None:
    """Baixa áudio para integração."""
    cfg = get_configuracao()
    if getattr(cfg, "integration_whatsapp", False):
        try:
            from tests.integration.whatsapp_webhook import (
                baixar_audio_para_integracao as _baixar_integ,
            )

            arquivo_audio = await _baixar_integ(whatsapp_service, media_id)
            if arquivo_audio:
                logger.info(f"Áudio baixado para integração: {arquivo_audio}")
            return arquivo_audio
        except Exception as e:
            logger.exception(f"Erro ao baixar áudio via módulo de testes: {e}")
            return None

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

        # Reuse shared service instance created at startup when available
        whatsapp_service: WhatsAppService | None = getattr(request.app.state, "whatsapp_service", None)

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
                whatsapp_svc: WhatsAppService | None = getattr(request.app.state, "whatsapp_service", None)
                gladia_svc = getattr(request.app.state, "gladia_service", None)
                mistral_svc = getattr(request.app.state, "mistral_service", None)
                murf_svc = getattr(request.app.state, "murf_service", None)
                usuario_svc = getattr(request.app.state, "usuario_service", None)

                telefone = mensagem.get("from")
                tipo = mensagem.get("type")

                # Ensure we have a per-user session and lock processing per-user
                if usuario_svc is not None and telefone:
                    try:
                        usuario_svc.bloquear_usuario(telefone)
                    except Exception:
                        logger.exception(f"Falha ao bloquear usuário {telefone} para processamento")

                # Load runtime config
                cfg = get_configuracao()

                if tipo == "text":
                    if getattr(cfg, "integration_whatsapp", False):
                        # Integration mode: send predefined sample text and save artifacts
                        try:
                            from tests.integration.whatsapp_webhook import get_sample_text

                            sample_text = await asyncio.to_thread(get_sample_text)
                        except Exception:
                            sample_text = "[integration reply]"
                        try:
                            if whatsapp_svc is not None:
                                await whatsapp_svc.enviar_mensagem_texto(telefone, sample_text)
                            else:
                                logger.warning("WhatsAppService não disponível no estado da app (modo integração)")
                        except Exception:
                            logger.exception("Erro ao enviar texto de integração")
                        # save artifacts
                        dados = _processar_texto(mensagem)
                        await _salvar_integracao(whatsapp_svc, "text", dados)
                    else:
                        # Extract and process text (run sync stubs in threadpool)
                        dados = _processar_texto(mensagem)
                        texto_usuario = dados.get("conteudo", "")
                        # Call LLM service (blocking stub) in thread
                        # Use per-user conversation_id stored in session to avoid mixing
                        conversation_id = None
                        agent_id = None
                        if usuario_svc is not None and telefone:
                            try:
                                sess = usuario_svc.obter_sessao_usuario(telefone)
                                conversation_id = sess.conversation_id_mistral
                                agent_id = sess.agent_id_mistral
                            except Exception:
                                logger.exception(f"Erro ao obter sessão para {telefone}")

                        # Choose a default agent if not present
                        if agent_id is None:
                            agent_id = "agent_fr_basic"

                        if mistral_svc is not None:
                            # If there's no conversation yet, start one and persist its id
                            if not conversation_id:
                                try:
                                    conv_id, primeira_resposta = await asyncio.to_thread(
                                        mistral_svc.iniciar_conversa, agent_id, texto_usuario
                                    )
                                    conversation_id = conv_id
                                    # Persist conversation id in session
                                    try:
                                        # sessao_storage is available via usuario_service
                                        usuario_svc.sessao_storage.atualizar_selecoes(
                                            telefone, agent_id_mistral=agent_id, conversation_id_mistral=conversation_id
                                        )
                                    except Exception:
                                        logger.exception(f"Não foi possível salvar conversation_id para {telefone}")
                                    resposta = primeira_resposta
                                except Exception:
                                    logger.exception("Erro ao iniciar conversa no Mistral")
                                    resposta = ""
                            else:
                                try:
                                    resposta = await asyncio.to_thread(
                                        mistral_svc.continuar_conversa, conversation_id, texto_usuario
                                    )
                                except Exception:
                                    logger.exception("Erro ao continuar conversa no Mistral")
                                    resposta = ""
                        else:
                            resposta = ""
                            logger.warning("MistralService não disponível no estado da app")
                        # Send response (se disponível)
                        if whatsapp_svc is not None:
                            await whatsapp_svc.enviar_mensagem_texto(telefone, resposta)
                        else:
                            logger.warning("WhatsAppService não disponível no estado da app")

                elif tipo == "audio":
                    if getattr(cfg, "integration_whatsapp", False):
                        # Integration mode: download original audio, save artifacts, and send sample audio
                        dados = _processar_audio(mensagem)
                        media_id = dados.get("media_id")
                        arquivo = await _baixar_audio_para_integracao(whatsapp_svc, media_id)
                        try:
                            from tests.integration.whatsapp_webhook import get_sample_audio_path

                            sample_audio = await asyncio.to_thread(get_sample_audio_path)
                        except Exception:
                            sample_audio = Path("tests/utils/audios/sample_audio.ogg")
                        try:
                            if whatsapp_svc is not None:
                                await whatsapp_svc.enviar_mensagem_audio(telefone, sample_audio)
                            else:
                                logger.warning("WhatsAppService não disponível no estado da app (modo integração)")
                        except Exception:
                            logger.exception("Erro ao enviar audio de integração")
                        # save artifacts
                        await _salvar_integracao(whatsapp_svc, "audio", dados, arquivo)
                    else:
                        dados = _processar_audio(mensagem)
                        media_id = dados.get("media_id")
                        # Baixar audio (async, non-blocking file I/O inside service)
                        if whatsapp_svc is not None:
                            arquivo = await whatsapp_svc.baixar_audio(media_id)
                        else:
                            arquivo = None
                            logger.warning("WhatsAppService não disponível para baixar áudio")

                        # Transcrever (blocking stub) in thread
                        if gladia_svc is not None and arquivo is not None:
                            texto_transcrito = await asyncio.to_thread(gladia_svc.transcrever_audio, arquivo)
                        else:
                            texto_transcrito = ""
                            logger.warning("GladiaService não disponível ou arquivo ausente")

                        # Process via LLM
                        if mistral_svc is not None:
                            resposta_texto = await asyncio.to_thread(mistral_svc.continuar_conversa, "default", texto_transcrito)
                        else:
                            resposta_texto = ""
                            logger.warning("MistralService não disponível no estado da app")

                        # Generate TTS (blocking) in thread
                        if murf_svc is not None:
                            caminho_audio, _dur = await asyncio.to_thread(murf_svc.gerar_audio, resposta_texto)
                        else:
                            caminho_audio = None
                            logger.warning("MurfService não disponível no estado da app")

                        # Send audio response
                        if whatsapp_svc is not None and caminho_audio is not None:
                            await whatsapp_svc.enviar_mensagem_audio(telefone, caminho_audio)
                        else:
                            logger.warning("Não foi possível enviar resposta de áudio: serviço ou áudio ausente")

                else:
                    logger.warning(f"Tipo de mensagem em background não suportado: {tipo}")

            except Exception as e:
                logger.exception(f"Erro no processamento em background: {str(e)}")
            finally:
                # Always release per-user processing lock
                try:
                    if usuario_svc is not None and telefone:
                        usuario_svc.desbloquear_usuario(telefone)
                except Exception:
                    logger.exception(f"Falha ao desbloquear usuário {telefone}")

        # Processar conforme tipo de mensagem (enqueue background task)
        if mensagem_tipo == "text":
            dados_extraidos = _processar_texto(mensagem_dict)
            # schedule background processing and return immediately
            background_tasks.add_task(_schedule_create_task, _process_message_bg(mensagem_dict))
            return _criar_resposta("received", "Mensagem de texto recebida e agendada", dados_extraidos)

        if mensagem_tipo == "audio":
            dados_extraidos = _processar_audio(mensagem_dict)
            # schedule background processing and return immediately
            background_tasks.add_task(_schedule_create_task, _process_message_bg(mensagem_dict))
            return _criar_resposta("received", "Mensagem de áudio recebida e agendada", dados_extraidos)

        # Tipo não suportado
        dados_extraidos = _processar_tipo_desconhecido(mensagem_dict)
        logger.warning(f"Tipo de mensagem não suportado: {dados_extraidos['tipo']}")
        # If integration mode active, schedule artifact save in background (keep request fast)
        if config.integration_whatsapp:
            async def _save_unknown():
                try:
                    await _salvar_integracao(whatsapp_service, dados_extraidos["tipo"], dados_extraidos)
                except Exception:
                    logger.exception("Erro ao salvar integração para tipo desconhecido")

            background_tasks.add_task(_schedule_create_task, _save_unknown())
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
