from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Отправка тестового email для проверки настроек'

    def add_arguments(self, parser):
        parser.add_argument('--to', type=str, help='nikitach.mk.09.04@gmail.com', default='')
    
    def handle(self, *args, **options):
        to_email = options['to'] or settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(
                subject='Тестовое письмо с English Studying Platform',
                message='Поздравляем! Настройки email работают корректно.\n\n'
                       f'Отправитель: {settings.DEFAULT_FROM_EMAIL}\n'
                       f'Получатель: {to_email}\n'
                       f'Хост: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}\n\n'
                       'Это тестовое письмо от системы восстановления пароля.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'Тестовое письмо отправлено на {to_email}'))
            self.stdout.write(self.style.SUCCESS(f'Отправитель: {settings.DEFAULT_FROM_EMAIL}'))
            self.stdout.write(self.style.SUCCESS(f'Хост: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}'))
            
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.filebased.EmailBackend':
                self.stdout.write(self.style.WARNING(f'Письма сохраняются в: {settings.EMAIL_FILE_PATH}'))
            else:
                self.stdout.write(self.style.SUCCESS('Режим реальной отправки на почту'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка отправки email: {str(e)}'))
            self.stdout.write(self.style.WARNING('Проверьте настройки в .env файле:'))
            self.stdout.write(f'EMAIL_HOST_USER={settings.EMAIL_HOST_USER}')
            self.stdout.write(f'EMAIL_HOST_PASSWORD={"*" * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else "НЕ ЗАДАН"}')