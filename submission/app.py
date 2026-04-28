from flask import Flask, render_template, request, redirect, url_for
from mongita import MongitaClientDisk
import json
import os

app = Flask(__name__)

# ------------------------------------------
# Mongita Setup (local embedded NoSQL DB)
# ------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
client = MongitaClientDisk(os.path.join(BASE_DIR, "mongita_data"))

db = client.bookstore
categories_col = db.categories
books_col = db.books

DEFAULT_CATEGORIES = [
    {"id": 1, "name": "Biographies"},
    {"id": 2, "name": "Learn to Play"},
    {"id": 3, "name": "Music Theory"},
    {"id": 4, "name": "Scores and Charts"}
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
        "readNow": 0
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
        "readNow": 1
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
        "readNow": 1
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
        "readNow": 0
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
        "readNow": 1
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
        "readNow": 0
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
        "readNow": 1
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
        "readNow": 0
    }
]


# ------------------------------------------
# Helper Functions
# ------------------------------------------
def clean_document(document):
    if not document:
        return None

    return {key: value for key, value in document.items() if key != "_id"}


def export_json_files():
    categories = [clean_document(category) for category in categories_col.find()]
    books = [clean_document(book) for book in books_col.find()]

    categories = sorted(categories, key=lambda c: c["id"])
    books = sorted(books, key=lambda b: b["id"])

    with open(os.path.join(BASE_DIR, "categories.json"), "w", encoding="utf-8") as file:
        json.dump(categories, file, indent=2)

    with open(os.path.join(BASE_DIR, "books.json"), "w", encoding="utf-8") as file:
        json.dump(books, file, indent=2)


def ensure_seed_data():
    if not list(categories_col.find()):
        categories_col.insert_many(DEFAULT_CATEGORIES)

    if not list(books_col.find()):
        books_col.insert_many(DEFAULT_BOOKS)

    export_json_files()


def get_categories():
    categories = [clean_document(category) for category in categories_col.find()]
    return sorted(categories, key=lambda c: c["name"])


def get_books(category_id=None):
    query = {}

    if category_id is not None:
        query["categoryId"] = category_id

    books = [clean_document(book) for book in books_col.find(query)]
    return sorted(books, key=lambda b: b["title"])


def get_book(book_id):
    return clean_document(books_col.find_one({"id": book_id}))


def get_next_book_id():
    books = get_books()

    if not books:
        return 1

    return max(book["id"] for book in books) + 1


def build_book_data(form_data):
    title = form_data.get("title", "").strip()
    author = form_data.get("author", "").strip()
    isbn = form_data.get("isbn", "").strip()
    price = form_data.get("price", type=float)
    image = form_data.get("image", "").strip()
    category_id = form_data.get("categoryId", type=int)
    read_now = form_data.get("readNow", type=int)

    selected_category = categories_col.find_one({"id": category_id})
    selected_category = clean_document(selected_category)

    if not title or not author or not isbn or not image:
        raise ValueError("Please fill in all fields.")

    if price is None or price < 0:
        raise ValueError("Please enter a valid price.")

    if not selected_category:
        raise ValueError("Please choose a valid category.")

    if read_now not in (0, 1):
        raise ValueError("Read Now must be 0 or 1.")

    return {
        "categoryId": category_id,
        "categoryName": selected_category["name"],
        "title": title,
        "author": author,
        "isbn": isbn,
        "price": round(price, 2),
        "image": image,
        "readNow": read_now
    }


ensure_seed_data()


# ------------------------------------------
# HOME PAGE
# ------------------------------------------
@app.route("/", methods=["GET"])
def home():
    categories = get_categories()
    return render_template("index.html", categories=categories)


# ------------------------------------------
# READ ALL BOOKS PAGE
# ------------------------------------------
@app.route("/read", methods=["GET"])
def read():
    category_id = request.args.get("categoryId", type=int)

    categories = get_categories()
    selected_category = None

    if category_id is not None:
        selected_category = categories_col.find_one({"id": category_id})
        selected_category = clean_document(selected_category)

    books = get_books(category_id if selected_category else None)

    return render_template(
        "read.html",
        categories=categories,
        selectedCategory=selected_category,
        books=books
    )


# ------------------------------------------
# CREATE BOOK FORM
# ------------------------------------------
@app.route("/create", methods=["GET"])
def create():
    categories = get_categories()
    return render_template("create.html", categories=categories, book=None, error=None)


# ------------------------------------------
# CREATE BOOK POST
# ------------------------------------------
@app.route("/create_post", methods=["POST"])
def create_post():
    categories = get_categories()

    try:
        new_book = build_book_data(request.form)
        new_book["id"] = get_next_book_id()
        books_col.insert_one(new_book)
        export_json_files()
        return redirect(url_for("read"))
    except ValueError as error:
        return render_template(
            "create.html",
            categories=categories,
            book=request.form,
            error=str(error)
        ), 400


# ------------------------------------------
# EDIT BOOK FORM
# ------------------------------------------
@app.route("/edit/<int:book_id>", methods=["GET"])
def edit(book_id):
    categories = get_categories()
    book = get_book(book_id)

    if not book:
        return render_template("error.html", error="Book not found."), 404

    return render_template("edit.html", categories=categories, book=book, error=None)


# ------------------------------------------
# EDIT BOOK POST
# ------------------------------------------
@app.route("/edit_post/<int:book_id>", methods=["POST"])
def edit_post(book_id):
    categories = get_categories()
    book = get_book(book_id)

    if not book:
        return render_template("error.html", error="Book not found."), 404

    try:
        updated_book = build_book_data(request.form)
        books_col.update_one({"id": book_id}, {"$set": updated_book})
        export_json_files()
        return redirect(url_for("read"))
    except ValueError as error:
        form_book = request.form.to_dict()
        form_book["id"] = book_id
        return render_template(
            "edit.html",
            categories=categories,
            book=form_book,
            error=str(error)
        ), 400


# ------------------------------------------
# DELETE BOOK
# ------------------------------------------
@app.route("/delete/<int:book_id>", methods=["GET"])
def delete(book_id):
    result = books_col.delete_one({"id": book_id})

    if result.deleted_count == 0:
        return render_template("error.html", error="Book not found."), 404

    export_json_files()
    return redirect(url_for("read"))


# ------------------------------------------
# ERRORS
# ------------------------------------------
@app.errorhandler(Exception)
def handle_error(e):
    return render_template("error.html", error=e), 500


# ------------------------------------------
# RUN APP
# ------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
