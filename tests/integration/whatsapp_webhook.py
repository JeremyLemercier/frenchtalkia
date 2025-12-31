import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any

from app.utils.logger import logger


def get_sample_text() -> str:
    sample = Path("tests/utils/texts/sample_text.txt")
    try:
        return sample.read_text(encoding="utf-8")
    except Exception:
        return "[integration reply]"


def get_sample_audio_path() -> Path:
    return Path("tests/utils/audios/sample_audio.ogg")


def salvar_resultado_integracao(
    tipo_mensagem: str,
    dados_extraidos: dict[str, Any],
    arquivo_audio: Path | None = None,
) -> Path | None:
    """
    Sauvegarde les artefacts d'intégration dans `tests/integration/results/<timestamp>/`.

    Retourne le chemin du dossier créé ou None en cas d'erreur.
    """
    try:
        results_dir = Path("tests/integration/results")
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        result_subdir = results_dir / timestamp_str
        result_subdir.mkdir(parents=True, exist_ok=True)

        extracted_data_path = result_subdir / "extracted_data.json"
        with open(extracted_data_path, "w", encoding="utf-8") as f:
            json.dump(dados_extraidos, f, indent=2, ensure_ascii=False)

        metadata: dict[str, Any] = {
            "timestamp_recebimento": datetime.now().isoformat(),
            "tipo_mensagem": tipo_mensagem,
            "telefone": dados_extraidos.get("telefone"),
        }

        # Se áudio: copiar arquivo e calcular hash
        if arquivo_audio and arquivo_audio.exists():
            try:
                audio_dest = result_subdir / "audio_received.ogg"
                shutil.copy2(arquivo_audio, audio_dest)

                with open(audio_dest, "rb") as f:
                    audio_bytes = f.read()
                    sha256_hash = hashlib.sha256(audio_bytes).hexdigest()

                metadata.update({
                    "tamanho_bytes": len(audio_bytes),
                    "sha256": sha256_hash,
                    "mime_type": dados_extraidos.get("mime_type", "audio/ogg; codecs=opus"),
                })
            except Exception as e:
                logger.exception(f"Erro ao copiar áudio para resultados de integração: {e}")

        metadata_path = result_subdir / "metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Resultado de integração salvo em {result_subdir}")
        return result_subdir

    except Exception as e:
        logger.exception(f"Erro ao salvar resultado de integração: {e}")
        return None


async def baixar_audio_para_integracao(whatsapp_service, media_id: str) -> Path | None:
    """
    Wrapper async pour télécharger l'audio via `whatsapp_service.baixar_audio`.
    Retourne le Path ou None si erreur.
    """
    try:
        arquivo = await whatsapp_service.baixar_audio(media_id)
        logger.info(f"Áudio baixado para integração: {arquivo}")
        return arquivo
    except Exception as e:
        logger.error(f"Erro ao baixar áudio para integração: {e}")
        return None
