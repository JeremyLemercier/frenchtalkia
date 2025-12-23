from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class Usuario(BaseModel):
    """Modelo de dados para usuário do sistema."""
    
    id_usuario: str = Field(..., description="Número de telefone WhatsApp")
    nome: str | None = Field(None, description="Nome do usuário")
    data_cadastro: datetime = Field(default_factory=datetime.now, description="Data de cadastro")
    cota_diaria_usada: int = Field(default=0, description="Segundos de áudio usados no dia")
    ultima_atualizacao_cota: date = Field(default_factory=date.today, description="Última data de atualização da cota")
    is_processing: bool = Field(default=False, description="Flag de concorrência para processamento")
    
    def resetar_cota_se_necessario(self) -> bool:
        """
        Verifica e reseta a cota diária se for um novo dia.
        
        Returns:
            bool: True se a cota foi resetada, False caso contrário
        """
        hoje = date.today()
        if self.ultima_atualizacao_cota < hoje:
            self.cota_diaria_usada = 0
            self.ultima_atualizacao_cota = hoje
            return True
        return False
    
    model_config = ConfigDict()
    
    @field_serializer('data_cadastro')
    def serialize_data_cadastro(self, value: datetime) -> str:
        """Serializa datetime para string ISO format."""
        return value.isoformat()
    
    @field_serializer('ultima_atualizacao_cota')
    def serialize_ultima_atualizacao_cota(self, value: date) -> str:
        """Serializa date para string ISO format."""
        return value.isoformat()
        
    def to_dict(self) -> dict[str, Any]:
        """Converte o modelo para dicionário, tratando tipos especiais."""
        data = self.model_dump()
        data["data_cadastro"] = self.data_cadastro.isoformat()
        data["ultima_atualizacao_cota"] = self.ultima_atualizacao_cota.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Usuario":
        """Cria instância a partir de dicionário, tratando tipos especiais."""
        if "data_cadastro" in data and isinstance(data["data_cadastro"], str):
            data["data_cadastro"] = datetime.fromisoformat(data["data_cadastro"])
        if "ultima_atualizacao_cota" in data and isinstance(data["ultima_atualizacao_cota"], str):
            data["ultima_atualizacao_cota"] = date.fromisoformat(data["ultima_atualizacao_cota"])
        return cls(**data)