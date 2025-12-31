import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import random
import asyncio

import aiofiles
import httpx

from app.config import ConfiguracaoApp
from app.utils.logger import logger


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

        logger.debug(f"WhatsAppService inicializado com phone_number_id: {self.phone_number_id}")

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

            logger.debug(f"Obtendo URL para media_id: {media_id}")

            response = await self._request_with_retry("get", url, headers=headers, params=params)

            if response.status_code == 401:
                msg_erro = "Token de acesso inválido"
                logger.error(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code == 404:
                msg_erro = f"Mídia não encontrada: {media_id}"
                logger.error(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code != 200:
                msg_erro = f"Erro ao obter URL da mídia: {response.status_code}"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            data = response.json()
            media_url = data.get("url")

            if not media_url:
                msg_erro = "URL não encontrada na resposta"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            logger.debug(f"URL obtida com sucesso: {media_url}")
            return media_url

        except httpx.RequestError as e:
            msg_erro = f"Erro de requisição ao obter URL da mídia: {str(e)}"
            logger.error(msg_erro)
            raise ValueError(msg_erro)

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
            media_url = await self.obter_url_media(media_id)

            # Criar diretório temporário se não existir
            temp_dir = self.config.diretorio_temp_audio
            temp_dir.mkdir(parents=True, exist_ok=True)

            # Gerar nome do arquivo (WhatsApp audio messages are expected to be .ogg)
            timestamp = int(time.time())
            filename = f"audio_{media_id}_{timestamp}.ogg"
            filepath = temp_dir / filename

            logger.debug(f"Baixando áudio {media_id} para {filepath}")

            # Fazer download do arquivo com retry
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = await self._request_with_retry("get", media_url, headers=headers)

            # Salvar arquivo de forma não-bloqueante
            async with aiofiles.open(filepath, "wb") as f:
                await f.write(response.content)

            logger.info(f"Áudio baixado com sucesso: {filepath}")
            return filepath

        except Exception as e:
            logger.exception(f"Erro ao baixar áudio {media_id}: {str(e)}")
            raise

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

            logger.debug(f"Fazendo upload do áudio: {caminho_audio}")

            # Ler arquivo binário de forma não-bloqueante
            async with aiofiles.open(caminho_audio, "rb") as f:
                audio_bytes = await f.read()

            files: Dict[str, Any] = {
                "file": (caminho_audio.name, audio_bytes, "audio/ogg; codecs=opus"),
                "type": (None, "audio/ogg; codecs=opus"),
                "messaging_product": (None, "whatsapp"),
            }

            response = await self._request_with_retry("post", url, headers=headers, files=files)

            if response.status_code == 400:
                msg_erro = "Formato de áudio inválido"
                logger.error(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code == 413:
                msg_erro = "Arquivo de áudio muito grande"
                logger.error(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code != 200:
                msg_erro = f"Erro no upload: {response.status_code}"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            data = response.json()
            media_id = data.get("id")

            if not media_id:
                msg_erro = "ID do mídia não encontrado na resposta"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            logger.info(f"Upload realizado com sucesso. Media ID: {media_id}")
            return media_id

        except httpx.RequestError as e:
            msg_erro = f"Erro de requisição no upload: {str(e)}"
            logger.error(msg_erro)
            raise ValueError(msg_erro)
        except Exception as e:
            logger.exception(f"Erro no upload do áudio: {str(e)}")
            raise

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
                "Content-Type": "application/json",
            }

            payload: Dict[str, Any] = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": telefone,
                "type": "text",
                "text": {"preview_url": False, "body": texto},
            }

            logger.debug(f"Enviando mensagem de texto para {telefone}: {texto[:50]}...")

            response = await self._request_with_retry("post", url, headers=headers, json=payload)

            if response.status_code == 400:
                msg_erro = "Número de telefone inválido"
                logger.error(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code == 429:
                msg_erro = "Rate limit excedido"
                logger.warning(msg_erro)
                raise ValueError(msg_erro)
            elif response.status_code != 200:
                msg_erro = f"Erro no envio: {response.status_code}"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id")

            if not message_id:
                msg_erro = "ID da mensagem não encontrado na resposta"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            logger.info(f"Mensagem de texto enviada com sucesso. ID: {message_id}")
            return message_id

        except httpx.RequestError as e:
            msg_erro = f"Erro de requisição no envio: {str(e)}"
            logger.error(msg_erro)
            raise ValueError(msg_erro)
        except Exception as e:
            logger.exception(f"Erro no envio da mensagem: {str(e)}")
            raise

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
                "Content-Type": "application/json",
            }

            payload: Dict[str, Any] = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": telefone,
                "type": "audio",
                "audio": {"id": media_id, "voice": True},
            }

            logger.debug(f"Enviando mensagem de áudio para {telefone} (media_id: {media_id})")

            response = await self._request_with_retry("post", url, headers=headers, json=payload)

            if response.status_code != 200:
                msg_erro = f"Erro no envio do áudio: {response.status_code}"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            data = response.json()
            message_id = data.get("messages", [{}])[0].get("id")

            if not message_id:
                msg_erro = "ID da mensagem não encontrado na resposta"
                logger.error(msg_erro)
                raise ValueError(msg_erro)

            logger.info(f"Mensagem de áudio enviada com sucesso. ID: {message_id}")
            return message_id

        except Exception as e:
            logger.exception(f"Erro no envio da mensagem de áudio: {str(e)}")
            raise

    def salvar_resultado_integracao(
        self,
        tipo_mensagem: str,
        dados_extraidos: Dict[str, Any],
        arquivo_audio: Optional[Path] = None,
    ) -> Optional[Path]:
        """
        Salva resultado de integração para análise manual.

        Args:
            tipo_mensagem: Tipo da mensagem (text/audio)
            dados_extraidos: Dados extraídos do webhook
            arquivo_audio: Caminho do arquivo de áudio (opcional)

        Returns:
            Optional[Path]: Caminho do diretório de resultados ou None se modo desativado
        """
        if not self.config.integration_test_mode:
            return None

        try:
            # Criar diretório base de resultados
            results_dir = Path("tests/integration/results")
            results_dir.mkdir(parents=True, exist_ok=True)

            # Criar subdiretório com timestamp
            timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            result_subdir = results_dir / timestamp_str
            result_subdir.mkdir(parents=True, exist_ok=True)

            # Salvar dados extraídos
            extracted_data_path = result_subdir / "extracted_data.json"
            with open(extracted_data_path, "w", encoding="utf-8") as f:
                json.dump(dados_extraidos, f, indent=2, ensure_ascii=False)

            # Preparar metadata
            metadata: Dict[str, Any] = {
                "timestamp_recebimento": datetime.now().isoformat(),
                "tipo_mensagem": tipo_mensagem,
                "telefone": dados_extraidos.get("telefone"),
            }

            # Se áudio: copiar arquivo e calcular hash
            if arquivo_audio and arquivo_audio.exists():
                audio_dest = result_subdir / "audio_received.ogg"
                shutil.copy2(arquivo_audio, audio_dest)

                # Calcular hash SHA256
                with open(audio_dest, "rb") as f:
                    audio_bytes = f.read()
                    sha256_hash = hashlib.sha256(audio_bytes).hexdigest()

                # Adicionar informações do áudio ao metadata
                metadata.update({
                    "tamanho_bytes": len(audio_bytes),
                    "sha256": sha256_hash,
                    "mime_type": dados_extraidos.get("mime_type", "audio/ogg; codecs=opus"),
                })

            # Salvar metadata
            metadata_path = result_subdir / "metadata.json"
            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.info(f"Resultado de integração salvo em {result_subdir}")
            return result_subdir

        except Exception as e:
            logger.exception(f"Erro ao salvar resultado de integração: {str(e)}")
            return None

    async def close(self) -> None:
        """
        Fecha o cliente HTTP.

        Deve ser chamado quando o serviço não for mais utilizado.
        """
        try:
            await self.httpx_client.aclose()
            logger.debug("Cliente HTTP fechado com sucesso")
        except Exception as e:
            logger.exception(f"Erro ao fechar cliente HTTP: {str(e)}")
            raise

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        files: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> httpx.Response:
        """
        Faz requests com retry exponencial simples para lidar com 429/5xx.
        """
        backoff_base = 1.0
        for attempt in range(1, max_retries + 1):
            try:
                if method.lower() == "get":
                    resp = await self.httpx_client.get(url, headers=headers, params=params)
                elif method.lower() == "post":
                    resp = await self.httpx_client.post(url, headers=headers, params=params, json=json, files=files)
                else:
                    resp = await self.httpx_client.request(method, url, headers=headers, params=params, json=json, files=files)

                # Retry on rate limit or server errors
                if resp.status_code == 429 or resp.status_code >= 500:
                    if attempt == max_retries:
                        return resp
                    sleep_time = backoff_base * (2 ** (attempt - 1))
                    # add jitter
                    sleep_time = sleep_time + random.uniform(0, 0.1 * sleep_time)
                    logger.warning(f"Request to {url} returned {resp.status_code}, retrying in {sleep_time:.2f}s (attempt {attempt})")
                    await asyncio.sleep(sleep_time)
                    continue

                return resp

            except httpx.RequestError as e:
                if attempt == max_retries:
                    logger.exception(f"Request error to {url}: {str(e)}")
                    raise
                sleep_time = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.1)
                logger.warning(f"Request error to {url}: {str(e)} - retrying in {sleep_time:.2f}s (attempt {attempt})")
                await asyncio.sleep(sleep_time)
                continue

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
