from database.models import Author, Book
from database.models import SessionLocal, engine


def db_get_books(limit: int):
    """Выводим последние добавленные в библиотеку книги."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        books = db.query(Book).all()
        return books[-limit:]


def db_new_book_add(author_id: int, book_title: str, description: str):
    """Добавляем новую книгу в библиотеку."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        new_book = Book(
            author_id=author_id,
            book_title=book_title,
            description=description,
        )
        db.add(new_book)
        db.commit()
        book = db.query(Book).filter(Book.book_title == book_title).first()
    return book


def db_change_author_book(id: int, new_autor_id: int):
    """Меняем автора книги по id книги."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        book = db.get(Book, id)
        book.author_id = new_autor_id
        db.commit()
        book = db.query(Book).filter(Book.id == id).first()
    return book


def db_delete_book(id: int):
    """Удаляем книгу по id книги."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        book = db.query(Book).filter(Book.id == id).first()
        db.delete(book)
        db.commit()
    return {"status": f"{book.book_title} delete"}


def db_get_authors(limit: int):
    """Выводим последних добавленных авторов."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        author = db.query(Author).all()
    return author[-limit:]


def db_new_authors_add(fio: str, biography: str):
    """Добавляем нового автора."""
    with SessionLocal(autoflush=False, bind=engine) as db:
        new_author = Author(
            fio=fio,
            biography=biography,
        )
        db.add(new_author)
        db.commit()
        author = db.query(Author).filter(Author.fio == fio).first()
    return author
