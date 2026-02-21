"""
Translation utilities for Akaraka
Uses googletrans for free translation without API keys
Falls back to placeholder if googletrans is not installed
"""
import logging

logger = logging.getLogger(__name__)

# Try to import googletrans, but don't fail if it's not installed
try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False
    logger.warning("googletrans not installed. Install with: pip install googletrans==4.0.0rc1")

_translator = None

def get_translator():
    """Get translator instance (singleton)"""
    global _translator
    
    if not GOOGLETRANS_AVAILABLE:
        return None
    
    if _translator is None:
        try:
            _translator = Translator()
        except Exception as e:
            logger.error(f"Failed to initialize translator: {str(e)}")
    
    return _translator


def translate_english_to_dari(english_text):
    """
    Translate English text to Dari/Pashto using Google Translate
    
    Args:
        english_text (str): Text in English to translate
        
    Returns:
        str: Translated text in Dari, or original text if translation fails
    """
    if not english_text or not english_text.strip():
        return ""
    
    if not GOOGLETRANS_AVAILABLE:
        logger.warning("googletrans not available, returning placeholder. Install with: pip install googletrans==4.0.0rc1")
        return ""
    
    try:
        translator = get_translator()
        if not translator:
            logger.warning("Translator not available, returning original text")
            return english_text
            
        # Translate English to Dari (language code: ps for Pashto/Dari)
        # googletrans 4.0.0rc1 uses 'dest' and 'src' parameters
        result = translator.translate(english_text, src='en', dest='ps')
        
        if result and hasattr(result, 'text'):
            translated_text = result.text
            logger.info(f"Translation successful: {english_text[:50]}... -> {translated_text[:50]}...")
            return translated_text
        
        logger.warning("Translation returned no result")
        return english_text
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        return english_text


def translate_batch(texts):
    """
    Translate multiple texts at once
    
    Args:
        texts (list): List of English texts
        
    Returns:
        list: List of translated texts
    """
    if not texts:
        return []
    
    if not GOOGLETRANS_AVAILABLE:
        logger.warning("googletrans not available. Install with: pip install googletrans==4.0.0rc1")
        return texts
    
    try:
        translator = get_translator()
        if not translator:
            logger.warning("Translator not available, returning original texts")
            return texts
        
        translated = []
        for text in texts:
            if text and text.strip():
                try:
                    result = translator.translate(text, src='en', dest='ps')
                    if result and hasattr(result, 'text'):
                        translated.append(result.text)
                    else:
                        translated.append(text)
                except Exception as e:
                    logger.warning(f"Failed to translate text: {str(e)}")
                    translated.append(text)
            else:
                translated.append(text)
        
        return translated
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        return texts
