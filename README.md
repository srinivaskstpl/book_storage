# Book Storage Django Project

This Django project is designed to manage books in different bookshops. It provides a RESTful API for storing and retrieving information about books, authors, and storing history.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/srinivaskstpl/book_storage.git
    cd book_storage
    ```

2. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Apply migrations:

    ```bash
    python manage.py migrate
    ```

4. Run the development server:

    ```bash
    python manage.py runserver
    ```

The server will be running at http://localhost:8000/ by default.

## Docker setup

1. Build Docker:

    ```bash
    docker build -t <your-image-name> .
    ```

4. Run docker container:

    ```bash
    docker run -p 8000:8000 -d <your-image-name>
    ```

## Running Tests

To run the test cases, use the following command:

```bash
python manage.py test


## Postman collection

    ```bash
    You can find postman collection JSON - Book_store.postman_collection.json
    ```