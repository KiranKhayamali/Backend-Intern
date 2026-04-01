from fastapi import FastAPI, Request 
from pydantic import BaseModel

app = FastAPI() 

book_db = [
    {"id": 1, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "published_year": 1925, "genre": "Novel", "summary": "A story about the mysterious millionaire Jay Gatsby and his obsession with Daisy Buchanan.", "rating": 4.5},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "published_year": 1960, "genre": "Novel", "summary": "A gripping tale of racial injustice and childhood innocence in the American South.", "rating": 4.8},
    {"id": 3, "title": "1984", "author": "George Orwell", "published_year": 1948, "genre": "Dystopian Fiction", "summary": "A dystopian social science fiction novel and cautionary tale about totalitarian control.", "rating": 4.6},
    {"id": 4, "title": "Pride and Prejudice", "author": "Jane Austen", "published_year": 1813, "genre": "Romance", "summary": "A romantic novel of manners that critiques the British landed gentry at the end of the 18th century.", "rating": 4.7},
    {"id": 5, "title": "The Catcher in the Rye", "author": "J.D. Salinger", "published_year": 1951, "genre": "Fiction", "summary": "A controversial novel that has been subject to bans and challenges since its publication.", "rating": 4.2},
    {"id": 6, "title": "The Lord of the Rings", "author": "J.R.R. Tolkien", "published_year": 1954, "genre": "Fantasy", "summary": "An epic high fantasy adventure set in the fictional world of Middle-earth.", "rating": 4.9},
    {"id": 7, "title": "The Hobbit", "author": "J.R.R. Tolkien", "published_year": 1937, "genre": "Fantasy", "summary": "A fantasy novel and children's book by English author J.R.R. Tolkien.", "rating": 4.8},
    {"id": 8, "title": "Fahrenheit 451", "author": "Ray Bradbury", "published_year": 1953, "genre": "Dystopian Fiction", "summary": "A dystopian novel about a future American society where books are banned.", "rating": 4.5},
    {"id": 9, "title": "Mockingbird", "author": "Harper Lee", "published_year": 1960, "genre": "Novel", "summary": "A gripping tale of racial injustice and childhood innocence in the American South.", "rating": 4.8},
    {"id": 10, "title": "The Alchemist", "author": "Paulo Coelho", "published_year": 1988, "genre": "Adventure", "summary": "A novel that follows a young Andalusian shepherd on his journey to the Egyptian pyramids.", "rating": 4.6},
    {"id": 11, "title": "The Da Vinci Code", "author": "Dan Brown", "published_year": 2003, "genre": "Thriller", "summary": "A mystery thriller novel that follows symbologist Robert Langdon and cryptologist Sophie Neveu.", "rating": 4.3},
    {"id": 12, "title": "The Hunger Games", "author": "Suzanne Collins", "published_year": 2008, "genre": "Dystopian Fiction", "summary": "A dystopian novel set in a future where the totalitarian nation of Panem is divided into 12 districts.", "rating": 4.7},
    {"id": 13,("id"): 13,("title"):("The Chronicles of Narnia"),("author"):("C.S. Lewis"),("published_year"): 1950,("genre"):("Fantasy"),("summary"):("A series of seven fantasy novels that are considered classics of children's literature."),("rating"): 4.8},
    {"id": 14,("title"):("The Shining"),("author"):("Stephen King"),("published_year"): 1977,("genre"):("Horror"),("summary"):("A horror novel about a family that becomes isolated in a haunted hotel."),("rating"): 4.5},
    {"id": 15,("title"):("The Thousand Splendid Suns"),("author"):("Khaled Hosseini"),("published_year"): 2007,("genre"):("Historical Fiction"),("summary"):("A novel that tells the story of two Afghan women under the Taliban regime."),("rating"): 4.6}
]

class Book(BaseModel):
    id: int | None = None
    title: str
    author: str
    published_year: int
    genre: str
    summary: str | None = None
    rating: float | None = None


@app.get("/")
def read_root():
    return {"message": "Hello, Reader!"}

@app.get("/books")
def read_books(skip: int = 0, limit: int = 5):
    return book_db[skip: skip + limit]

@app.get("/books/search")
def search_books(q: str | None = None):
    if not q:
        return {"message": "No search query provided"}
    q_lower = q.lower()
    result = [book for book in book_db if q_lower in book["title"].lower() or q_lower in book["author"].lower()]
    if result:
        return result
    return {"message": "No books found matching the query."}

@app.get("/books/rating")
def filter_books_by_rating(q: float | None = None):
    if not q:
        return {"message": "No rating query provided"}
    result = [book for book in book_db if book["rating"] >= q]
    if result:
        return result
    return {"message": "No books found with rating greater than or equal to the query."}

@app.get("/books/{book_id}")
def read_book(book_id: int):
    for book in book_db:
        if book["id"] ==book_id:
            return book
    return {"message": "Book not found"}


# #Post Request before Validation 
# @app.post("/books/")
# async def create_book(request: Request):
#     book_data = await request.json()
#     print("Received book data: ", book_data)
#     book_data["id"] = len(book_db) + 1
#     book_db.append(book_data)
#     return book_data


@app.post("/books/")
async def create_book(book: Book):
    new_book = book.model_dump()
    new_book["id"] = len(book_db) + 1
    book_db.append(new_book)
    return new_book

@app.put("/books/{book_id}")
async def update_book(book_id: int, book: Book): 
    updated_book = book.model_dump() 
    updated_book["id"] = book_id 
    book_db[book_id - 1] = updated_book
    return updated_book

@app.delete("/books/{book_id}")
def remove_book(book_id: int):
    for book in book_db:
        if book["id"] == book_id :
            book_db.remove(book)
            # return {"message": f"{book_id} has been removed from the database"}
            return book_db
    return {"message": "No book found to delete in the id."}

