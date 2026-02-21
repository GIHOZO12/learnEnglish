from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from courses.models import CourseEnrollment

User = get_user_model()


class Command(BaseCommand):
    help = 'Update user course progress for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            'user_id',
            type=int,
            help='User ID to update'
        )
        parser.add_argument(
            'progress',
            type=int,
            help='Progress percentage (0-100)'
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        progress = options['progress']

        try:
            user = User.objects.get(id=user_id)
            enrollments = user.course_enrollments.all()

            if not enrollments.exists():
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} has no course enrollments')
                )
                return

            for enrollment in enrollments:
                enrollment.update_progress(progress)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Updated {user.username} - {enrollment.course.title}: {progress}%'
                    )
                )

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
