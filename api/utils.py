from api.models import Book, Storing
import pandas as pd


def handle_excel(file):
    try:
        df = pd.read_excel(file)
        df["is_null"] = df["quantity"].isnull()

    except Exception as e:
        raise e

    errors = []  # List to store validation errors
    store_list = []
    for index, row in df.iterrows():
        barcode = row.get("barcode", "")
        quantity = row.get("quantity", "")
        is_null = row.get("is_null")
        if not barcode:
            continue

        try:
            if is_null:
                errors.append(f"Error at row {index + 2}. Quantity cannot be blank.")
            else:
                quantity = int(quantity)
                book_obj = Book.objects.filter(barcode=barcode)
                if not book_obj.exists():
                    errors.append(
                        f"Error at row {index + 2}. Book with barcode: {barcode} does not exist"
                    )
                else:
                    store_list.append(Storing(book=book_obj.first(), quantity=quantity))

        except ValueError:
            errors.append(
                f"Invalid quantity at row {index + 2}. Quantity must be a number."
            )
    if store_list:
        Storing.objects.bulk_create(store_list)
    if errors:
        return errors
    else:
        return True


def handle_text(file):
    errors = []  # List to store validation errors

    # Read lines from the file
    lines = file.readlines()
    store_list = []

    for line_number, line_bytes in enumerate(lines):
        line = line_bytes.strip()

        if line.startswith(b"BRC"):
            barcode = line[3:]
            barcode = barcode.decode("utf-8")
            # Check if there is a quantity line following the barcode
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

            quantity = quantity_line[3:]

            # Validate and save the data
            if not barcode:
                continue

            try:
                book_obj = Book.objects.filter(barcode=barcode)
            except Book.DoesNotExist:
                errors.append(
                    f"Book with barcode '{barcode}' not found at line {line_number + 1}."
                )
                continue
            try:
                quantity = int(quantity)
            except ValueError:
                errors.append(
                    f"Invalid quantity at line {line_number + 2}. Quantity must be a number."
                )
                continue

            try:
                store_list.append(Storing(book=book_obj.first(), quantity=quantity))
            except Exception as e:
                errors.append(f"Error saving data at line {line_number + 1}: {str(e)}")
    if store_list:
        Storing.objects.bulk_create(store_list)
    if errors:
        return errors
    else:
        return True
