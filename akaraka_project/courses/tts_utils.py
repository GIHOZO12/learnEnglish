"""
Text-to-Speech utilities for Akaraka
Generates audio files for English and Dari pronunciations
"""
import os
import logging
from django.conf import settings
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.warning("gTTS not installed. Install with: pip install gTTS==2.3.2")


def ensure_audio_directories():
    """Ensure audio directories exist"""
    audio_dirs = [
        os.path.join(settings.MEDIA_ROOT, 'audio', 'lessons'),
        os.path.join(settings.MEDIA_ROOT, 'audio', 'vocabulary'),
    ]
    
    for dir_path in audio_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)


def generate_audio_english(text, filename=None):
    """
    Generate English pronunciation audio
    
    Args:
        text (str): English text to convert to speech
        filename (str): Optional custom filename (without extension)
        
    Returns:
        str: Path to generated audio file, or None if failed
    """
    if not text or not text.strip():
        return None
    
    if not GTTS_AVAILABLE:
        logger.warning("gTTS not available. Install with: pip install gTTS==2.3.2")
        return None
    
    try:
        ensure_audio_directories()
        
        # Generate filename if not provided
        if not filename:
            filename = f"english_{hash(text) % 1000000}"
        
        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'lessons', f"{filename}.mp3")
        
        # Skip if file already exists
        if os.path.exists(audio_path):
            logger.info(f"Audio file already exists: {audio_path}")
            return f"audio/lessons/{filename}.mp3"
        
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(audio_path)
        
        logger.info(f"Generated English audio: {audio_path}")
        return f"audio/lessons/{filename}.mp3"
        
    except Exception as e:
        logger.error(f"Error generating English audio: {str(e)}")
        return None


def generate_audio_dari(text, filename=None):
    """
    Generate Dari/Pashto pronunciation audio
    
    Args:
        text (str): Dari text to convert to speech
        filename (str): Optional custom filename (without extension)
        
    Returns:
        str: Path to generated audio file, or None if failed
    """
    if not text or not text.strip():
        return None
    
    if not GTTS_AVAILABLE:
        logger.warning("gTTS not available. Install with: pip install gTTS==2.3.2")
        return None
    
    try:
        ensure_audio_directories()
        
        # Generate filename if not provided
        if not filename:
            filename = f"dari_{hash(text) % 1000000}"
        
        audio_path = os.path.join(settings.MEDIA_ROOT, 'audio', 'lessons', f"{filename}.mp3")
        
        # Skip if file already exists
        if os.path.exists(audio_path):
            logger.info(f"Audio file already exists: {audio_path}")
            return f"audio/lessons/{filename}.mp3"
        
        # Try different language codes for Dari/Pashto
        lang_codes = ['ps', 'ur', 'fa']  # Pashto, Urdu, Farsi
        
        for lang_code in lang_codes:
            try:
                logger.info(f"Attempting to generate Dari audio with language code: {lang_code}")
                tts = gTTS(text=text, lang=lang_code, slow=False)
                tts.save(audio_path)
                logger.info(f"Generated Dari audio with {lang_code}: {audio_path}")
                return f"audio/lessons/{filename}.mp3"
            except Exception as e:
                logger.warning(f"Failed with language code {lang_code}: {str(e)}")
                continue
        
        # If all language codes fail, log error
        logger.error(f"Could not generate Dari audio for any language code")
        return None
        
    except Exception as e:
        logger.error(f"Error generating Dari audio: {str(e)}")
        return None


def generate_lesson_audio(lesson):
    """
    Generate audio files for lesson content
    
    Args:
        lesson: Lesson object
        
    Returns:
        dict: Dictionary with audio file paths
    """
    audio_files = {}
    
    # Generate English audio
    if lesson.content_english:
        english_audio = generate_audio_english(
            lesson.content_english,
            filename=f"lesson_{lesson.id}_en"
        )
        if english_audio:
            audio_files['english'] = english_audio
    
    # Generate Dari audio
    if lesson.content_dari:
        dari_audio = generate_audio_dari(
            lesson.content_dari,
            filename=f"lesson_{lesson.id}_ps"
        )
        if dari_audio:
            audio_files['dari'] = dari_audio
    
    return audio_files


def generate_word_audio(english_word, dari_word=None, word_id=None):
    """
    Generate audio files for vocabulary word
    
    Args:
        english_word (str): English word
        dari_word (str): Dari/Pashto word
        word_id (int): Vocabulary word ID for filename
        
    Returns:
        dict: Dictionary with audio file paths
    """
    audio_files = {}
    
    # Generate English pronunciation
    if english_word:
        english_audio = generate_audio_english(
            english_word,
            filename=f"word_{word_id}_en" if word_id else None
        )
        if english_audio:
            audio_files['english'] = english_audio
    
    # Generate Dari pronunciation
    if dari_word:
        dari_audio = generate_audio_dari(
            dari_word,
            filename=f"word_{word_id}_ps" if word_id else None
        )
        if dari_audio:
            audio_files['dari'] = dari_audio
    
    return audio_files
