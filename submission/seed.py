from mongita import MongitaClientDisk
import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "mongita_data")
client = MongitaClientDisk(DATA_DIR)
db = client.bookstore

categories_col = db.categories
books_col = db.books


DEFAULT_CATEGORIES = [
    {"id": 1, "name": "Biographies"},
    {"id": 2, "name": "Learn to Play"},
    {"id": 3, "name": "Music Theory"},
    {"id": 4, "name": "Scores and Charts"},
]

DEFAULT_BOOKS = [
    {
        "id": 1,
        "categoryId": 1,
        "categoryName": "Biographies",
        "title": "Beethoven",
        "author": "David Jacobs",
        "isbn": "13-9780304936588",
        "price": 9.99,
        "image": "beethoven.gif",
        "readNow": 0,
    },
    {
        "id": 2,
        "categoryId": 1,
        "categoryName": "Biographies",
        "title": "Madonna",
        "author": "Andrew Morton",
        "isbn": "13-9780312287863",
        "price": 12.99,
        "image": "madonna.jpg",
        "readNow": 1,
    },
    {
        "id": 3,
        "categoryId": 1,
        "categoryName": "Biographies",
        "title": "Clapton: The Autobiography",
        "author": "Eric Clapton",
        "isbn": "13-9780767925365",
        "price": 10.99,
        "image": "clapton.jpg",
        "readNow": 1,
    },
    {
        "id": 4,
        "categoryId": 1,
        "categoryName": "Biographies",
        "title": "Music is My Mistress",
        "author": "Edward Kennedy Ellington",
        "isbn": "13-9780303608037",
        "price": 68.99,
        "image": "ellington.jpg",
        "readNow": 0,
    },
    {
        "id": 5,
        "categoryId": 2,
        "categoryName": "Learn to Play",
        "title": "Play Piano Today!",
        "author": "Hal Leonard",
        "isbn": "13-9780634069321",
        "price": 19.99,
        "image": "piano.jpg",
        "readNow": 1,
    },
    {
        "id": 6,
        "categoryId": 2,
        "categoryName": "Learn to Play",
        "title": "Guitar Basics",
        "author": "James Longworth",
        "isbn": "13-9780571538163",
        "price": 14.99,
        "image": "guitar.jpg",
        "readNow": 0,
    },
    {
        "id": 7,
        "categoryId": 3,
        "categoryName": "Music Theory",
        "title": "Music Theory Essentials",
        "author": "Jason W. Solomon",
        "isbn": "13-9781423492724",
        "price": 21.95,
        "image": "theory.jpg",
        "readNow": 1,
    },
    {
        "id": 8,
        "categoryId": 4,
        "categoryName": "Scores and Charts",
        "title": "Classical Favorites",
        "author": "Various",
        "isbn": "13-9780793512737",
        "price": 15.99,
        "image": "scores.jpg",
        "readNow": 0,
    },
]


def clean_document(document):
    return {key: value for key, value in document.items() if key != "_id"}


def export_collections():
    with open(os.path.join(BASE_DIR, "categories.json"), "w", encoding="utf-8") as file:
        json.dump(
            sorted(
                [clean_document(category) for category in categories_col.find()],
                key=lambda category: category["id"],
            ),
            file,
            indent=2,
        )

    with open(os.path.join(BASE_DIR, "books.json"), "w", encoding="utf-8") as file:
        json.dump(
            sorted(
                [clean_document(book) for book in books_col.find()],
                key=lambda book: book["id"],
            ),
            file,
            indent=2,
        )


categories_col.delete_many({})
books_col.delete_many({})

categories_col.insert_many(DEFAULT_CATEGORIES)
books_col.insert_many(DEFAULT_BOOKS)
export_collections()

print("Bookstore Mongita DB created.")
