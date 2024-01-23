from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=255)
    birth_date = models.DateField()

    class Meta:
        unique_together = (
            "name",
            "birth_date",
        )


class Book(models.Model):
    barcode = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255)
    publish_year = models.PositiveIntegerField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Storing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
