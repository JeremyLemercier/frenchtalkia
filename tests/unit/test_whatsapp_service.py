from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.config import ConfiguracaoApp
from app.services.whatsapp_service import WhatsAppService


# ==================== Testes para Obter URL da Mídia ====================


@pytest.mark.asyncio
async def test_obter_url_media_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar obtenção bem-sucedida de URL da mídia.
    
    Verifica que o método retorna a URL temporária corretamente
    quando a API responde com sucesso.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    expected_url = "https://tmp-media.whatsapp.net/xyz123"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"url": expected_url}
    mock_httpx_client.get.return_value = mock_response
    
    # Execute
    result = await service.obter_url_media(media_id)
    
    # Verify
    assert result == expected_url
    
    # Verificar chamada correta
    mock_httpx_client.get.assert_called_once_with(
        f"https://graph.facebook.com/v24.0/{media_id}",
        params={"phone_number_id": mock_config.whatsapp_phone_number_id},
        headers={"Authorization": f"Bearer {mock_config.whatsapp_token}"}
    )


@pytest.mark.asyncio
async def test_obter_url_media_not_found(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar mídia não encontrada.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 404 (mídia não encontrada).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "nonexistent_media_id"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_httpx_client.get.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match=f"Mídia não encontrada: {media_id}"):
        await service.obter_url_media(media_id)
    
    # Verificar chamada correta
    mock_httpx_client.get.assert_called_once_with(
        f"https://graph.facebook.com/v24.0/{media_id}",
        params={"phone_number_id": mock_config.whatsapp_phone_number_id},
        headers={"Authorization": f"Bearer {mock_config.whatsapp_token}"}
    )


@pytest.mark.asyncio
async def test_obter_url_media_invalid_token(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar token inválido.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 401 (token inválido).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_httpx_client.get.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="Token de acesso inválido"):
        await service.obter_url_media(media_id)


@pytest.mark.asyncio
async def test_obter_url_media_missing_url_in_response(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar resposta sem URL.
    
    Verifica que o método levanta ValueError quando a API
    responde com sucesso mas não inclui a URL no JSON.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    
    # Mock response sem URL
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_field": "value"}
    mock_httpx_client.get.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="URL não encontrada na resposta"):
        await service.obter_url_media(media_id)


# ==================== Testes para Download de Áudio ====================


@pytest.mark.asyncio
async def test_baixar_audio_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar download bem-sucedido de áudio.
    
    Verifica que o método baixa o arquivo corretamente,
    salva no diretório temporário e retorna o caminho.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    media_url = "https://tmp-media.whatsapp.net/xyz123"
    audio_content = b"fake_audio_content_ogg_bytes"
    
    # Mock obter_url_media como AsyncMock
    mock_obter_url = AsyncMock(return_value=media_url)
    
    with patch.object(service, 'obter_url_media', mock_obter_url):
        # Mock download response
        mock_download_response = MagicMock()
        mock_download_response.status_code = 200
        mock_download_response.content = audio_content
        mock_httpx_client.get.return_value = mock_download_response
        
        # Execute
        result = await service.baixar_audio(media_id)
    
    # Verify
    assert result.is_file()
    assert result.suffix == ".ogg"
    assert media_id in result.name
    assert result.read_bytes() == audio_content
    
    # Verificar chamadas
    mock_obter_url.assert_called_once_with(media_id)
    mock_httpx_client.get.assert_called_once_with(
        media_url,
        headers={"Authorization": f"Bearer {mock_config.whatsapp_token}"}
    )


@pytest.mark.asyncio
async def test_baixar_audio_url_expired(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar URL expirada durante download.
    
    Verifica que o método levanta ValueError quando a URL
    temporária expirou (status 401 no download).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    media_url = "https://tmp-media.whatsapp.net/xyz123"
    
    # Mock obter_url_media como AsyncMock
    mock_obter_url = AsyncMock(return_value=media_url)
    
    with patch.object(service, 'obter_url_media', mock_obter_url):
        # Mock download response com erro 401
        mock_download_response = MagicMock()
        mock_download_response.status_code = 401
        mock_httpx_client.get.return_value = mock_download_response
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Erro ao baixar áudio: 401"):
            await service.baixar_audio(media_id)


@pytest.mark.asyncio
async def test_baixar_audio_download_error(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar erro de download genérico.
    
    Verifica que o método levanta ValueError quando ocorre
    um erro genérico no download (status diferente de 200).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    media_id = "test_media_id_123"
    media_url = "https://tmp-media.whatsapp.net/xyz123"
    
    # Mock obter_url_media como AsyncMock
    mock_obter_url = AsyncMock(return_value=media_url)
    
    with patch.object(service, 'obter_url_media', mock_obter_url):
        # Mock download response com erro 500
        mock_download_response = MagicMock()
        mock_download_response.status_code = 500
        mock_httpx_client.get.return_value = mock_download_response
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Erro ao baixar áudio: 500"):
            await service.baixar_audio(media_id)


# ==================== Testes para Upload de Áudio ====================


@pytest.mark.asyncio
async def test_fazer_upload_audio_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar upload bem-sucedido de áudio.
    
    Verifica que o método faz o upload corretamente,
    enviando o arquivo binário e retornando o media_id.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    expected_media_id = "uploaded_media_id_456"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": expected_media_id}
    mock_httpx_client.post.return_value = mock_response
    
    # Execute
    result = await service.fazer_upload_audio(sample_audio_file)
    
    # Verify
    assert result == expected_media_id
    
    # Verificar chamada correta
    expected_url = f"https://graph.facebook.com/v24.0/{mock_config.whatsapp_phone_number_id}/media"
    expected_headers = {"Authorization": f"Bearer {mock_config.whatsapp_token}"}
    
    # Verificar que foi chamado com os parâmetros corretos
    assert mock_httpx_client.post.call_count == 1
    call_args = mock_httpx_client.post.call_args
    
    # Verificar URL e headers
    assert call_args.args[0] == expected_url
    assert call_args.kwargs["headers"] == expected_headers
    
    # Verificar estrutura do multipart
    assert "files" in call_args.kwargs
    files = call_args.kwargs["files"]
    assert isinstance(files, dict)
    assert "file" in files
    assert "type" in files
    assert "messaging_product" in files


@pytest.mark.asyncio
async def test_fazer_upload_audio_file_too_large(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar arquivo muito grande.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 413 (arquivo grande demais).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 413
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="Arquivo de áudio muito grande"):
        await service.fazer_upload_audio(sample_audio_file)


@pytest.mark.asyncio
async def test_fazer_upload_audio_invalid_format(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar formato de áudio inválido.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 400 (formato inválido).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="Formato de áudio inválido"):
        await service.fazer_upload_audio(sample_audio_file)


@pytest.mark.asyncio
async def test_fazer_upload_audio_missing_media_id(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar resposta sem media_id.
    
    Verifica que o método levanta ValueError quando a API
    responde com sucesso mas não inclui o media_id.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    # Mock response sem media_id
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"other_field": "value"}
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="ID do mídia não encontrado na resposta"):
        await service.fazer_upload_audio(sample_audio_file)


# ==================== Testes para Envio de Mensagens ====================


@pytest.mark.asyncio
async def test_enviar_mensagem_texto_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar envio bem-sucedido de mensagem de texto.
    
    Verifica que o método envia o payload correto e
    retorna o message_id da API.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    telefone = "5511999999999"
    texto = "Olá, esta é uma mensagem de teste"
    expected_message_id = "wamid.test.message.123"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{"id": expected_message_id}]}
    mock_httpx_client.post.return_value = mock_response
    
    # Execute
    result = await service.enviar_mensagem_texto(telefone, texto)
    
    # Verify
    assert result == expected_message_id
    
    # Verificar payload correto
    expected_url = f"https://graph.facebook.com/v24.0/{mock_config.whatsapp_phone_number_id}/messages"
    expected_headers = {
        "Authorization": f"Bearer {mock_config.whatsapp_token}",
        "Content-Type": "application/json",
    }
    expected_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefone,
        "type": "text",
        "text": {"preview_url": False, "body": texto},
    }
    
    mock_httpx_client.post.assert_called_once_with(
        expected_url,
        headers=expected_headers,
        json=expected_payload
    )


@pytest.mark.asyncio
async def test_enviar_mensagem_texto_invalid_phone(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar telefone inválido.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 400 (telefone inválido).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    telefone = "invalid_phone"
    texto = "Test message"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="Número de telefone inválido"):
        await service.enviar_mensagem_texto(telefone, texto)


@pytest.mark.asyncio
async def test_enviar_mensagem_texto_rate_limit(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar rate limit excedido.
    
    Verifica que o método levanta ValueError quando a API
    retorna status 429 (rate limit).
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    telefone = "5511999999999"
    texto = "Test message"
    
    # Mock response
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="Rate limit excedido"):
        await service.enviar_mensagem_texto(telefone, texto)


@pytest.mark.asyncio
async def test_enviar_mensagem_texto_missing_message_id(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar resposta sem message_id.
    
    Verifica que o método levanta ValueError quando a API
    responde com sucesso mas não inclui o message_id.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    telefone = "5511999999999"
    texto = "Test message"
    
    # Mock response sem message_id
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"messages": [{}]}
    mock_httpx_client.post.return_value = mock_response
    
    # Execute & Verify
    with pytest.raises(ValueError, match="ID da mensagem não encontrado na resposta"):
        await service.enviar_mensagem_texto(telefone, texto)


@pytest.mark.asyncio
async def test_enviar_mensagem_audio_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock, sample_audio_file: Path):
    """
    Testar envio bem-sucedido de mensagem de áudio.
    
    Verifica que o método faz o upload do áudio primeiro
    e depois envia a mensagem com o media_id.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    telefone = "5511999999999"
    expected_media_id = "uploaded_media_id_456"
    expected_message_id = "wamid.test.audio.123"
    
    # Mock upload como AsyncMock
    mock_upload = AsyncMock(return_value=expected_media_id)
    
    with patch.object(service, 'fazer_upload_audio', mock_upload):
        # Mock envio response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": expected_message_id}]}
        mock_httpx_client.post.return_value = mock_response
        
        # Execute
        result = await service.enviar_mensagem_audio(telefone, sample_audio_file)
    
    # Verify
    assert result == expected_message_id
    
    # Verificar sequência correta
    mock_upload.assert_called_once_with(sample_audio_file)
    
    # Verificar payload correto
    expected_url = f"https://graph.facebook.com/v24.0/{mock_config.whatsapp_phone_number_id}/messages"
    expected_headers = {
        "Authorization": f"Bearer {mock_config.whatsapp_token}",
        "Content-Type": "application/json",
    }
    expected_payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": telefone,
        "type": "audio",
        "audio": {"id": expected_media_id, "voice": True},
    }
    
    mock_httpx_client.post.assert_called_once_with(
        expected_url,
        headers=expected_headers,
        json=expected_payload
    )


@pytest.mark.asyncio
async def test_enviar_mensagem_audio_upload_error(mock_config: ConfiguracaoApp, sample_audio_file: Path):
    """
    Testar erro no upload durante envio de áudio.
    
    Verifica que o método propaga o erro quando o
    upload do áudio falha.
    """
    # Setup
    service = WhatsAppService(mock_config)
    
    telefone = "5511999999999"
    
    # Mock upload com erro como AsyncMock
    mock_upload = AsyncMock(side_effect=ValueError("Upload failed"))
    
    with patch.object(service, 'fazer_upload_audio', mock_upload):
        # Execute & Verify
        with pytest.raises(ValueError, match="Upload failed"):
            await service.enviar_mensagem_audio(telefone, sample_audio_file)


@pytest.mark.asyncio
async def test_close_success(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar fechamento bem-sucedido do cliente HTTP.
    
    Verifica que o método fecha o cliente corretamente.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    
    # Execute
    await service.close()
    
    # Verify
    mock_httpx_client.aclose.assert_called_once()


@pytest.mark.asyncio
async def test_close_error(mock_config: ConfiguracaoApp, mock_httpx_client: AsyncMock):
    """
    Testar erro ao fechar cliente HTTP.
    
    Verifica que o método propaga o erro quando ocorre
    erro no fechamento do cliente.
    """
    # Setup
    service = WhatsAppService(mock_config)
    service.httpx_client = mock_httpx_client
    mock_httpx_client.aclose.side_effect = Exception("Close error")
    
    # Execute & Verify
    with pytest.raises(Exception, match="Close error"):
        await service.close()


# ==================== Testes para Métodos Legados ====================


def test_verificar_webhook_valid_token(mock_config: ConfiguracaoApp):
    """
    Testar verificação de webhook com token válido.
    
    Verifica que o método retorna True quando o token
    corresponde ao configurado.
    """
    # Setup
    service = WhatsAppService(mock_config)
    
    # Execute
    result = service.verificar_webhook(mock_config.whatsapp_verify_token)
    
    # Verify
    assert result is True


def test_verificar_webhook_invalid_token(mock_config: ConfiguracaoApp):
    """
    Testar verificação de webhook com token inválido.
    
    Verifica que o método retorna False quando o token
    não corresponde ao configurado.
    """
    # Setup
    service = WhatsAppService(mock_config)
    
    # Execute
    result = service.verificar_webhook("invalid_token")
    
    # Verify
    assert result is False


def test_processar_webhook_legacy(mock_config: ConfiguracaoApp):
    """
    Testar processamento de webhook legado.
    
    Verifica que o método legado simplesmente retorna
    o payload recebido sem modificações.
    """
    # Setup
    service = WhatsAppService(mock_config)
    
    payload = {"test": "payload"}
    
    # Execute
    result = service.processar_webhook(payload)
    
    # Verify
    assert result == payload