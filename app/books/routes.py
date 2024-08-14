from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models import Book
from app.books import bp
from app.forms import BookForm

@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            isbn=form.isbn.data,
            title=form.title.data,
            author=form.author.data,
            length=form.length.data,
            format=form.format.data,
            contributor=current_user
        )
        db.session.add(book)
        db.session.commit()
        flash('Book added successfully!')
        return redirect(url_for('books.book_list'))
    return render_template('books/add_book.html', title='Add Book', form=form)

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_book(id):
    book = Book.query.get_or_404(id)
    if book.contributor != current_user:
        abort(403)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book updated successfully!')
        return redirect(url_for('books.book_list'))
    return render_template('books/edit_book.html', title='Edit Book', form=form, book=book)

@bp.route('/delete/<int:id>')
@login_required
def delete_book(id):
    book = Book.query.get_or_404(id)
    if book.contributor != current_user:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!')
    return redirect(url_for('books.book_list'))

@bp.route('/list')
@login_required
def book_list():
    books = Book.query.all()
    return render_template('books/book_list.html', title='Book List', books=books)

@bp.route('/search')
@login_required
def search_books():
    query = request.args.get('query')
    books = Book.query.filter(
        (Book.title.ilike(f'%{query}%')) |
        (Book.author.ilike(f'%{query}%')) |
        (Book.isbn.ilike(f'%{query}%'))
    ).all()
    return render_template('books/search_results.html', title='Search Results', books=books, query=query)