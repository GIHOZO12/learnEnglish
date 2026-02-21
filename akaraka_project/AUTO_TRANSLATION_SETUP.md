# Auto-Translation Setup Guide

## Current Status
✅ **Lesson creation is now working without external dependencies**

The system will create lessons with auto-translation capability, but requires one more step for actual translations.

## Installation (Optional but Recommended)

To enable automatic Dari translation from English content:

### Step 1: Install googletrans package
```bash
cd c:\Users\Ismail\Downloads\akaraka\akaraka_project
pip install googletrans==4.0.0rc1
```

### Step 2: Verify Installation
```bash
python -c "from googletrans import Translator; print('✓ googletrans installed successfully')"
```

## How It Works

### Without googletrans (Current)
- Lessons can be created with English content
- Dari field remains empty or can be manually filled
- Placeholder text appears if auto-translation is attempted

### With googletrans (Recommended)
- Create lesson with only English content
- Fill in Dari field leave empty
- System automatically translates English to Dari using Google Translate
- Dari field auto-populates with translation

## Usage in Admin Dashboard

1. Go to **Admin Dashboard → Courses → Select Course → Lessons**
2. Click **"+ Add Lesson"**
3. Fill in:
   - **Lesson Title** (required)
   - **English Content** (required)
   - **Dari Content** (optional - leave empty for auto-translation)
   - **Estimated Time** (required)
   - **Lesson Image** (optional)
4. Click **"Create Lesson"**

## Features

✅ No need to upload audio files anymore
✅ Automatic translation from English to Dari
✅ Edit lessons to refine translations
✅ Delete lessons from course
✅ Manage exercises per lesson
✅ Full course content management

## API Endpoint Support

You can also use the translation utilities in your code:

```python
from courses.translation_utils import translate_english_to_dari, translate_batch

# Single translation
dari_text = translate_english_to_dari("Hello, how are you?")

# Batch translation
texts = ["Hello", "Good morning", "Thank you"]
translations = translate_batch(texts)
```

## Notes

- Translation happens automatically when creating/editing lessons without Dari content
- System is fault-tolerant - if translation fails, English content is preserved
- You can always manually edit Dari content later
- No API keys required with googletrans
