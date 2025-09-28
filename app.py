import os
from flask import Flask, request, jsonify, send_from_directory
from googletrans import Translator
from docx import Document
from PIL import Image
import pytesseract
import tempfile
import speech_recognition as sr
import pydub
from pydub import AudioSegment

app = Flask(__name__, static_folder='.')
translator = Translator()

# Configure Tesseract path if it's not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configure FFmpeg path for audio processing
import os
import shutil

# Check if FFmpeg is available in system PATH
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    print(f"FFmpeg found in system PATH: {ffmpeg_path}")
else:
    # Fallback to check Downloads folder
    downloads_ffmpeg = os.path.join(os.path.expanduser("~"), "Downloads", "ffmpeg", "ffmpeg-master-latest-win64-gpl-shared", "bin", "ffmpeg.exe")
    if os.path.exists(downloads_ffmpeg):
        ffmpeg_dir = os.path.dirname(downloads_ffmpeg)
        os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
        print(f"FFmpeg configured from Downloads: {downloads_ffmpeg}")
    else:
        print("FFmpeg not found in system PATH or Downloads - will use WAV files only") 

# Initialize speech recognizer
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Minimum audio energy to consider for recording
recognizer.dynamic_energy_threshold = True
recognizer.dynamic_energy_adjustment_damping = 0.15
recognizer.dynamic_energy_ratio = 1.5
recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before a phrase is considered complete
recognizer.operation_timeout = None  # Seconds to wait for a phrase to start
recognizer.phrase_threshold = 0.3  # Minimum seconds of speaking audio before we consider the speaking audio a phrase
recognizer.non_speaking_duration = 0.8  # Seconds of non-speaking audio to keep on both sides of the recording

# Utility functions for text extraction
def extract_text_from_image(image_path):
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        return f"Error with OCR: {e}"

def extract_text_from_audio(audio_path):
    try:
        print(f"Processing audio file: {audio_path}")
        
        # Check if the file is already a WAV file
        file_ext = os.path.splitext(audio_path)[1].lower()
        print(f"File extension: {file_ext}")
        
        # For WAV files, use directly
        if file_ext == '.wav':
            wav_path = audio_path
            print("Using WAV file directly")
        else:
            # For other formats, try conversion but handle FFmpeg gracefully
            try:
                print("Attempting to convert audio to WAV...")
                audio = AudioSegment.from_file(audio_path)
                # Create a proper WAV filename
                base_name = os.path.splitext(audio_path)[0]
                wav_path = base_name + '.wav'
                audio.export(wav_path, format="wav")
                print(f"Audio converted to: {wav_path}")
            except Exception as e:
                print(f"Audio conversion error: {e}")
                error_msg = str(e).lower()
                if any(keyword in error_msg for keyword in ["ffmpeg", "cannot find", "not found", "avconv"]):
                    return f"❌ Audio conversion failed: FFmpeg not found.\n\n🔧 Solutions:\n1. Use WAV files (recommended) - they work without FFmpeg\n2. Install FFmpeg from: https://ffmpeg.org/download.html\n3. Convert your audio to WAV using an online converter\n\n💡 Tip: Record audio directly in the browser for best results!"
                else:
                    return f"Audio conversion failed: {e}"
        
        # Use speech recognition
        print("Starting speech recognition...")
        try:
            with sr.AudioFile(wav_path) as source:
                # Adjust for ambient noise
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                print("Recording audio data...")
                audio_data = recognizer.record(source)
                print("Recognizing speech...")
                
                # Try multiple recognition methods
                try:
                    text = recognizer.recognize_google(audio_data)
                    print(f"Recognized text: {text}")
                except sr.UnknownValueError:
                    print("Google recognition failed, trying with language hint...")
                    try:
                        text = recognizer.recognize_google(audio_data, language='en-US')
                        print(f"Recognized text (with language hint): {text}")
                    except sr.UnknownValueError:
                        print("Speech recognition could not understand the audio")
                        return "Could not understand the audio. Please speak clearly and try again."
                except sr.RequestError as e:
                    print(f"Google recognition service error: {e}")
                    return f"Error with speech recognition service: {e}"
                    
        except Exception as e:
            print(f"Error during speech recognition: {e}")
            return f"Error during speech recognition: {e}"
        
        # Clean up temporary WAV file if we created one
        if wav_path != audio_path and os.path.exists(wav_path):
            os.unlink(wav_path)
            print("Cleaned up temporary WAV file")
        
        return text
    except FileNotFoundError as e:
        print(f"Audio file not found: {e}")
        return f"Audio file not found: {e}"
    except Exception as e:
        print(f"Unexpected error processing audio: {e}")
        return f"Error processing audio: {e}"

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error with DOCX: {e}"

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("Upload request received")
    if 'file' not in request.files:
        print("No file part in request")
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        print("No file selected")
        return jsonify({'error': 'No selected file'}), 400

    print(f"Processing file: {file.filename}")
    file_ext = os.path.splitext(file.filename)[1].lower()
    print(f"File extension: {file_ext}")
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        file.save(temp_file.name)
        temp_path = temp_file.name
        print(f"File saved to: {temp_path}")
    
    extracted_text = ""
    if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
        print("Processing as image")
        extracted_text = extract_text_from_image(temp_path)
    elif file_ext in ['.doc', '.docx']:
        print("Processing as document")
        extracted_text = extract_text_from_docx(temp_path)
    elif file_ext == '.pdf':
        print("Processing as PDF")
        # PDF handling with PyPDF2 or pdfplumber can be added here
        # For simplicity, we assume PDFs are images for now and use OCR
        extracted_text = extract_text_from_image(temp_path)
    elif file_ext in ['.mp3', '.wav', '.m4a', '.ogg']:
        print("Processing as audio")
        extracted_text = extract_text_from_audio(temp_path)
    else:
        print(f"Unsupported file type: {file_ext}")
        extracted_text = f"Unsupported file type: {file_ext}"

    print(f"Extracted text: {extracted_text}")
    os.unlink(temp_path) # Clean up temp file
    print("Temp file cleaned up")

    return jsonify({'text': extracted_text})

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json
    text_to_translate = data.get('text', '')
    target_language = data.get('target_language', 'mr')  # Default to Marathi
    
    # Language mapping for unsupported languages
    language_mapping = {
        'gon': 'ml',  # Gondi -> Malayalam (closest available)
        'sat': 'ml',  # Santali -> Malayalam (closest available)
        'mr': 'mr',   # Marathi
        'ur': 'ur',   # Urdu
        'ml': 'ml'    # Malayalam
    }
    
    # Get the actual language code to use
    actual_language = language_mapping.get(target_language, target_language)
    
    # Language detection can be done here, or assumed
    # Example: translator.detect(text_to_translate).lang
    # Translate from English ('en') to the selected minority language
    try:
        translated = translator.translate(text_to_translate, dest=actual_language).text
        
        # Add note for unsupported languages
        if target_language in ['gon', 'sat']:
            translated += f"\n\n[Note: Translated to Malayalam as {target_language.upper()} is not directly supported by Google Translate]"
        
        return jsonify({'translation': translated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/backtranslate', methods=['POST'])
def backtranslate_text():
    data = request.json
    text_to_backtranslate = data.get('text', '')
    source_language = data.get('source_language', 'mr')  # Default to Marathi
    
    # Language mapping for unsupported languages
    language_mapping = {
        'gon': 'ml',  # Gondi -> Malayalam (closest available)
        'sat': 'ml',  # Santali -> Malayalam (closest available)
        'mr': 'mr',   # Marathi
        'ur': 'ur',   # Urdu
        'ml': 'ml'    # Malayalam
    }
    
    # Get the actual language code to use
    actual_language = language_mapping.get(source_language, source_language)
    
    # Back-translate from the selected minority language to English ('en')
    try:
        back_translated = translator.translate(text_to_backtranslate, src=actual_language, dest='en').text
        return jsonify({'translation': back_translated})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)