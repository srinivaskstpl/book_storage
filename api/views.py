from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from rest_framework.views import APIView

from .models import Author, Book, BooksLeftOver
from .serializers import (
    CreateBooksLeftOverSerializer,
    GetAuthorDetailsSerializer,
    BookDetailsSerializer,
    GetHistorySerializer,
    CreateBookSerializer,
    CreateStorageSerializer,
)

from .signals import create_storing_entry
from api.utils import handle_excel, handle_text


def ping_view(request):
    return JsonResponse({"message": "success"})


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
            queryset = queryset.filter(barcode__icontains=barcode).order_by("barcode")
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
        return Book.objects.filter(id=self.kwargs.get("pk"))


class BooksLeftOverView(APIView):
    """
    View to list and create Storing history for a specific Book instance.
    """

    def post(self, request):
        barcode = request.data.get("barcode")
        quantity = request.data.get("quantity")

        if not barcode or not isinstance(quantity, int):
            return Response(
                {"error": "Invalid input data."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Get the book or return a 404 response if it doesn't exist
        book = get_object_or_404(Book, barcode=barcode)

        # Get or create BooksLeftOver instance for the book
        leftover, created = BooksLeftOver.objects.get_or_create(
            book=book, defaults={"quantity": 0}
        )

        # Update quantity based on the URL name
        if self.request.resolver_match.url_name == "add-leftover":
            leftover.quantity += int(quantity)
        elif self.request.resolver_match.url_name == "remove-leftover":
            leftover.quantity -= int(quantity)

        leftover.save()
        serializer = CreateBooksLeftOverSerializer(leftover, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class BulkCreateStorageView(APIView):
    def post(self, request):
        if "file" in request.data.keys():
            file = request.data["file"]
            file_extension = file.name.split(".")[-1].lower()

            if file_extension not in ["xlsx", "txt"]:
                return Response(
                    {
                        "error": "Invalid file format. Only Excel (.xlsx) or text (.txt) files are allowed."
                    }
                )
            file_extension = file.name.split(".")[-1].lower()

            if file_extension == "xlsx":
                result = handle_excel(file)
            else:
                result = handle_text(file)

            if result != True:
                return Response(result)

            return Response({"success": "Data uploaded successfully"})
        else:
            return Response({"missing file": "please upload a text/excel file"})
