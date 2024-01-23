# api/serializers.py
from rest_framework import serializers
from .models import Author, Book, Storing


class CreateAuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Author instances.

    Overrides to_representation method to exclude author's birth_date.
    """

    class Meta:
        model = Author
        fields = "__all__"

    def to_representation(self, instance):
        """
        Override to exclude author's birth_date from the representation.

        Args:
            instance: The Author instance.

        Returns:
            dict: The serialized representation of the Author instance.
        """
        representation = super().to_representation(instance)
        representation.pop("birth_date")
        return representation


class GetAuthorDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving specific details of Author instances.
    """

    class Meta:
        model = Author
        fields = ["name", "birth_date"]


class CreateBookSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Book instances.
    """

    class Meta:
        model = Book
        fields = "__all__"


class BookDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed information about Book instances.

    Includes nested representation of the author.
    """

    author = GetAuthorDetailsSerializer()
    quantity = serializers.SerializerMethodField(required=False)
    class Meta:
        model = Book
        fields = ["title", "publish_year", "author", "barcode", "quantity"]
    
    def get_quantity(self, instance):
        quantity = instance.books.filter(book_id=instance.id).last()
        return quantity.quantity if quantity is not None else 0



class CreateStorageSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Storing instances.
    """

    class Meta:
        model = Storing
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('id')
        representation.pop('date')
        return representation


class GetHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving the history of Book instances.

    Includes information about the book and its storing history.
    """

    book = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["book", "history"]

    def get_book(self, obj):
        """
        Get the serialized representation of the book.

        Args:
            obj: The Book instance.

        Returns:
            dict: The serialized representation of the book.
        """
        return {"key": obj.id, "title": obj.title}

    def get_history(self, obj):
        """
        Get the serialized representation of the storing history.

        Args:
            obj: The Book instance.

        Returns:
            list: List of dictionaries representing the storing history.
        """
        information_history = obj.books.all().order_by("-date")
        history_list = [
            {"date": entry.date, "quantity": entry.quantity}
            for entry in information_history
        ]
        return history_list
