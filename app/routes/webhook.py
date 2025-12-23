from fastapi import APIRouter, Request, Response
from typing import Any

from app.config import get_configuracao
from app.models import WebhookPayload, TextMessage, AudioMessage
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
        # Extrair parâmetros da requisição
        hub_mode = request.query_params.get("hub.mode")
        hub_challenge = request.query_params.get("hub.challenge")
        hub_verify_token = request.query_params.get("hub.verify_token")
        
        logger.debug(f"Parâmetros recebidos: hub.mode={hub_mode}, hub.challenge={hub_challenge}, hub.verify_token={hub_verify_token}")
        
        # Obter configuração
        config = get_configuracao()
        
        # Validar se hub.challenge está presente
        if not hub_challenge:
            logger.warning("hub.challenge não fornecido")
            return Response(status_code=403)
        
        # Validar se hub.mode == "subscribe"
        if hub_mode != "subscribe":
            logger.warning(f"hub.mode inválido: {hub_mode}")
            return Response(status_code=403)
        
        # Validar se hub.verify_token corresponde ao token configurado
        if hub_verify_token != config.whatsapp_verify_token:
            logger.warning(f"hub.verify_token inválido: {hub_verify_token}")
            return Response(status_code=403)
        
        # Se válido: retornar challenge
        logger.info("Verificação do webhook bem-sucedida")
        return Response(content=hub_challenge, media_type="text/plain")
        
    except Exception as e:
        logger.error(f"Erro na verificação do webhook: {str(e)}")
        return Response(status_code=500)


@router.post("/whatsapp")
async def webhook_receive(request: Request) -> dict[str, Any]:
    """
    Endpoint para receber mensagens do webhook do WhatsApp.
    
    Args:
        request: Request HTTP com payload da mensagem
        
    Returns:
        dict: Confirmação de recebimento com dados processados
    """
    try:
        # Receber payload JSON
        payload_data = await request.json()
        logger.debug(f"Payload recebido: {payload_data}")
        
        # Validar payload com WebhookPayload
        payload = WebhookPayload.model_validate(payload_data)
        
        # Extrair primeira mensagem
        mensagem_dict = payload.extrair_mensagem()
        if not mensagem_dict:
            logger.warning("Nenhuma mensagem encontrada no payload")
            return {
                "status": "error",
                "message": "Nenhuma mensagem encontrada"
            }
        
        # Identificar tipo de mensagem
        mensagem_tipo = mensagem_dict.get("type")
        telefone = mensagem_dict.get("from")
        mensagem_id = mensagem_dict.get("id")
        timestamp = mensagem_dict.get("timestamp")
        
        logger.info(f"Mensagem recebida - Tipo: {mensagem_tipo}, Telefone: {telefone}, ID: {mensagem_id}")
        
        # Processar conforme tipo de mensagem
        if mensagem_tipo == "text":
            # Extrair mensagem de texto
            text_message = TextMessage.model_validate(mensagem_dict)
            conteudo = text_message.body
            
            return {
                "status": "received",
                "message": "Mensagem de texto recebida com sucesso",
                "data": {
                    "tipo": "text",
                    "telefone": telefone,
                    "mensagem_id": mensagem_id,
                    "timestamp": timestamp,
                    "conteudo": conteudo
                }
            }
            
        elif mensagem_tipo == "audio":
            # Extrair mensagem de áudio
            audio_message = AudioMessage.model_validate(mensagem_dict)
            media_id = audio_message.audio_id
            mime_type = audio_message.mime_type
            
            return {
                "status": "received",
                "message": "Mensagem de áudio recebida com sucesso",
                "data": {
                    "tipo": "audio",
                    "telefone": telefone,
                    "mensagem_id": mensagem_id,
                    "timestamp": timestamp,
                    "media_id": media_id,
                    "mime_type": mime_type
                }
            }
        
        else:
            logger.warning(f"Tipo de mensagem não suportado: {mensagem_tipo}")
            return {
                "status": "received",
                "message": f"Tipo de mensagem não suportado: {mensagem_tipo}",
                "data": {
                    "tipo": mensagem_tipo,
                    "telefone": telefone,
                    "mensagem_id": mensagem_id,
                    "timestamp": timestamp
                }
            }
            
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        return {
            "status": "error",
            "message": "Erro ao processar webhook"
        }


@router.get("/health")
async def webhook_health() -> dict[str, str]:
    """
    Endpoint de health check para o webhook.
    
    Returns:
        dict: Status do serviço de webhook
    """
    return {
        "status": "ok",
        "service": "webhook"
    }