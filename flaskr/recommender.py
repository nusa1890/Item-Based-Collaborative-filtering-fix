from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for, session)
from matplotlib import image
from sklearn.decomposition import TruncatedSVD
from flaskr.db import get_db
from flaskr.auth import login_required
from scipy.sparse.linalg import svds
from flaskr.recommend_movies import recommend_movies
import pandas as pd
import numpy as np
import requests

bp = Blueprint('recommender', __name__)

# recommends movies for any user
# returns the movies with the highest predicted rating that the
# specified user hasn't already rated
# though i didnt user any explicit movie content features

@bp.route('/recommended', methods=['GET', 'POST'])
@login_required
def recommended():
    db = get_db()
    user_id = session.get('user_id')
    recommend_movies(user_id)
    page = request.args.get('page', 1, type=int)
    if page is None:
        page = 0

    movies = db.execute(
            # 'SELECT p.id, title, body, created, author_id, username'
            # ' FROM post p JOIN user u ON p.author_id = u.id'
            # ' ORDER BY created DESC'
            # gets all of the movies
            'SELECT * '
            'FROM rec'+str(g.user['id'])+' LIMIT ? OFFSET ?', ('18', str((page - 1) * 18), )).fetchall()
    #r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=Toy%20story&page=1&include_adult=true&year=1995")

    #movies = predictions
    #for i in range(len(movies.index)):
    #    print(i)
    #    print(movies.iloc[i]['TITLE'])
    return render_template(
        'recommender/recommender.html', movies=movies, page=page)
    # get the two movie sets from the data base

@bp.route('/recommended_next_page', methods=['GET', 'POST'])
@login_required
def recommended_next_page():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    if page is None:
        page = 0

    movies = db.execute(
            # 'SELECT p.id, title, body, created, author_id, username'
            # ' FROM post p JOIN user u ON p.author_id = u.id'
            # ' ORDER BY created DESC'
            # gets all of the movies
            'SELECT * '
            'FROM rec'+str(g.user['id'])+' LIMIT ? OFFSET ?', ('18', str((page - 1) * 18), )).fetchall()
    #r = requests.get("https://api.themoviedb.org/3/search/movie?api_key=8d5d54aa72351ac3e821515d968260c5&language=en-US&query=Toy%20story&page=1&include_adult=true&year=1995")

    #movies = predictions
    #for i in range(len(movies.index)):
    #    print(i)
    #    print(movies.iloc[i]['TITLE'])
    return render_template(
        'recommender/recommender.html', movies=movies, page=page)
    # get the two movie sets from the data base

@bp.route("/search_recommender", methods=['GET'])
def search_recommender():
    db = get_db()
    page = request.args.get('page', 1, type=int)
    query=['']
    print(request.url_rule.endpoint)
    movie_name= request.args.getlist('movie_name')
    genre= request.args.getlist('genre')
    for item in movie_name:
        query.append('SELECT * FROM rec'+str(g.user['id'])+' WHERE title LIKE '+'"%'+item+'%"')
        if not genre:
            query="".join(query)
        else:
            for item in genre:
                query.append(' AND genres LIKE '+'"%'+item+'%"')
            query="".join(query)
    movies=db.execute(query+' LIMIT ? OFFSET ?',('18', str((page - 1) * 18), )).fetchall()
    #movies=db.execute('SELECT * FROM movies LIMIT ? OFFSET ?',('18', str((page - 1) * 18), )).fetchall()
    return render_template('blog/index.html', movies=movies, page=page,movie_name=movie_name,genre=genre)