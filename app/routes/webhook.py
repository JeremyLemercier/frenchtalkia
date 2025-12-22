from fastapi import APIRouter, Request, Response
from typing import Any

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
    # PARA FAZER:Implementar verificação real do webhook
    # Este é um stub - sempre retorna sucesso
    
    # Simular verificação
    hub_mode = request.query_params.get("hub.mode")
    hub_challenge = request.query_params.get("hub.challenge")
    hub_verify_token = request.query_params.get("hub.verify_token")
    
    # Em implementação real, verificar hub_verify_token com token configurado
    if hub_mode == "subscribe" and hub_challenge:
        return Response(content=hub_challenge, media_type="text/plain")
    
    return Response(status_code=403)


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