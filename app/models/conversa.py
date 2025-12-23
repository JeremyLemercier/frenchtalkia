from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class Conversa(BaseModel):
    """Modelo de dados para conversa do usuário."""

    id_conversa: str = Field(
        default_factory=lambda: str(uuid4()), description="ID único da conversa"
    )
    id_usuario: str = Field(..., description="ID do usuário (número de telefone)")
    conversation_id_mistral: str = Field(..., description="ID da conversa na API Mistral")
    tema: str = Field(..., description="Tema da conversa")
    topico: str = Field(..., description="Tópico da conversa")
    data_inicio: datetime = Field(default_factory=datetime.now, description="Data e hora de início")
    data_fim: datetime | None = Field(None, description="Data e hora de término")
    feedback_evaluation: int | None = Field(
        None, description="Avaliação do feedback (1=bom, 0=problema)"
    )
    feedback_comment: str | None = Field(None, description="Comentário do feedback")

    model_config = ConfigDict()

    @field_serializer("data_inicio")
    def serialize_data_inicio(self, value: datetime) -> str:
        """Serializa datetime para string ISO format."""
        return value.isoformat()

    @field_serializer("data_fim")
    def serialize_data_fim(self, value: datetime | None) -> str | None:
        """Serializa datetime opcional para string ISO format."""
        return value.isoformat() if value else None

    def to_dict(self) -> dict[str, Any]:
        """Converte o modelo para dicionário, tratando tipos especiais."""
        data = self.model_dump()
        data["data_inicio"] = self.data_inicio.isoformat()
        if self.data_fim:
            data["data_fim"] = self.data_fim.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conversa":
        """Cria instância a partir de dicionário, tratando tipos especiais."""
        if "data_inicio" in data and isinstance(data["data_inicio"], str):
            data["data_inicio"] = datetime.fromisoformat(data["data_inicio"])
        if (
            "data_fim" in data
            and data["data_fim"] is not None
            and isinstance(data["data_fim"], str)
        ):
            data["data_fim"] = datetime.fromisoformat(data["data_fim"])
        return cls(**data)

    def finalizar_conversa(self) -> None:
        """Finaliza a conversa registrando a data de término."""
        self.data_fim = datetime.now()

    def solicitar_avaliacao(self) -> str:
        """
        Retorna mensagem de texto pedindo ao usuário para avaliar a conversa.

        Returns:
            str: Mensagem solicitando avaliação
        """
        return "Como foi a conversa? Digite 1 para bom ou 0 se teve algo errado."

    def registrar_feedback(self, evaluation: int, comment: str | None = None) -> None:
        """
        Registra o feedback do usuário sobre a conversa.

        Args:
            evaluation: Avaliação (1=bom, 0=problema)
            comment: Comentário opcional descrevendo o problema
        """
        self.feedback_evaluation = evaluation
        self.feedback_comment = comment
