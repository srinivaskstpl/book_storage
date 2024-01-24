import pandas as pd

from django.forms import ValidationError
from rest_framework import serializers
from .models import Author, Book, BooksLeftOver, Storing


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
        quantity = instance.store_history.filter(book_id=instance.id).last()
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
        representation.pop("id")
        representation.pop("date")
        return representation


class GetHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving the history of Book instances.

    Includes information about the book and its storing history.
    """

    book = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()
    start_balance = serializers.SerializerMethodField()
    end_balance = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ["book", "start_balance", "end_balance", "history"]

    def get_book(self, obj):
        """
        Get the serialized representation of the book.

        Args:
            obj: The Book instance.

        Returns:
            dict: The serialized representation of the book.
        """
        return {"key": obj.id, "title": obj.title}

    def get_start_balance(self, obj):
        return obj.store_history.first().quantity

    def get_end_balance(self, obj):
        return obj.store_history.latest("id").quantity

    def get_history(self, obj):
        """
        Get the serialized representation of the storing history.

        Args:
            obj: The Book instance.

        Returns:
            list: List of dictionaries representing the storing history.
        """
        information_history = obj.store_history.all().order_by("-date")
        history_list = [
            {"date": entry.date, "quantity": entry.quantity}
            for entry in information_history
        ]
        return history_list


class CreateBooksLeftOverSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Book instances.
    """

    class Meta:
        model = BooksLeftOver
        fields = "__all__"


class BulkCreateStorageSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        file_extension = value.name.split(".")[-1].lower()

        if file_extension not in ["xlsx", "txt"]:
            raise serializers.ValidationError(
                "Invalid file format. Only Excel (.xlsx) or text (.txt) files are allowed."
            )

        return value

    def save(self, **kwargs):
        uploaded_file = self.validated_data["file"]
        file_extension = uploaded_file.name.split(".")[-1].lower()

        if file_extension == "xlsx":
            self.handle_excel(uploaded_file)
        else:
            self.handle_text(uploaded_file)

        return {"success": "Data uploaded successfully"}

    def handle_excel(self, file):
        try:
            df = pd.read_excel(file)
            df["is_null"] = df["quantity"].isnull()

        except Exception as e:
            raise serializers.ValidationError(f"Error reading Excel file: {str(e)}")

        errors = []  # List to store validation errors

        for index, row in df.iterrows():
            barcode, quantity, is_null = (
                row.get("barcode", ""),
                row.get("quantity", ""),
                row.get("is_null"),
            )

            if not barcode:
                continue

            try:
                if is_null:
                    errors.append(
                        f"Error at row {index + 2}. Quantity cannot be blank."
                    )
                else:
                    quantity = int(quantity)
                    book_obj = Book.objects.get(barcode=barcode)

                    if not book_obj:
                        errors.append(
                            f"Error at row {index + 2}. Book with barcode: {barcode} does not exist"
                        )
                    else:
                        Storing.objects.create(book=book_obj, quantity=quantity)

            except ValueError:
                errors.append(
                    f"Invalid quantity at row {index + 2}. Quantity must be a number."
                )

        self.handle_errors(errors)

    def handle_text(self, file):
        errors = []  # List to store validation errors

        lines = file.readlines()

        for line_number, line_bytes in enumerate(lines):
            line = line_bytes.strip()

            if line.startswith(b"BRC"):
                barcode = line[3:].decode("utf-8")

                if line_number + 1 < len(lines):
                    quantity_line_bytes = lines[line_number + 1]
                    quantity_line = quantity_line_bytes.strip()
                else:
                    errors.append(
                        f"Missing quantity line for barcode at line {line_number + 1}."
                    )
                    continue

                if not quantity_line.startswith(b"QNT"):
                    errors.append(f"Missing quantity at line {line_number + 2}.")
                    continue

                quantity = quantity_line[3:].decode("utf-8")
                self.process_text_line(barcode, quantity, line_number, errors)

        self.handle_errors(errors)

    def process_text_line(self, barcode, quantity, line_number, errors):
        if not barcode:
            return

        try:
            book_obj = Book.objects.get(barcode=barcode)
        except Book.DoesNotExist:
            errors.append(
                f"Book with barcode '{barcode}' not found at line {line_number + 1}."
            )
            return

        try:
            quantity = int(quantity)
            Storing.objects.create(book=book_obj, quantity=quantity)
        except ValueError:
            errors.append(
                f"Invalid quantity at line {line_number + 2}. Quantity must be a number."
            )
        except Exception as e:
            errors.append(f"Error saving data at line {line_number + 1}: {str(e)}")

    def handle_errors(self, errors):
        if errors:
            raise serializers.ValidationError({"non_field_errors": errors})
