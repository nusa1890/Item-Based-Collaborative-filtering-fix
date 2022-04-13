from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)

from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

import requests

bp = Blueprint('blog', __name__)

# change this to all movies
# also allow this to change if a search is done on the title or genre
# some how display the results in pages?
@bp.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)

    db = get_db()

    if page is None:
        page = 1

    if g.user:
        movies = db.execute(
            # get all of the movies they haven't rated
            'SELECT id, title, genres, poster '
            'FROM movies '
            'EXCEPT '
            'SELECT m.id, m.title, m.genres, m.poster '
            'FROM movies m '
            'INNER JOIN '
            'ratings r '
            'ON r.userID = ? '
            'and m.id = r.movieID '
            'LIMIT ? OFFSET ?',
            (g.user['id'], '18', str((page - 1) * 18), )).fetchall()
    else:
        movies = db.execute(
            # 'SELECT p.id, title, body, created, author_id, username'
            # ' FROM post p JOIN user u ON p.author_id = u.id'
            # ' ORDER BY created DESC'
            # gets all of the movies
            'SELECT * '
            'FROM movies LIMIT ? OFFSET ?', ('18', str((page - 1) * 18), )).fetchall()


    return render_template('blog/index.html', movies=movies, page = page)

@bp.route("/search", methods=['GET'])
def search():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    query=['']
    movie_name= request.args.getlist('movie_name')
    genre= request.args.getlist('genre')
    for item in movie_name:
        query.append('SELECT * FROM movies WHERE title LIKE '+'"%'+item+'%"')
        if not genre:
            query="".join(query)
        else:
            for item in genre:
                query.append(' AND genres LIKE '+'"%'+item+'%"')
            query="".join(query)
    movies=db.execute(query+' LIMIT ? OFFSET ?',('18', str((page - 1) * 18), )).fetchall()
    #movies=db.execute('SELECT * FROM movies LIMIT ? OFFSET ?',('18', str((page - 1) * 18), )).fetchall()
    return render_template('blog/index.html', movies=movies, page=page,movie_name=movie_name,genre=genre)

# lists all of the films that the current user has already rated
@bp.route('/rated')
@login_required
def rated():
    page = request.args.get('page', 1, type=int)

    if page is None:
        page = 1

    db = get_db()
    ratings = db.execute(
        'SELECT m.id, m.title, m.genres, m.poster, r.rating '
        'FROM movies m '
        'INNER JOIN '
        'ratings r '
        'ON r.userID = ? '
        'and m.id = r.movieID '
        'LIMIT ? OFFSET ?',
        (g.user['id'], '18', str((page - 1) * 18), )).fetchall()

    return render_template('blog/ratings.html', ratings=ratings, page=page)


# updates the rating of a film you have watched
@bp.route('/<int:id>/update', methods=('POST', ))
@login_required
def update(id):
    # value to change the rating to
    db = get_db()
    db.execute(
        'UPDATE ratings '
        'SET rating = ?'
        'WHERE userID = ? '
        'AND movieID = ? ', (request.form['value'], g.user['id'], id))
    db.commit()
    return redirect(url_for('blog.rated'))


# removes a post from seen and rated to not rated anymore
@bp.route('/<int:id>/remove', methods=('POST', ))
@login_required
def remove(id):
    db = get_db()
    db.execute('DELETE FROM ratings '
               'WHERE userID = ? '
               'AND movieID = ?', (g.user['id'], id))
    db.commit()
    return redirect(url_for('blog.rated'))


# adding a rating to a film moves it to rated films with that rating
@bp.route('/<int:id>/add', methods=('POST', ))
@login_required
def add(id):
    print(request.form['value'])
    db = get_db()
    db.execute(
        'INSERT INTO ratings '
        '(userID, movieID, rating) '
        'VALUES (?, ?, ?)', (g.user['id'], id, request.form['value']))
    db.commit()
    print(url_for('index'))
    return redirect(url_for('index'))



