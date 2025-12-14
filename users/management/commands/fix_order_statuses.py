from django.core.management.base import BaseCommand
from courses.models import CourseOrder
from django.utils import timezone

class Command(BaseCommand):
    help = 'Исправляет статусы заказов курсов'
    
    def handle(self, *args, **options):
        paid_orders = CourseOrder.objects.filter(status='paid')
        
        self.stdout.write(f'Найдено {paid_orders.count()} заказов со статусом "paid"')
        
        updated_count = 0
        for order in paid_orders:
            order.status = 'in_progress'
            order.save()
            updated_count += 1
            self.stdout.write(f'  Заказ #{order.id}: статус изменен на "in_progress"')
        
        self.stdout.write(self.style.SUCCESS(f'\nОбновлено {updated_count} заказов!'))
        
        self.stdout.write('\nТекущие заказы пользователя Oleg:')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            user = User.objects.get(username='Oleg')
            user_orders = CourseOrder.objects.filter(student=user)
            for order in user_orders:
                self.stdout.write(f'  Заказ #{order.id}: {order.course.name} - статус: {order.status}, прогресс: {order.progress}%')
        except User.DoesNotExist:
            self.stdout.write('Пользователь Oleg не найден')