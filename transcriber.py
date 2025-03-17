import speech_recognition as sr
from pydub import AudioSegment
import sys
import os

# Definir la carpeta de salida
output_folder = r"C:\Users\pablo\Documents\Inti Kamari\Videos Spa\Audios"

# Asegurar que se pasa un archivo como argumento
if len(sys.argv) < 2:
    print("Uso: python transcriber.py archivo.mp3")
    sys.exit(1)

# Obtener el nombre del archivo desde la línea de comandos
audio_file = sys.argv[1]

# Verificar si el archivo existe
if not os.path.exists(audio_file):
    print(f"Error: No se encontró el archivo {audio_file}")
    sys.exit(1)

print(f"Archivo encontrado: {audio_file}")

# Obtener el nombre base del archivo (sin ruta)
base_name = os.path.splitext(os.path.basename(audio_file))[0]

# Convertir a WAV si no está en ese formato
wav_file = os.path.join(output_folder, base_name + ".wav")
print("Convirtiendo archivo a formato WAV...")
try:
    audio = AudioSegment.from_file(audio_file)
    audio.export(wav_file, format="wav")
    print(f"Archivo convertido: {wav_file}")
except Exception as e:
    print(f"Error al convertir el archivo: {e}")
    sys.exit(1)

# Verificar si el archivo WAV fue creado
if not os.path.exists(wav_file):
    print(f"Error: No se generó el archivo WAV en {wav_file}")
    sys.exit(1)

# Inicializar el reconocedor
recognizer = sr.Recognizer()

# Cargar el archivo de audio
try:
    with sr.AudioFile(wav_file) as source:
        print("Procesando audio...")
        audio_data = recognizer.record(source)  # Leer el audio completo
        print("Audio cargado exitosamente.")
except Exception as e:
    print(f"Error al cargar el archivo de audio: {e}")
    sys.exit(1)

# Intentar transcribir el audio
try:
    print("Iniciando transcripción...")
    transcription = recognizer.recognize_google(audio_data, language="es-ES")
    output_file = os.path.join(output_folder, base_name + ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transcription)
    print(f"Transcripción completada. Guardado en: {output_file}")
except sr.UnknownValueError:
    print("No se pudo transcribir el audio (audio no reconocido).")
except sr.RequestError:
    print("Error al conectar con el servicio de reconocimiento de voz.")
except Exception as e:
    print(f"Error inesperado: {e}")

# Verificar si el archivo de transcripción se generó correctamente
if not os.path.exists(output_file):
    print(f"Error: No se generó el archivo de transcripción en {output_file}")
    sys.exit(1)

# Eliminar archivo temporal WAV
try:
    os.remove(wav_file)
    print("Archivo temporal eliminado.")
except Exception as e:
    print(f"Error al eliminar archivo temporal: {e}")
