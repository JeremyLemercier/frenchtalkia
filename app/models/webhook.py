from typing import Any, Dict, List

from pydantic import BaseModel, Field


class WebhookMessage(BaseModel):
    """Modelo base para mensagens recebidas do webhook WhatsApp."""
    
    from_: str = Field(..., alias="from", description="Número de telefone do remetente")
    id: str = Field(..., description="ID da mensagem")
    timestamp: str = Field(..., description="Timestamp da mensagem")
    type: str = Field(..., description="Tipo da mensagem (text, audio, etc.)")
    
    class Config:
        populate_by_name = True


class TextMessage(WebhookMessage):
    """Modelo para mensagens de texto do webhook WhatsApp."""
    
    text: Dict[str, str] = Field(..., description="Conteúdo da mensagem de texto")
    
    @property
    def body(self) -> str:
        """Retorna o corpo da mensagem de texto."""
        return self.text.get("body", "")


class AudioMessage(WebhookMessage):
    """Modelo para mensagens de áudio do webhook WhatsApp."""
    
    audio: Dict[str, str] = Field(..., description="Informações do áudio")
    
    @property
    def audio_id(self) -> str:
        """Retorna o ID do áudio."""
        return self.audio.get("id", "")
    
    @property
    def mime_type(self) -> str:
        """Retorna o MIME type do áudio."""
        return self.audio.get("mime_type", "")
    
    @property
    def sha256(self) -> str:
        """Retorna o hash SHA256 do áudio."""
        return self.audio.get("sha256", "")


class WebhookContact(BaseModel):
    """Modelo para informações de contato do webhook WhatsApp."""
    
    profile: Dict[str, str] = Field(..., description="Informações do perfil")
    wa_id: str = Field(..., description="ID do WhatsApp")
    
    @property
    def name(self) -> str:
        """Retorna o nome do contato."""
        return self.profile.get("name", "")


class WebhookMetadata(BaseModel):
    """Modelo para metadados do webhook WhatsApp."""
    
    display_phone_number: str = Field(..., description="Número de telefone exibido")
    phone_number_id: str = Field(..., description="ID do número de telefone")


class WebhookValue(BaseModel):
    """Modelo para o valor do webhook WhatsApp."""
    
    messaging_product: str = Field(..., description="Produto de mensageria")
    metadata: WebhookMetadata = Field(..., description="Metadados")
    contacts: List[WebhookContact] = Field(default_factory=list, description="Contatos")
    messages: List[Dict[str, Any]] = Field(default_factory=list, description="Mensagens")


class WebhookChange(BaseModel):
    """Modelo para mudanças do webhook WhatsApp."""
    
    value: WebhookValue = Field(..., description="Valor da mudança")
    field: str = Field(..., description="Tipo do campo")


class WebhookEntry(BaseModel):
    """Modelo para entradas do webhook WhatsApp."""
    
    id: str = Field(..., description="ID da entrada")
    changes: List[WebhookChange] = Field(..., description="Lista de mudanças")


class WebhookPayload(BaseModel):
    """Modelo raiz do webhook WhatsApp."""
    
    object: str = Field(..., description="Objeto do webhook")
    entry: List[WebhookEntry] = Field(..., description="Lista de entradas")
    
    def extrair_mensagem(self) -> Dict[str, Any] | None:
        """
        Extrai a primeira mensagem do payload.
        
        Returns:
            Dict[str, Any] | None: Primeira mensagem encontrada ou None
        """
        for entry in self.entry:
            for change in entry.changes:
                if change.value.messages:
                    return change.value.messages[0]
        return None
    
    def extrair_text_message(self) -> TextMessage | None:
        """
        Extrai a primeira mensagem de texto do payload.
        
        Returns:
            TextMessage | None: Primeira mensagem de texto encontrada ou None
        """
        for entry in self.entry:
            for change in entry.changes:
                for message in change.value.messages:
                    if message.get("type") == "text":
                        return TextMessage.model_validate(message)
        return None
    
    def extrair_audio_message(self) -> AudioMessage | None:
        """
        Extrai a primeira mensagem de áudio do payload.
        
        Returns:
            AudioMessage | None: Primeira mensagem de áudio encontrada ou None
        """
        for entry in self.entry:
            for change in entry.changes:
                for message in change.value.messages:
                    if message.get("type") == "audio":
                        return AudioMessage.model_validate(message)
        return None
    
    def extrair_contato(self) -> WebhookContact | None:
        """
        Extrai o primeiro contato do payload.
        
        Returns:
            WebhookContact | None: Primeiro contato encontrado ou None
        """
        for entry in self.entry:
            for change in entry.changes:
                if change.value.contacts:
                    return change.value.contacts[0]
        return None
    
    def extrair_phone_number_id(self) -> str | None:
        """
        Extrai o phone_number_id do payload.
        
        Returns:
            str | None: Phone number ID encontrado ou None
        """
        for entry in self.entry:
            for change in entry.changes:
                return change.value.metadata.phone_number_id
        return None
