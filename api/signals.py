from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import BooksLeftOver, Storing


@receiver(pre_save, sender=BooksLeftOver)
def create_storing_entry(sender, instance, **kwargs):
    """
    Signal to create a Storing entry when a BooksLeftOver entry is created.
    """
    # update history
    prev_instance = BooksLeftOver.objects.get(id=instance.id)
    if prev_instance.quantity < instance.quantity:
        quantity = instance.quantity - prev_instance.quantity
    else:
        quantity = -abs(prev_instance.quantity - instance.quantity)

    Storing.objects.create(book=instance.book, quantity=quantity)
