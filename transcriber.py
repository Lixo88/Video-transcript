import os
import concurrent.futures
import speech_recognition as sr
from pydub import AudioSegment

# Define input and output folder
input_folder = r"C:\Users\pablo\Downloads\asd"
output_folder = input_folder  # Save the files in the same folder

# Set the correct FFmpeg path
AudioSegment.converter = r"C:\ffmpeg-2025-03-17-git-5b9356f18e-essentials_build\ffmpeg-2025-03-17-git-5b9356f18e-essentials_build\bin\ffmpeg.exe"
print(f"FFmpeg configured at: {AudioSegment.converter}")

def process_file(file):
    # Normalize the file name to avoid issues with special characters
    safe_file = (file.replace(" ", "_")
                   .replace("(", "")
                   .replace(")", "")
                   .replace("á", "a")
                   .replace("é", "e")
                   .replace("í", "i")
                   .replace("ó", "o")
                   .replace("ú", "u"))
    
    audio_file = os.path.abspath(os.path.join(input_folder, file))
    base_name = os.path.splitext(safe_file)[0]
    wav_file = os.path.join(output_folder, base_name + ".wav")
    output_file = os.path.join(output_folder, base_name + ".txt")
    
    print(f"\nProcessing: {file}")
    print(f"Full path: {audio_file}")

    if not os.path.exists(audio_file):
        print(f"Error: File does not exist at {audio_file}")
        return

    # Attempt to open the file with Pydub
    try:
        print(f"Trying to open file with Pydub: {audio_file}")
        audio = AudioSegment.from_file(audio_file)
        print(f"Detected format: {audio.channels} channels, {audio.frame_rate} Hz, {audio.sample_width} bytes per sample")
    except Exception as e:
        print(f"Error reading file {file}: {e}")
        return

    # Convert MP3 to WAV
    try:
        audio.export(wav_file, format="wav")
        print(f"Converted file: {wav_file}")
    except Exception as e:
        print(f"Error converting {file}: {e}")
        return

    # Initialize the recognizer and load the WAV file
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(wav_file) as source:
            print("Processing audio...")
            audio_data = recognizer.record(source)
    except Exception as e:
        print(f"Error loading {file}: {e}")
        return

    # Attempt to transcribe the audio using Google Speech Recognition (Spanish)
    try:
        print("Starting transcription...")
        transcription = recognizer.recognize_google(audio_data, language="en-EN")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcription)
        print(f"Transcription completed. Saved in: {output_file}")
    except sr.UnknownValueError:
        print(f"Could not transcribe {file} (audio not recognized).")
    except sr.RequestError:
        print("Error connecting to the speech recognition service.")
    except Exception as e:
        print(f"Unexpected error in {file}: {e}")

    # Remove the temporary WAV file
    try:
        os.remove(wav_file)
        print("Temporary file removed.")
    except Exception as e:
        print(f"Error deleting temporary file for {file}: {e}")

def main():
    # Get all MP3 files in the input folder
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(".mp3")]
    if not files:
        print("No MP3 files found in the folder.")
        return

    print(f"Files found: {len(files)}")

    # Process files concurrently using a ThreadPoolExecutor.
    # You can adjust max_workers if needed.
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_file, file) for file in files]
        concurrent.futures.wait(futures)

if __name__ == "__main__":
    main()
