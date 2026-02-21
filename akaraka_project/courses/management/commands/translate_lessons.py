"""
Django management command to translate all lessons to Dari
Usage: python manage.py translate_lessons [--force] [--lesson-id=123]
"""
from django.core.management.base import BaseCommand
from courses.models import Lesson
from courses.translation_utils import translate_english_to_dari
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Translate lesson content from English to Dari'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force re-translation of all lessons, even if Dari content already exists'
        )
        parser.add_argument(
            '--lesson-id',
            type=int,
            help='Translate a specific lesson by ID'
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        lesson_id = options.get('lesson_id')

        if lesson_id:
            try:
                lesson = Lesson.objects.get(id=lesson_id)
                self.translate_lesson(lesson, force)
            except Lesson.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Lesson with ID {lesson_id} not found')
                )
        else:
            # Translate all lessons
            if force:
                lessons = Lesson.objects.all()
                self.stdout.write(
                    self.style.WARNING(
                        f'Re-translating {lessons.count()} lessons (force mode)...'
                    )
                )
            else:
                lessons = Lesson.objects.filter(content_dari='')
                self.stdout.write(
                    self.style.WARNING(
                        f'Translating {lessons.count()} lessons without Dari content...'
                    )
                )

            translated_count = 0
            skipped_count = 0

            for lesson in lessons:
                if self.translate_lesson(lesson, force):
                    translated_count += 1
                else:
                    skipped_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Translation complete!\n'
                    f'  Translated: {translated_count}\n'
                    f'  Skipped: {skipped_count}'
                )
            )

    def translate_lesson(self, lesson, force=False):
        """Translate a single lesson"""
        if not force and lesson.content_dari and lesson.content_dari.strip():
            logger.info(f'Skipping lesson "{lesson.title}" - Dari content already exists')
            return False

        self.stdout.write(f'Translating: {lesson.title}...', ending=' ')

        try:
            translated = translate_english_to_dari(lesson.content_english)

            if translated and translated.strip() and translated != lesson.content_english:
                lesson.content_dari = translated
                lesson.save()
                self.stdout.write(self.style.SUCCESS('✓ Done'))
                return True
            else:
                # Use English as fallback
                lesson.content_dari = lesson.content_english
                lesson.save()
                self.stdout.write(self.style.WARNING('⚠ Using English fallback'))
                return True

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
            logger.error(f'Translation error for lesson {lesson.id}: {str(e)}')
            return False
