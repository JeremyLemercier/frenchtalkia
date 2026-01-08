from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import configuracao
from app.routes import webhook
from app.services.gladia_service import GladiaService
from app.services.mistral_service import MistralService
from app.services.murf_service import MurfService
from app.services.usuario_service import UsuarioService
from app.services.whatsapp_service import WhatsAppService
from app.storage.conversa_storage import ConversaStorage
from app.storage.sessao_storage import SessaoStorage
from app.storage.usuario_storage import UsuarioStorage
from app.utils.logger import logger

# Constantes
APP_DESCRIPTION = "API para robô de aprendizado de francês via WhatsApp"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação."""
    # Startup
    startup_event()
    yield
    # Shutdown (se necessário)
    await shutdown_event()


def startup_event():
    """Evento de inicialização da aplicação."""
    # Validar que a configuração foi carregada com sucesso
    if configuracao is None:
        erro_msg = (
            "\n❌ ERRO FATAL: Não foi possível inicializar a aplicação.\n"
            "A configuração não pôde ser carregada devido a variáveis de ambiente ausentes ou inválidas.\n\n"
            "Por favor, verifique:\n"
            "1. Se o arquivo .env existe no diretório raiz do projeto\n"
            "2. Se todas as variáveis obrigatórias estão definidas:\n"
            "   - WHATSAPP_TOKEN\n"
            "   - WHATSAPP_PHONE_NUMBER_ID\n"
            "   - WHATSAPP_VERIFY_TOKEN\n"
            "   - MISTRAL_API_KEY\n"
            "   - GLADIA_API_KEY\n"
            "   - MURF_API_KEY\n\n"
            "Você pode copiar o arquivo .env.example para .env e preencher os valores necessários.\n"
        )
        raise RuntimeError(erro_msg)

    # Criar diretórios necessários
    configuracao.diretorio_dados.mkdir(parents=True, exist_ok=True)
    configuracao.diretorio_temp_audio.mkdir(parents=True, exist_ok=True)

    # Inicializar storages
    usuario_storage = UsuarioStorage(configuracao.diretorio_dados / "usuarios.json")
    sessao_storage = SessaoStorage(configuracao.diretorio_dados / "sessoes.json")
    conversa_storage = ConversaStorage(configuracao.diretorio_dados / "conversas.json")

    # Inicializar serviços
    usuario_service = UsuarioService(usuario_storage, sessao_storage)
    whatsapp_service = WhatsAppService(configuracao)
    gladia_service = GladiaService()
    mistral_service = MistralService()
    murf_service = MurfService()

    # Armazenar serviços no estado da aplicação para acesso global
    app.state.usuario_service = usuario_service
    app.state.usuario_storage = usuario_storage
    app.state.sessao_storage = sessao_storage
    app.state.conversa_storage = conversa_storage
    app.state.whatsapp_service = whatsapp_service
    app.state.gladia_service = gladia_service
    app.state.mistral_service = mistral_service
    app.state.murf_service = murf_service

    logger.info("Aplicação FrenchTalkIA inicializada com sucesso!")
    logger.info(f"Diretório de dados: {configuracao.diretorio_dados}")
    logger.info(f"Diretório de áudio temporário: {configuracao.diretorio_temp_audio}")
    logger.info(f"Ambiente: {configuracao.ambiente}")


async def shutdown_event():
    """Evento de encerramento da aplicação."""
    logger.info("Encerrando aplicação FrenchTalkIA...")
    try:
        # If application `app` is available in globals, attempt to close whatsapp client's httpx session
        app_obj = globals().get("app")
        if app_obj is not None and hasattr(app_obj, "state"):
            whatsapp_svc = getattr(app_obj.state, "whatsapp_service", None)
            if whatsapp_svc is not None:
                try:
                    await whatsapp_svc.close()
                    logger.info("WhatsAppService HTTP client fechado com sucesso")
                except Exception as e:
                    logger.exception(f"Erro ao fechar WhatsAppService: {e}")
    except Exception:
        logger.exception("Erro durante shutdown_event")


# Criar aplicação FastAPI com gerenciamento de ciclo de vida
app = FastAPI(
    title="FrenchTalkIA",
    description=APP_DESCRIPTION,
    version="0.1.0",
    lifespan=lifespan,
)

# Configurar CORS (se necessário)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(webhook.router)


@app.get("/")
async def root() -> dict[str, Any]:
    """Endpoint raiz da aplicação."""
    return {"message": "FrenchTalkIA API", "version": "0.1.0", "status": "operacional"}


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Endpoint de health check."""
    if configuracao is None:
        return {
            "status": "error",
            "servico": "FrenchTalkIA",
            "ambiente": "desconhecido",
            "versao": "0.1.0",
            "erro": "Configuração não carregada - verifique as variáveis de ambiente",
        }

    return {
        "status": "ok",
        "servico": "FrenchTalkIA",
        "ambiente": configuracao.ambiente,
        "versao": "0.1.0",
    }


@app.get("/info")
async def info() -> dict[str, Any]:
    """Endpoint com informações detalhadas da aplicação."""
    if configuracao is None:
        return {
            "nome": "FrenchTalkIA",
            "descricao": APP_DESCRIPTION,
            "versao": "0.1.0",
            "status": "erro_configuracao",
            "erro": "Configuração não carregada - verifique as variáveis de ambiente",
            "endpoints": {
                "health": "/health",
                "webhook_whatsapp": "/webhook/whatsapp",
                "docs": "/docs",
                "redoc": "/redoc",
            }
        }

    return {
        "nome": "FrenchTalkIA",
        "descricao": APP_DESCRIPTION,
        "versao": "0.1.0",
        "status": "operacional",
        "ambiente": configuracao.ambiente,
        "endpoints": {
            "health": "/health",
            "webhook_whatsapp": "/webhook/whatsapp",
            "docs": "/docs",
            "redoc": "/redoc",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
