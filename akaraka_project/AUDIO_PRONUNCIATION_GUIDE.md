# Audio Pronunciation Feature - Setup & Usage

## What's New

✅ **Automatic Text-to-Speech (TTS) Audio Generation**
- English pronunciation audio for lesson content
- Dari/Pashto pronunciation audio for lesson content  
- Click "🔊 Speak" buttons in lesson to hear pronunciations
- Web Speech API integration for browser-based playback

## Installation

### Required Package
```bash
pip install gTTS==2.3.2
```

## How It Works

### 1. Creating Lessons with Audio
When you create or edit a lesson in the Admin Dashboard:
- Fill in English content and Dari content
- Click "Create Lesson" or "Update Lesson"
- System automatically generates:
  - English pronunciation MP3 file
  - Dari pronunciation MP3 file
- Audio files are stored in `/media/audio/lessons/`

### 2. Lesson Page Audio Features
On the lesson detail page, students see:
- **"🔊 Speak" button for English** - Click to hear English pronunciation
- **"🔊 تکلم (Speak) button for Dari** - Click to hear Dari pronunciation
- Audio uses browser's Web Speech API for instant playback
- Works offline - no internet required after initial generation

### 3. Features Included
✅ Automatic MP3 generation for lessons
✅ Caching - audio files are reused if already generated
✅ Fallback language support (Urdu as backup for Dari)
✅ Web Speech API for browser playback
✅ Works in all modern browsers (Chrome, Firefox, Safari, Edge)
✅ Supports text content up to 5000 characters

## Usage in Admin Dashboard

### Create Lesson with Audio
1. Go to **Courses → Select Course → Lessons → "+ Add Lesson"**
2. Fill all fields:
   - Lesson Title ✓
   - English Content ✓ (audio will be generated)
   - Estimated Time ✓
3. Leave Dari empty → auto-translated + audio generated
4. Click "Create Lesson"
5. ✓ Audio files automatically generated

### Edit Lesson Audio
1. Go to lesson in lesson management
2. Click "Edit"
3. Modify English or Dari content
4. Click "Update Lesson"
5. ✓ New audio files regenerated

## Audio Quality

| Language | Quality | Speed |
|----------|---------|-------|
| English | Natural | Normal (0.9x) |
| Dari | Natural | Slower (0.8x) |

## Browser Support

✓ Chrome 25+
✓ Firefox 49+
✓ Safari 14.1+
✓ Edge 79+
✓ Opera 35+

## Troubleshooting

### "Audio generation failed" message
**Solution:** Install gTTS package
```bash
pip install gTTS==2.3.2
```

### Audio files not being created
**Ensure:** 
- MEDIA_ROOT is configured in Django settings
- `/media/audio/lessons/` directory exists and is writable
- gTTS is installed

### Speak button does not play sound
**Check:**
- Browser supports Web Speech API
- Speaker/headphones are connected
- Browser hasn't blocked audio playback

## Technical Details

### Audio Storage
- Location: `/media/audio/lessons/`
- Format: MP3 (compatible with all browsers)
- Size: ~50-100 KB per 100 words
- Naming: `lesson_{id}_en.mp3`, `lesson_{id}_ps.mp3`

### Caching
- Audio files are generated once and reused
- Regenerated only when lesson content changes
- No duplicate generation

### Language Codes
- English: `en` (en-US pronunciation)
- Dari/Pashto: `ps` (with fallback to `ur` if unavailable)

## API Usage (For Developers)

```python
from courses.tts_utils import generate_lesson_audio, generate_word_audio

# Generate audio for entire lesson
lesson = Lesson.objects.get(id=1)
audio_files = generate_lesson_audio(lesson)
# Returns: {'english': 'audio/lessons/lesson_1_en.mp3', 'dari': 'audio/lessons/lesson_1_ps.mp3'}

# Generate audio for vocabulary word
audio = generate_word_audio('Hello', 'سلام', word_id=5)
# Returns: {'english': 'audio/lessons/word_5_en.mp3', 'dari': 'audio/lessons/word_5_ps.mp3'}
```

## Next Steps (Optional)

1. **Customize Voice** - Modify gTTS parameters in `tts_utils.py`
2. **Add Voice Selection** - Let teachers choose between voices
3. **Download Offline** - Add option to download audio files
4. **Progress Tracking** - Track which students use audio feature

## Support

For issues or questions about the audio pronunciation feature:
- Check that gTTS==2.3.2 is installed
- Ensure media directories have proper permissions
- Test audio generation with the management command
