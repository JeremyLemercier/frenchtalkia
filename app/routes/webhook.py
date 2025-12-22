import logging
from fastapi import APIRouter, Request, Response
from typing import Any

from app.config import get_configuracao

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = logging.getLogger(__name__)


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
        dict: Confirmação de recebimento
    """
    # PARA FAZER:Implementar processamento real do webhook
    # Este é um stub - apenas confirma recebimento
    
    try:
        payload = await request.json()
        
        # Em implementação real, processar o payload para extrair
        # informações da mensagem (telefone, conteúdo, tipo, etc.)
        
        return {
            "status": "received",
            "message": "Webhook recebido com sucesso"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erro ao processar webhook: {str(e)}"
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