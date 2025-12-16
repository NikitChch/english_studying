from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import CourseOrder

@receiver(pre_save, sender=CourseOrder)
def update_course_students_on_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = CourseOrder.objects.get(pk=instance.pk)
            
            if old_instance.status != instance.status:
                if instance.status in ['completed', 'cancelled']:
                    if old_instance.status in ['in_progress', 'paid']:
                        if instance.course.current_students > 0:
                            instance.course.current_students -= 1
                            instance.course.save()
                
                elif instance.status in ['in_progress', 'paid']:
                    if old_instance.status in ['completed', 'cancelled']:
                        instance.course.current_students += 1
                        instance.course.save()
        except CourseOrder.DoesNotExist:
            pass

@receiver(post_save, sender=CourseOrder)
def update_course_on_order_creation(sender, instance, created, **kwargs):
    if created:
        if instance.status in ['paid', 'in_progress']:
            instance.course.current_students += 1
            instance.course.save()

@receiver(post_delete, sender=CourseOrder)
def update_course_students_on_delete(sender, instance, **kwargs):
    if instance.status in ['in_progress', 'paid']:
        if instance.course.current_students > 0:
            instance.course.current_students -= 1
            instance.course.save()