from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Author, Book, Storing
from django.urls import reverse


class BookshopApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test data for authors
        self.author1 = Author.objects.create(name="Author 1", birth_date="1990-01-01")
        self.author2 = Author.objects.create(name="Author 2", birth_date="1985-05-15")

    def test_add_book(self):
        url = reverse("book-create-search")

        data = {
            "title": "Test Book 1",
            "publish_year": 2020,
            "author": self.author1.pk,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().title, "Test Book 1")

    def test_get_book(self):
        # Create a book
        book = Book.objects.create(
            title="Test Book 2", publish_year=2018, author=self.author2
        )

        url = reverse("book-detail", kwargs={"pk": book.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book 2")

    def test_search_books_by_barcode(self):
        # Create some books
        book1 = Book.objects.create(
            title="Test Book 3", publish_year=2015, author=self.author1, barcode="12345"
        )
        book2 = Book.objects.create(
            title="Test Book 4", publish_year=2019, author=self.author2, barcode="67890"
        )

        url = reverse("book-create-search") + "?barcode=67890"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["found"], 1)
        self.assertEqual(response.data["items"][0]["title"], "Test Book 4")

    def test_invalid_book_creation(self):
        url = reverse("book-create-search")

        data = {
            "title": "Invalid Book",  # Missing required field 'publish_year'
            "author": self.author1.pk,
        }

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
