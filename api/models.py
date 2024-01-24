from django.db import models
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_birth_date(value):
    if value <= date(1900, 1, 1):
        raise ValidationError(_("Birth date must be greater than 01/01/1900."))


def validate_publish_year(value):
    if not isinstance(value, int) or value <= 1900:
        raise ValidationError(_("Publish year must be an integer greater than 1900."))


class Author(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField(validators=[validate_birth_date])

    class Meta:
        unique_together = (
            "name",
            "birth_date",
        )


class Book(models.Model):
    barcode = models.CharField(max_length=255, blank=True, null=True, unique=True)
    title = models.CharField(max_length=255, null=False, blank=False)
    publish_year = models.PositiveIntegerField(validators=[validate_publish_year])
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class BooksLeftOver(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="books")
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)


class Storing(models.Model):
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="store_history"
    )
    quantity = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
