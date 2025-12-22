import logging
import time
from pathlib import Path
from typing import Any, Dict

import httpx

from app.config import ConfiguracaoApp


class WhatsAppService:
    """Serviço para integração com WhatsApp Cloud API."""
    
    def __init__(self, config: ConfiguracaoApp) -> None:
        """
        Inicializa o serviço do WhatsApp.
        
        Args:
            config: Configuração da aplicação com tokens e IDs
        """
        self.config = config
        self.access_token = config.whatsapp_token
        self.phone_number_id = config.whatsapp_phone_number_id
        self.base_url = "https://graph.facebook.com/v24.0"
        self.httpx_client = httpx.AsyncClient(timeout=30.0)
        self.logger = logging.getLogger(__name__)
        
        self.logger.debug(f"WhatsAppService inicializado com phone_number_id: {self.phone_number_id}")
    
    async def obter_url_media(self, media_id: str) -> str:
        """
        Obtém URL temporária para acessar mídia.
        
        Args:
            media_id: ID do mídia no WhatsApp
            
        Returns:
            str: URL temporária da mídia (válida por 5 minutos)
            
        Raises:
            ValueError: Se o token for inválido ou mídia não encontrada
        """
        try:
            url = f"{self.base_url}/{media_id}"
            params = {"phone_number_id": self.phone_number_id}
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            self.logger.debug(f"Obtendo URL para media_id: {media_id}")
            
            response = await self.httpx_client.get(url, params=params, headers=headers)
            
            if response.status_code == 401:
                self.logger.error("Token de acesso inválido")
                raise ValueError("Token de acesso inválido")
            elif response.status_code == 404:
                self.logger.error(f"Mídia não encontrada: {media_id}")
                raise ValueError(f"Mídia não encontrada: {media_id}")
            elif response.status_code != 200:
                self.logger.error(f"Erro ao obter URL da mídia: {response.status_code} - {response.text}")
                raise ValueError(f"Erro ao obter URL da mídia: {response.status_code}")
            
            data = response.json()
            media_url = data.get("url")
            
            if not media_url:
                self.logger.error("URL não encontrada na resposta")
                raise ValueError("URL não encontrada na resposta")
            
            self.logger.debug(f"URL obtida com sucesso: {media_url}")
            return media_url
            
        except httpx.RequestError as e:
            self.logger.error(f"Erro de requisição ao obter URL da mídia: {str(e)}")
            raise ValueError(f"Erro de requisição: {str(e)}")
    
    async def baixar_audio(self, media_id: str) -> Path:
        """
        Baixa arquivo de áudio do WhatsApp.
        
        Args:
            media_id: ID do mídia no WhatsApp
            
        Returns:
            Path: Caminho do arquivo baixado
            
        Raises:
            ValueError: Se ocorrer erro no download ou salvamento
        """
        try:
            # Obter URL temporária
            media_url = await self.obter_url_media(media_id)
            
            # Criar diretório temporário se não existir
            temp_dir = self.config.diretorio_temp_audio
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome do arquivo
            timestamp = int(time.time())
            filename = f"audio_{media_id}_{timestamp}.ogg"
            filepath = temp_dir / filename
            
            self.logger.debug(f"Baixando áudio {media_id} para {filepath}")
            
            # Fazer download do arquivo
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self.httpx_client.get(media_url, headers=headers)
            
            if response.status_code != 200:
                self.logger.error(f"Erro ao baixar áudio: {response.status_code} - {response.text}")
                raise ValueError(f"Erro ao baixar áudio: {response.status_code}")
            
            # Salvar arquivo
            filepath.write_bytes(response.content)
            
            self.logger.info(f"Áudio baixado com sucesso: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Erro ao baixar áudio {media_id}: {str(e)}")
            raise ValueError(f"Erro ao baixar áudio: {str(e)}")
    
    async def fazer_upload_audio(self, caminho_audio: Path) -> str:
        """
        Faz upload de arquivo de áudio para WhatsApp.
        
        Args:
            caminho_audio: Caminho do arquivo de áudio
            
        Returns:
            str: ID do mídia uploaded
            
        Raises:
            ValueError: Se ocorrer erro no upload
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/media"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            self.logger.debug(f"Fazendo upload do áudio: {caminho_audio}")
            
            # Ler arquivo binário
            with open(caminho_audio, "rb") as audio_file:
                files: Dict[str, Any] = {
                    "file": (caminho_audio.name, audio_file, "audio/ogg; codecs=opus"),
                    "type": (None, "audio/ogg; codecs=opus"),
                    "messaging_product": (None, "whatsapp")
                }
                
                response = await self.httpx_client.post(url, headers=headers, files=files)
            
            if response.status_code == 400:
                self.logger.error(f"Formato de áudio inválido: {response.text}")
                raise ValueError("Formato de áudio inválido")
            elif response.status_code == 413:
                self.logger.error("Arquivo de áudio muito grande")
                raise ValueError("Arquivo de áudio muito grande")
            elif response.status_code != 200:
                self.logger.error(f"Erro no upload: {response.status_code} - {response.text}")
                raise ValueError(f"Erro no upload: {response.status_code}")
            
            data = response.json()
            media_id = data.get("id")
            
            if not media_id:
                self.logger.error("ID do mídia não encontrado na resposta")
                raise ValueError("ID do mídia não encontrado na resposta")
            
            self.logger.info(f"Upload realizado com sucesso. Media ID: {media_id}")
            return media_id
            
        except httpx.RequestError as e:
            self.logger.error(f"Erro de requisição no upload: {str(e)}")
            raise ValueError(f"Erro de requisição: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erro no upload do áudio: {str(e)}")
            raise ValueError(f"Erro no upload: {str(e)}")
    
    async def enviar_mensagem_texto(self, telefone: str, texto: str) -> str:
        """
        Envia mensagem de texto via WhatsApp.
        
        Args:
            telefone: Número de telefone do destinatário
            texto: Conteúdo da mensagem
            
        Returns:
            str: ID da mensagem enviada
            
        Raises:
            ValueError: Se ocorrer erro no envio
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload: Dict[str, Any] = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": telefone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": texto
                }
            }
            
            self.logger.debug(f"Enviando mensagem de texto para {telefone}: {texto[:50]}...")
            
            response = await self.httpx_client.post(url, headers=headers, json=payload)
            
            if response.status_code == 400:
                self.logger.error(f"Número de telefone inválido: {response.text}")
                raise ValueError("Número de telefone inválido")
            elif response.status_code == 429:
                self.logger.error("Rate limit excedido")
                raise ValueError("Rate limit excedido")
            elif response.status_code != 200:
                self.logger.error(f"Erro no envio: {response.status_code} - {response.text}")
                raise ValueError(f"Erro no envio: {response.status_code}")
            
            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id")
            
            if not message_id:
                self.logger.error("ID da mensagem não encontrado na resposta")
                raise ValueError("ID da mensagem não encontrado na resposta")
            
            self.logger.info(f"Mensagem de texto enviada com sucesso. ID: {message_id}")
            return message_id
            
        except httpx.RequestError as e:
            self.logger.error(f"Erro de requisição no envio: {str(e)}")
            raise ValueError(f"Erro de requisição: {str(e)}")
        except Exception as e:
            self.logger.error(f"Erro no envio da mensagem: {str(e)}")
            raise ValueError(f"Erro no envio: {str(e)}")
    
    async def enviar_mensagem_audio(self, telefone: str, caminho_audio: Path) -> str:
        """
        Envia mensagem de áudio via WhatsApp.
        
        Args:
            telefone: Número de telefone do destinatário
            caminho_audio: Caminho do arquivo de áudio
            
        Returns:
            str: ID da mensagem enviada
            
        Raises:
            ValueError: Se ocorrer erro no envio
        """
        try:
            # Fazer upload do áudio
            media_id = await self.fazer_upload_audio(caminho_audio)
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            payload: Dict[str, Any] = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": telefone,
                "type": "audio",
                "audio": {
                    "id": media_id,
                    "voice": True
                }
            }
            
            self.logger.debug(f"Enviando mensagem de áudio para {telefone} (media_id: {media_id})")
            
            response = await self.httpx_client.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                self.logger.error(f"Erro no envio do áudio: {response.status_code} - {response.text}")
                raise ValueError(f"Erro no envio do áudio: {response.status_code}")
            
            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id")
            
            if not message_id:
                self.logger.error("ID da mensagem não encontrado na resposta")
                raise ValueError("ID da mensagem não encontrado na resposta")
            
            self.logger.info(f"Mensagem de áudio enviada com sucesso. ID: {message_id}")
            return message_id
            
        except Exception as e:
            self.logger.error(f"Erro no envio da mensagem de áudio: {str(e)}")
            raise ValueError(f"Erro no envio da mensagem de áudio: {str(e)}")
    
    async def close(self) -> None:
        """
        Fecha o cliente HTTP.
        
        Deve ser chamado quando o serviço não for mais utilizado.
        """
        try:
            await self.httpx_client.aclose()
            self.logger.debug("Cliente HTTP fechado com sucesso")
        except Exception as e:
            self.logger.error(f"Erro ao fechar cliente HTTP: {str(e)}")
    
    # Métodos legados mantidos para compatibilidade
    def verificar_webhook(self, verify_token: str) -> bool:
        """
        Verifica token do webhook do WhatsApp.
        
        Args:
            verify_token: Token recebido na verificação
            
        Returns:
            bool: True se token é válido
        """
        return verify_token == self.config.whatsapp_verify_token
    
    def processar_webhook(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Processa payload recebido do webhook.
        
        Args:
            payload: Payload JSON do webhook
            
        Returns:
            dict: Dados processados da mensagem
        """
        # Este método será substituído pela lógica nos endpoints
        return payload