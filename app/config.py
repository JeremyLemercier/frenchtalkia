from pathlib import Path
from typing import Literal, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class ConfiguracaoApp(BaseSettings):
    """Configuração da aplicação usando Pydantic Settings."""
    
    # WhatsApp Cloud API
    whatsapp_token: str = Field(..., alias="WHATSAPP_TOKEN", description="Token de autenticação da WhatsApp Cloud API")
    whatsapp_phone_number_id: str = Field(..., alias="WHATSAPP_PHONE_NUMBER_ID", description="ID do número de telefone WhatsApp")
    whatsapp_verify_token: str = Field(..., alias="WHATSAPP_VERIFY_TOKEN", description="Token para verificação do webhook")
    
    # APIs Externas
    mistral_api_key: str = Field(..., alias="MISTRAL_API_KEY", description="Chave da API Mistral")
    gladia_api_key: str = Field(..., alias="GLADIA_API_KEY", description="Chave da API Gladia")
    murf_api_key: str = Field(..., alias="MURF_API_KEY", description="Chave da API Murf")
    
    # Configurações da Aplicação
    ambiente: Literal["dev", "prod"] = Field(default="dev", alias="AMBIENTE", description="Ambiente de execução")
    diretorio_dados: Path = Field(default=Path("./data"), alias="DIRETORIO_DADOS", description="Caminho para armazenamento JSON")
    diretorio_temp_audio: Path = Field(default=Path("./temp/audio"), alias="DIRETORIO_TEMP_AUDIO", description="Caminho para arquivos temporários")
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "populate_by_name": True,
    }
        
    @field_validator("diretorio_dados", "diretorio_temp_audio", mode="before")
    @classmethod
    def converter_path(cls, v: Union[str, Path]) -> Path:
        """Converte string para Path se necessário."""
        if isinstance(v, str):
            return Path(v)
        return v
    
    @field_validator("whatsapp_token", "whatsapp_phone_number_id", "whatsapp_verify_token",
               "mistral_api_key", "gladia_api_key", "murf_api_key", mode="before")
    @classmethod
    def validar_campos_obrigatorios(cls, v: str) -> str:
        """Valida que campos obrigatórios não estão vazios."""
        if not v or v.strip() == "":
            raise ValueError("Campo obrigatório não pode estar vazio")
        return v


# Variável global para armazenar a configuração
# Inicializada na função get_configuracao() para permitir tratamento de erro adequado
_configuracao: ConfiguracaoApp | None = None


def get_configuracao() -> ConfiguracaoApp:
    """
    Retorna a instância singleton da configuração.
    Carrega a configuração a partir das variáveis de ambiente ou do arquivo .env.
    
    Raises:
        ValueError: Se as variáveis de ambiente obrigatórias não estiverem definidas.
        
    Returns:
        ConfiguracaoApp: Instância da configuração da aplicação.
    """
    global _configuracao
    
    if _configuracao is None:
        try:
            _configuracao = ConfiguracaoApp()  # type: ignore[call-arg]
        except Exception as e:
            erro_msg = (
                f"Erro ao carregar configuração: {e}\n"
                "Verifique se o arquivo .env existe e contém todas as variáveis necessárias.\n"
                "Você pode copiar o arquivo .env.example para .env e preencher os valores necessários:\n"
                "- WHATSAPP_TOKEN\n"
                "- WHATSAPP_PHONE_NUMBER_ID\n"
                "- WHATSAPP_VERIFY_TOKEN\n"
                "- MISTRAL_API_KEY\n"
                "- GLADIA_API_KEY\n"
                "- MURF_API_KEY"
            )
            raise ValueError(erro_msg) from e
    
    return _configuracao


# Mantido para compatibilidade com código existente
# Sugere-se usar get_configuracao() em novo código
configuracao: ConfiguracaoApp | None = None
try:
    configuracao = get_configuracao()
except ValueError as e:
    # Define configuracao como None para evitar NameError
    # A validação adequada deve ser feita onde a configuração é usada
    import sys
    print(f"\n❌ ERRO DE CONFIGURAÇÃO: {e}\n", file=sys.stderr)
    configuracao = None