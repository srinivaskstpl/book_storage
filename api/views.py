from rest_framework import generics
from .models import Author, Book
from .serializers import (
    GetAuthorDetailsSerializer,
    BookDetailsSerializer,
    GetHistorySerializer,
    CreateBookSerializer,
    CreateStorageSerializer,
)
from rest_framework.response import Response
from rest_framework import status


class AuthorDetailView(generics.ListCreateAPIView):
    """
    View to list and create Author instances.
    """
    queryset = Author.objects.all()
    serializer_class = GetAuthorDetailsSerializer


class GetAuthorDetailView(generics.RetrieveAPIView):
    """
    View to retrieve details of a specific Author instance.
    """
    queryset = Author.objects.all()
    serializer_class = GetAuthorDetailsSerializer


class BookDetailView(generics.ListCreateAPIView):
    """
    View to list and create Book instances with optional barcode filtering.
    """
    queryset = Book.objects.all()
    serializer_class = CreateBookSerializer

    def get_queryset(self):
        """
        Filter the queryset based on the barcode query parameter.
        """
        queryset = Book.objects.all()
        barcode = self.request.query_params.get("barcode")
        if barcode:
            queryset = queryset.filter(barcode__icontains=barcode)
        return queryset

    def get_serializer_class(self):
        """
        Return different serializer class based on the request method.
        """
        if self.request.method == "POST":
            return CreateBookSerializer
        return BookDetailsSerializer

    def list(self, request, *args, **kwargs):
        """
        List view with additional data about found items count.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        # Include found items count in the serialized data
        response_data = {"found": len(serializer.data), "items": serializer.data}

        return Response(response_data, status=status.HTTP_200_OK)


class BookRetrieveAPIView(generics.RetrieveAPIView):
    """
    View to retrieve details of a specific Book instance.
    """
    queryset = Book.objects.all()
    serializer_class = BookDetailsSerializer


class StoringHistoryView(generics.ListCreateAPIView):
    """
    View to list and create Storing history for a specific Book instance.
    """
    queryset = Book.objects.all()

    def get_serializer_class(self):
        """
        Return different serializer class based on the request method.
        """
        if self.request.method == "POST":
            return CreateStorageSerializer
        return GetHistorySerializer

    def get_queryset(self):
        """
        Filter the queryset to include only the Book with the given ID.
        """
        return Book.objects.filter(id=self.kwargs.get('pk'))
