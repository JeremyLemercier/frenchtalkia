from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_serializer
from pydantic.config import ConfigDict


class EstadoSessao(str, Enum):
    """Estados possíveis da sessão do usuário."""

    AGUARDANDO_NOME = "AGUARDANDO_NOME"
    MENU_PRINCIPAL = "MENU_PRINCIPAL"
    MENU_TEMAS = "MENU_TEMAS"
    MENU_TOPICOS = "MENU_TOPICOS"
    EM_CONVERSA = "EM_CONVERSA"


class Sessao(BaseModel):
    """Modelo de dados para sessão do usuário."""

    id_usuario: str = Field(..., description="ID do usuário (número de telefone)")
    estado_atual: EstadoSessao = Field(..., description="Estado atual da sessão")
    tema_selecionado: str | None = Field(None, description="Tema selecionado pelo usuário")
    topico_selecionado: str | None = Field(None, description="Tópico selecionado pelo usuário")
    agent_id_mistral: str | None = Field(None, description="ID do agente Mistral")
    conversation_id_mistral: str | None = Field(None, description="ID da conversa Mistral")
    ultima_interacao: datetime = Field(
        default_factory=datetime.now, description="Data e hora da última interação"
    )

    model_config = ConfigDict(
        use_enum_values=True,
    )

    @field_serializer("ultima_interacao")
    def _serialize_ultima_interacao(self, v: datetime, _info):
        return v.isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Converte o modelo para dicionário, tratando tipos especiais."""
        data = self.model_dump()
        data["estado_atual"] = self.estado_atual.value
        data["ultima_interacao"] = self.ultima_interacao.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Sessao:
        """Cria instância a partir de dicionário, tratando tipos especiais."""
        if "estado_atual" in data and isinstance(data["estado_atual"], str):
            data["estado_atual"] = EstadoSessao(data["estado_atual"])
        if "ultima_interacao" in data and isinstance(data["ultima_interacao"], str):
            data["ultima_interacao"] = datetime.fromisoformat(data["ultima_interacao"])
        return cls(**data)

    def atualizar_estado(self, novo_estado: EstadoSessao) -> None:
        """Atualiza o estado da sessão e registra a interação."""
        self.estado_atual = novo_estado
        self.ultima_interacao = datetime.now()

    def limpar_selecoes(self) -> None:
        """Limpa as seleções de tema e tópico."""
        self.tema_selecionado = None
        self.topico_selecionado = None
        self.agent_id_mistral = None
        self.conversation_id_mistral = None