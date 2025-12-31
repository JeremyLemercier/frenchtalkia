import json
from pathlib import Path
from typing import Any

INTEGRATION_RESULTS_PATH = Path("./tests/integration/results")

def get_latest_integration_result() -> dict[str, Any] | None:
    """
    Retorna o resultado mais recente de tests/integration/results.
    
    Returns:
        dict[str, Any] | None: Dados extraídos do resultado mais recente
    """
    results_dir = INTEGRATION_RESULTS_PATH
    if not results_dir.exists():
        return None

    # Buscar diretórios com timestamp
    timestamp_dirs = sorted(
        [d for d in results_dir.iterdir() if d.is_dir()],
        key=lambda x: x.name,
        reverse=True
    )

    if not timestamp_dirs:
        return None

    latest_dir = timestamp_dirs[0]
    extracted_data_path = latest_dir / "extracted_data.json"
    metadata_path = latest_dir / "metadata.json"

    with open(extracted_data_path, encoding="utf-8") as f:
        extracted_data = json.load(f)

    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    return {**extracted_data, **metadata}


def list_integration_results() -> list[str]:
    """
    Lista todos os resultados armazenados em tests/integration/results.
    
    Returns:
        list[str]: Lista de timestamps em ordem cronológica
    """
    results_dir = INTEGRATION_RESULTS_PATH
    if not results_dir.exists():
        return []

    timestamp_dirs = sorted(
        [d.name for d in results_dir.iterdir() if d.is_dir()],
        key=lambda x: x
    )

    return timestamp_dirs


def load_integration_result(timestamp: str) -> dict[str, Any]:
    """
    Carrega resultado específico por timestamp.
    
    Args:
        timestamp: Timestamp do resultado a carregar
        
    Returns:
        dict[str, Any]: Dados consolidados do resultado
    """
    result_dir = INTEGRATION_RESULTS_PATH / timestamp
    extracted_data_path = result_dir / "extracted_data.json"
    metadata_path = result_dir / "metadata.json"

    with open(extracted_data_path, encoding="utf-8") as f:
        extracted_data = json.load(f)

    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    return {**extracted_data, **metadata}


def clear_integration_results() -> None:
    """
    Limpa todos os resultados de tests/integration/results.
    
    Remove diretório tests/integration/results completamente.
    Útil para cleanup entre testes.
    """
    import shutil
    results_dir = INTEGRATION_RESULTS_PATH
    if results_dir.exists():
        shutil.rmtree(results_dir)


def verify_audio_file(path: Path) -> bool:
    """
    Verifica se arquivo de áudio é válido.
    
    Args:
        path: Caminho do arquivo de áudio
        
    Returns:
        bool: True se arquivo é válido, False caso contrário
    """
    if not path.exists():
        return False

    if path.stat().st_size == 0:
        return False

    # Verificar extensão
    if path.suffix.lower() not in ['.ogg', '.mp3', '.aac', '.amr', '.m4a']:
        return False

    return True


def verify_extracted_data(data: dict[str, Any], expected_fields: list[str]) -> bool:
    """
    Valida estrutura dos dados extraídos.
    
    Args:
        data: Dados extraídos a validar
        expected_fields: Lista de campos esperados
        
    Returns:
        bool: True se todos os campos esperados existem, False caso contrário
    """
    for field in expected_fields:
        if field not in data:
            return False

    return True
