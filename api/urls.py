from django.urls import path
from .views import (
    AuthorDetailView,
    BookDetailView,
    BookRetrieveAPIView,
    BulkCreateStorageView,
    StoringHistoryView,
    GetAuthorDetailView,
    BooksLeftOverView,
    ping_view,
)

urlpatterns = [
    path("ping/", ping_view, name="ping"),
    path("author/<int:pk>/", GetAuthorDetailView.as_view(), name="author-detail"),
    path("author/", AuthorDetailView.as_view()),
    path("book/<int:pk>/", BookRetrieveAPIView.as_view(), name="book-detail"),
    path("book/", BookDetailView.as_view(), name="book-create-search"),
    path("history/<int:pk>/", StoringHistoryView.as_view(), name="storing-history"),
    path("leftover/add", BooksLeftOverView.as_view(), name="add-leftover"),
    path("leftover/remove", BooksLeftOverView.as_view(), name="remove-leftover"),
    path("leftover/bulk", BulkCreateStorageView.as_view(), name="bulk-leftover"),
]
