import os
import time
import logging
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

print(">>> SCRIPT CARGADO: THIS IS IT")

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("transcripciones.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

def normalize_name(name: str) -> str:
    replacements = {
        " ": "_", "(": "", ")": "",
        "á":"a","é":"e","í":"i","ó":"o","ú":"u","ñ":"n"
    }
    for src, dst in replacements.items():
        name = name.replace(src, dst)
    return name

# Intentar uso de Whisper local; si falla, caer a API.
try:
    import whisper
    MODEL = whisper.load_model("base")
    def TRANSCRIBER(path: Path) -> str:
        logging.info("Usando Whisper LOCAL para transcribir.")
        return MODEL.transcribe(str(path))["text"]
except Exception:
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    def TRANSCRIBER(path: Path, retries: int = 3, backoff: float = 2.0) -> str:
        logging.info("Usando Whisper API (v1) para transcribir.")
        for attempt in range(1, retries + 1):
            try:
                with open(path, "rb") as audio_f:
                    resp = openai.Audio.transcriptions.create(
                        file=audio_f,
                        model="whisper-1",
                        language="es"
                    )
                return resp["text"]
            except Exception as e:
                logging.warning(f"Intento {attempt} fallido para {path.name}: {e}")
                if attempt < retries:
                    time.sleep(backoff ** attempt)
                else:
                    raise
                
def process_file(mp3_path: Path, output_dir: Path):
    safe_stem = normalize_name(mp3_path.stem)
    txt_path  = output_dir / f"{safe_stem}.txt"

    if txt_path.exists():
        logging.info(f"{txt_path.name} ya existe, saltando.")
        return

    try:
        logging.info(f"Transcribiendo: {mp3_path.name}")
        text = TRANSCRIBER(mp3_path)
        txt_path.write_text(text, encoding="utf-8")
        logging.info(f"Guardado: {txt_path.name}")
    except Exception as e:
        logging.error(f"Error al transcribir {mp3_path.name}: {e}")

def main():
    print(">>> Arrancando transcripción…")  # Diagnóstico

    parser = argparse.ArgumentParser(
        description="Transcribe todos los MP3 de una carpeta usando Whisper."
    )
    parser.add_argument("input", help="Carpeta con archivos .mp3")
    parser.add_argument(
        "-o","--output",
        help="Carpeta destino (por defecto, misma carpeta)",
        default=None
    )
    parser.add_argument(
        "-w","--workers",
        type=int, default=4,
        help="Número de hilos concurrentes"
    )
    args = parser.parse_args()

    in_dir  = Path(args.input).expanduser().resolve()
    out_dir = Path(args.output).expanduser().resolve() if args.output else in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f">>> Carpeta de entrada: {in_dir}")
    print(f">>> Carpeta de salida : {out_dir}")

    mp3_files = sorted(in_dir.glob("*.mp3"))
    print(f">>> Archivos MP3 encontrados: {len(mp3_files)} -> {mp3_files}")

    if not mp3_files:
        logging.warning("No se encontraron archivos .mp3 en la carpeta.")
        return

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(process_file, mp3, out_dir): mp3 for mp3 in mp3_files}
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logging.error(f"Fallo inesperado en {futures[future].name}: {e}")

if __name__ == "__main__":
    main()
