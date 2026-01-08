import os
import threading
import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import ConfiguracaoApp


@pytest.fixture
def mock_config() -> MagicMock:
    """Fixture que retorna configuração mockada com valores padrão."""
    config = MagicMock(spec=ConfiguracaoApp)
    config.whatsapp_token = "test_token"
    config.whatsapp_phone_number_id = "123456789"
    config.whatsapp_verify_token = "test_verify_token"
    config.diretorio_temp_audio = Path("./temp/audio")
    return config


@pytest.fixture
def mock_httpx_client() -> AsyncMock:
    """Fixture que retorna cliente HTTP mockado para testes unitários."""
    return AsyncMock()


@pytest.fixture
def integration_mode() -> bool:
    """Fixture que detecta se está em modo de integração."""
    return os.getenv("INTEGRATION_WHATSAPP", "false").lower() == "true"


@pytest.fixture
def integration_results_dir() -> Path:
    """Fixture que retorna caminho para resultados de integração."""
    return Path("./tests/integration/results")


@pytest.fixture
def sample_text_payload() -> dict[str, Any]:
    """Fixture que carrega payload de texto de exemplo."""
    payload_path = Path(__file__).parent / "utils" / "payloads" / "text_message.json"
    import json
    with open(payload_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_audio_payload() -> dict[str, Any]:
    """Fixture que carrega payload de áudio de exemplo."""
    payload_path = Path(__file__).parent / "utils" / "payloads" / "audio_message.json"
    import json
    with open(payload_path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def sample_audio_file() -> Path:
    """Fixture que retorna Path para arquivo de áudio de exemplo."""
    return Path(__file__).parent / "utils" / "audios" / "sample_audio.ogg"


@pytest.fixture(autouse=True)
def _patch_asyncio_create_task(monkeypatch):
    """Start a background asyncio loop and patch create_task used by app.routes.webhook.

    The FastAPI BackgroundTasks executes callables in a threadpool; calling
    `asyncio.create_task` there raises "no running event loop". Tests patch
    `app.routes.webhook.asyncio.create_task` to schedule coroutines on a
    dedicated loop running in a background thread using
    `asyncio.run_coroutine_threadsafe`.
    """
    loop = asyncio.new_event_loop()
    thread = threading.Thread(target=loop.run_forever, daemon=True)
    thread.start()

    def _create_task(coro):
        return asyncio.run_coroutine_threadsafe(coro, loop)

    monkeypatch.setattr("app.routes.webhook.asyncio.create_task", _create_task)

    yield

    loop.call_soon_threadsafe(loop.stop)
    thread.join(timeout=1)
