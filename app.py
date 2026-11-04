# ********************************************************************
## app.py       Author: Llewellyn (Cassie) VanDelinder
## Module 3: Assignment 1
# A tiny REST API for a book list. Demonstrates CRUD endpoints and an HTML page: table, error handling, and a loading spinner
# ********************************************************************

from flask import Flask, jsonify
from flask import Flask, request, jsonify

# -- BOOKS LIST LOADED IN MEMORY, CHANGES RESET WHEN SERVER RESTARTS --
books = [
    {"id": 1, "title": "1984", "author": "George Orwell", "rating": 4.9},
    {"id": 2, "title": "Brave New World", "author": "Aldous Huxley", "rating": 4.3},
    {"id": 3, "title": "Fahrenheit 451", "author": "Ray Bradbury", "rating": 4.7},
    {"id": 4, "title": "Ready Player One", "author": "Ernest Cline", "rating": 3.9},
]

app = Flask(__name__)


@app.route("/")
def welcome():
    return jsonify(message="Welcome to Tiny REST App!")


# -- RETURNS EVERY BOOK --
@app.route("/goodbooks", methods=["GET"])
def get_books():
    return jsonify(books)


from flask import abort


# -- RETURNS BOOK FOR ID, OR 404 IF DOESN'T EXIST --
@app.route("/goodbooks/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        abort(404, description="Book not found")
    return jsonify(book)


from flask import request


# -- ADDS A NEW BOOK TO MEMORY, CHANGES RESET WHEN SERVER RESTARTS --
@app.route("/goodbooks", methods=["POST"])
def add_book():
    data = request.get_json()
    if not data or "title" not in data or "author" not in data:
        abort(400, description="Missing required fields")
    new_id = max(b["id"] for b in books) + 1 if books else 1
    book = {
        "id": new_id,
        "title": data["title"],
        "author": data["author"],
        "rating": data.get("rating", 0),
    }
    books.append(book)
    return jsonify(book), 201


# -- MODIFIES VALUE(S) FOR A BOOK IN MEMORY, CHANGES RESET WHEN SERVER RESTARTS --
@app.route("/goodbooks/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        abort(404, description="Book not found")
    book.update({k: v for k, v in data.items() if k in ["title", "author", "rating"]})
    return jsonify(book)


# -- DELETES A BOOK FROM MEMORY, CHANGES RESET WHEN SERVER RESTARTS --
@app.route("/goodbooks/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    global books
    if not any(b["id"] == book_id for b in books):
        abort(404, description="Book not found")
    books = [b for b in books if b["id"] != book_id]
    return "", 204


from flask import render_template_string


TABLE_TEMPLATE = """
<!doctype html>
<title>Book List</title>
<style>

/* LOADING SPINNER, code from https://www.w3schools.com/howto/howto_css_loader.asp */
.loader {
  border: 16px solid #f3f3f3; /* Light grey */
  border-top: 16px solid #3498db; /* Blue */
  border-radius: 50%;
  width: 120px;
  height: 120px;
  animation: spin 2s linear infinite;
  margin-bottom: 20px;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>

<h1>Books</h1>
<div id="loader" class="loader"></div>

<!-- Empty placeholders for the error message and table, filled by the script -->
<p id="error" hidden>Could not load the books. Is the server running?</p>
<table border=1 cellpadding=5 cellspacing=0>
<thead><tr><th>ID</th><th>Title</th><th>Author</th><th>Rating</th></tr></thead>
<tbody id="rows"></tbody>
</table>


<script>
// Assign references to elements the script updates
const spinner = document.getElementById('loader');
const err_empty = document.getElementById('error');
const booktable = document.getElementById('rows');

// Set a brief timeout to demonstrate the loading spinner
setTimeout(() => {


// sends a GET request to /goodbooks 
fetch('/goodbooks')
    .then(response => {

// The server responded, but not with a success response (outside 200-299) - passes error to .catch and skips this section of the chain
    if (!response.ok) {
        throw new Error('Unable to load books.');
    }

// Parse the JSON response into a list of books
    return response.json();
    })
    .then (books => {

// Populate table and shade if book rating is greater than/equal to 4
books.forEach(book => {
    const row = `<tr style="background-color: ${book.rating >= 4 ? 'lightgreen' : 'white'}">
        <td>${book.id}</td>
        <td>${book.title}</td>
        <td>${book.author}</td>
        <td>${book.rating}</td>
    </tr>`
    booktable.innerHTML += row;
});

// Hide the spinner because books have been found
    spinner.hidden = true;
})

// Catches any failure above: hides the spinner, shows the error message, logs the details
    .catch(error => {
    spinner.hidden = true;  //hides the spinner
    err_empty.hidden = false;   //shows the on-page error message
    console.error(error.message);  // logs the error details to the developer console
    });
},2000);  //closing of the timeout wrapper. 2000=2 seconds
</script>
"""


# HTML Request and response for the books list: Example: http://127.0.0.1:5000/goodbooks/html
@app.route("/goodbooks/html")
def books_html():
    return render_template_string(TABLE_TEMPLATE)


# Starts the FLASK server
if __name__ == "__main__":
    app.run(debug=True)
