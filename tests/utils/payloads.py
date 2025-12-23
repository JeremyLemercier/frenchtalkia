import json
from pathlib import Path
from typing import Any


def load_text_webhook_payload() -> dict[str, Any]:
    """
    Carrega payload real de texto de tests/utils/payloads/text_message.json.
    
    Returns:
        dict[str, Any]: Payload completo do webhook de texto
    """
    payload_path = Path(__file__).parent / "utils" / "payloads" / "text_message.json"
    with open(payload_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_audio_webhook_payload() -> dict[str, Any]:
    """
    Carrega payload real de áudio de tests/utils/payloads/audio_message.json.
    
    Returns:
        dict[str, Any]: Payload completo do webhook de áudio
    """
    payload_path = Path(__file__).parent / "utils" / "payloads" / "audio_message.json"
    with open(payload_path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_custom_text_payload(telefone: str, texto: str) -> dict[str, Any]:
    """
    Cria payload customizado de mensagem de texto.
    
    Args:
        telefone: Número de telefone do remetente
        texto: Conteúdo da mensagem de texto
        
    Returns:
        dict[str, Any]: Payload completo do webhook de texto
    """
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511999999999",
                                "phone_number_id": "123456789"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Usuário Teste"},
                                    "wa_id": telefone
                                }
                            ],
                            "messages": [
                                {
                                    "from": telefone,
                                    "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q2RTY3RTcA",
                                    "timestamp": "1704067200",
                                    "type": "text",
                                    "text": {"body": texto}
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }


def create_custom_audio_payload(telefone: str, media_id: str) -> dict[str, Any]:
    """
    Cria payload customizado de mensagem de áudio.
    
    Args:
        telefone: Número de telefone do remetente
        media_id: ID da mídia de áudio
        
    Returns:
        dict[str, Any]: Payload completo do webhook de áudio
    """
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "123456789012345",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "5511999999999",
                                "phone_number_id": "123456789"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Usuário Teste"},
                                    "wa_id": telefone
                                }
                            ],
                            "messages": [
                                {
                                    "from": telefone,
                                    "id": "wamid.HBgLMTY1MDUwNzY1MjAVAgARGBI5QTNDQTVCM0Q0Q2RTY3RTcA",
                                    "timestamp": "1704067300",
                                    "type": "audio",
                                    "audio": {
                                        "id": media_id,
                                        "mime_type": "audio/ogg; codecs=opus",
                                        "sha256": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2"
                                    }
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
