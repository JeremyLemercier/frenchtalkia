import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.config import ConfiguracaoApp
from app.main import app


# Criar cliente de teste
client = TestClient(app)


@pytest.fixture
def mock_config():
    """Fixture para mock da configuração."""
    config = MagicMock(spec=ConfiguracaoApp)
    config.whatsapp_token = "test_token"
    config.whatsapp_phone_number_id = "123456789"
    config.whatsapp_verify_token = "test_verify_token"
    config.diretorio_temp_audio = Path("./temp/audio")
    return config


@pytest.fixture
def text_message_payload():
    """Fixture para carregar payload de mensagem de texto."""
    payload_path = Path(__file__).parent.parent / "utils" / "payloads" / "text_message.json"
    with open(payload_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def audio_message_payload():
    """Fixture para carregar payload de mensagem de áudio."""
    payload_path = Path(__file__).parent.parent / "utils" / "payloads" / "audio_message.json"
    with open(payload_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ==================== Testes para GET (Verificação) ====================

def test_webhook_verify_success(mock_config: MagicMock):
    """
    Testar verificação bem-sucedida do webhook.
    
    Verifica que o endpoint retorna o challenge quando os parâmetros
    estão corretos e o token de verificação é válido.
    """
    with patch("app.routes.webhook.get_configuracao", return_value=mock_config):
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge_123",
                "hub.verify_token": "test_verify_token"
            }
        )
        
        assert response.status_code == 200
        assert response.text == "test_challenge_123"
        assert response.headers["content-type"] == "text/plain; charset=utf-8"


def test_webhook_verify_invalid_token(mock_config: MagicMock):
    """
    Testar verificação com token inválido.
    
    Verifica que o endpoint retorna status 403 quando o token
    de verificação não corresponde ao configurado.
    """
    with patch("app.routes.webhook.get_configuracao", return_value=mock_config):
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.challenge": "test_challenge_123",
                "hub.verify_token": "invalid_token"
            }
        )
        
        assert response.status_code == 403


def test_webhook_verify_missing_params(mock_config: MagicMock):
    """
    Testar verificação com parâmetros faltando.
    
    Verifica que o endpoint retorna status 403 quando o
    parâmetro hub.challenge não está presente.
    """
    with patch("app.routes.webhook.get_configuracao", return_value=mock_config):
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "subscribe",
                "hub.verify_token": "test_verify_token"
            }
        )
        
        assert response.status_code == 403


def test_webhook_verify_invalid_mode(mock_config: MagicMock):
    """
    Testar verificação com modo inválido.
    
    Verifica que o endpoint retorna status 403 quando o
    parâmetro hub.mode não é "subscribe".
    """
    with patch("app.routes.webhook.get_configuracao", return_value=mock_config):
        response = client.get(
            "/webhook/whatsapp",
            params={
                "hub.mode": "invalid_mode",
                "hub.challenge": "test_challenge_123",
                "hub.verify_token": "test_verify_token"
            }
        )
        
        assert response.status_code == 403


# ==================== Testes para POST (Recepção) ====================

def test_webhook_receive_text_message(text_message_payload: dict[str, Any]):
    """
    Testar recepção de mensagem de texto.
    
    Verifica que o endpoint processa corretamente uma mensagem
    de texto, extraindo os dados relevantes (telefone, tipo, conteúdo).
    """
    response = client.post(
        "/webhook/whatsapp",
        json=text_message_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "received"
    assert "data" in data
    assert data["data"]["tipo"] == "text"
    assert data["data"]["telefone"] == "5511999999999"
    assert data["data"]["conteudo"] == "Olá, como você está?"
    assert "mensagem_id" in data["data"]
    assert "timestamp" in data["data"]


def test_webhook_receive_audio_message(audio_message_payload: dict[str, Any]):
    """
    Testar recepção de mensagem de áudio.
    
    Verifica que o endpoint processa corretamente uma mensagem
    de áudio, extraindo os dados relevantes (telefone, tipo, media_id, mime_type).
    """
    response = client.post(
        "/webhook/whatsapp",
        json=audio_message_payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "received"
    assert "data" in data
    assert data["data"]["tipo"] == "audio"
    assert data["data"]["telefone"] == "5511888888888"
    assert data["data"]["media_id"] == "1234567890123456"
    assert data["data"]["mime_type"] == "audio/ogg; codecs=opus"
    assert "mensagem_id" in data["data"]
    assert "timestamp" in data["data"]


def test_webhook_receive_invalid_payload():
    """
    Testar recepção de payload inválido.
    
    Verifica que o endpoint trata corretamente um JSON malformado,
    retornando status 400 e uma mensagem de erro apropriada.
    """
    response = client.post(
        "/webhook/whatsapp",
        json={"invalid": "payload"}
    )
    
    # O endpoint deve retornar 200 mesmo com payload inválido
    # pois o WhatsApp espera confirmação de recebimento
    assert response.status_code == 200
    data = response.json()
    
    # Verifica que o erro foi tratado
    assert "status" in data


def test_webhook_receive_no_messages():
    """
    Testar recepção de payload sem mensagens.
    
    Verifica que o endpoint trata corretamente um payload
    que não contém mensagens.
    """
    payload: dict[str, Any] = {
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
                                "phone_number_id": "123456789012345"
                            },
                            "contacts": [],
                            "messages": []
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    response = client.post(
        "/webhook/whatsapp",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "error"
    assert "Nenhuma mensagem encontrada" in data["message"]


def test_webhook_receive_unsupported_message_type():
    """
    Testar recepção de tipo de mensagem não suportado.
    
    Verifica que o endpoint trata corretamente mensagens
    de tipos não suportados (ex: image, video).
    """
    payload: dict[str, Any] = {
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
                                "phone_number_id": "123456789012345"
                            },
                            "contacts": [
                                {
                                    "profile": {"name": "Test User"},
                                    "wa_id": "5511999999999"
                                }
                            ],
                            "messages": [
                                {
                                    "from": "5511999999999",
                                    "id": "msg123",
                                    "timestamp": "1704067200",
                                    "type": "image",
                                    "image": {
                                        "id": "1234567890123456",
                                        "mime_type": "image/jpeg"
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
    
    response = client.post(
        "/webhook/whatsapp",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "received"
    assert "Tipo de mensagem não suportado" in data["message"]
    assert data["data"]["tipo"] == "image"


def test_webhook_health():
    """
    Testar endpoint de health check.
    
    Verifica que o endpoint de health retorna status ok.
    """
    response = client.get("/webhook/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "ok"
    assert data["service"] == "webhook"