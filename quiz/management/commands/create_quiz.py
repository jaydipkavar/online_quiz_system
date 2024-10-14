from django.core.management.base import BaseCommand
from quiz.models import Course, Question
from courses_data import courses_data

class Command(BaseCommand):
    help = 'Populate the database with default courses and questions'

    def handle(self, *args, **kwargs):
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                course_name=course_data['course_name'],
                defaults={'question_number': course_data['question_number'], 'total_marks': course_data['total_marks']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created course: {course.course_name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Course already exists: {course.course_name}'))

            for q_data in course_data['questions']:
                Question.objects.get_or_create(
                    course=course,
                    marks=q_data['marks'],
                    question=q_data['question'],
                    option1=q_data['option1'],
                    option2=q_data['option2'],
                    option3=q_data['option3'],
                    option4=q_data['option4'],
                    answer=q_data['answer'],
                    hint=q_data['hint'],
                )
                self.stdout.write(self.style.SUCCESS(f'Created question: "{q_data["question"]}" for course: "{course.course_name}"'))
