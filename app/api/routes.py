from flask import jsonify, request
from app.api import api
from app.models import User, Book
from app import db

@api.route('/books', methods=['GET'])
def get_books():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

@api.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    book = Book.query.get_or_404(id)
    return jsonify(book.to_dict())

@api.route('/books', methods=['POST'])
def create_book():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    data = request.get_json()
    if not all(k in data for k in ('title', 'author', 'isbn')):
        return jsonify({"msg": "Missing required fields"}), 400
    book = Book(
        title=data['title'],
        author=data['author'],
        isbn=data['isbn'],
        length=data.get('length'),
        format=data.get('format'),
        user_id=user.id
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

@api.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    book = Book.query.get_or_404(id)
    if book.user_id != user.id:
        return jsonify({"msg": "Not authorized to update this book"}), 403
    data = request.get_json()
    for field in ('title', 'author', 'isbn', 'length', 'format'):
        if field in data:
            setattr(book, field, data[field])
    db.session.commit()
    return jsonify(book.to_dict())

@api.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"msg": "Missing token"}), 401
    user = User.query.filter_by(token=token).first()
    if not user:
        return jsonify({"msg": "Invalid token"}), 401
    book = Book.query.get_or_404(id)
    if book.user_id != user.id:
        return jsonify({"msg": "Not authorized to delete this book"}), 403
    db.session.delete(book)
    db.session.commit()
    return '', 204