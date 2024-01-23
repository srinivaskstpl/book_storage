from django.urls import path
from .views import (
    AuthorDetailView,
    BookDetailView,
    BookRetrieveAPIView,
    StoringHistoryView,
    GetAuthorDetailView,
    ping_view,
)

urlpatterns = [
    path('ping/', ping_view, name='ping'),
    path("author/<int:pk>/", GetAuthorDetailView.as_view(), name="author-detail"),
    path("author/", AuthorDetailView.as_view()),
    path("book/<int:pk>/", BookRetrieveAPIView.as_view(), name="book-detail"),
    path("book/", BookDetailView.as_view(), name="book-create-search"),
    path("history/<int:pk>/", StoringHistoryView.as_view(), name="storing-history"),
    path("leftover/", StoringHistoryView.as_view(), name="storing-history"),
]
