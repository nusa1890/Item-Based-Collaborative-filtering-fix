from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from matplotlib import image
from sklearn.decomposition import TruncatedSVD
from flaskr.db import get_db

from scipy.sparse.linalg import svds

import pandas as pd
import numpy as np
import requests

bp = Blueprint('recommender', __name__)

# recommends movies for any user
# returns the movies with the highest predicted rating that the
# specified user hasn't already rated
# though i didnt user any explicit movie content features
def recommend_movies(user):
    db = get_db()
    #Ambil data ratings dari sqlite dengan querry "SELECT * FROM review" dan simpan ke pandas dataframe
    ratings = pd.read_sql_query('SELECT userId, movieId, rating FROM ratings',db)
    ratings.columns = ['USERID', 'MOVIEID', 'RATING']
    #Ambil data movies dari sqlite dengan querry "SELECT * FROM review" dan simpan ke pandas dataframe
    movies = pd.read_sql_query('SELECT * FROM movies', db)
    movies.columns = ['MOVIEID', 'TITLE', 'GENRES', 'POSTER']

    num_rated = len(db.execute(
        'SELECT m.id, m.title, m.genres, m.poster, r.rating '
        'FROM movies m '
        'INNER JOIN '
        'ratings r '
        'ON r.userID = '+str(user)+' '
        'and m.id = r.movieID '
        'LIMIT 15').fetchall())

    combined_movies_data = pd.merge(ratings, movies, how='inner', on='MOVIEID')#merge data rating dan data movie pada movieId
    #Buat pivot table untuk rating menggunakan userId sebagai index dan movieId sebagai kolom
    rating_crosstab = combined_movies_data.pivot_table(index='USERID', columns='MOVIEID', values='RATING').fillna(0)
    #lakukan transpose dan dimesionality reduction dengan menggunakan fungsi SVD ke tabel pivot yang telah dibuat
    X = rating_crosstab.T
    SVD = TruncatedSVD(n_components=12, random_state=5)
    resultant_matrix = SVD.fit_transform(X)

    #cari korelasi antar film menggunakan pearson correlation menggunakan fungsi corrcoef pada library numpy
    corr_mat = np.corrcoef(resultant_matrix)
    corr_mat = pd.DataFrame(corr_mat, columns = rating_crosstab.columns.tolist(), index = rating_crosstab.columns.tolist())
    #cari data user yang akan diberi rekomendasi berdasarkan rating film tertinggi yang diberikan 
    try:
        userId = user
        unrated=X[userId].loc[X[userId]==0]
        rated=X[userId].loc[X[userId]>0]
        #buat pivot table dengan menggunakan movieId yang sudah dirating sebagai kolom dan movieId yang belum dirating sebagai index
        r_ur_corr_matt=corr_mat[rated.index].loc[unrated.index]\
                    .apply(lambda x: x.nlargest(5), axis=1).fillna(0)#cari nilai similarity pada 10 item yang sudah 
        simlilarity_dot_weight=r_ur_corr_matt.apply(lambda x: sum(x*rated), axis=1)
        simlilarity_sum=r_ur_corr_matt.apply(np.sum, axis=1)
        pred=(simlilarity_dot_weight/simlilarity_sum).sort_values(ascending=False)
        reccomendation=pd.concat([movies.set_index('MOVIEID'), pred], axis=1).sort_values(by=0, ascending=False)
        reccomendation.columns = ['title', 'genres', 'poster', 'pred_rating']
        reccomendation=reccomendation.rename_axis('id')
    except:
        reccomendation=movies
        reccomendation.columns = ['id', 'title', 'genres', 'poster']
    if num_rated < 15:
        flash("Please rate atleast "+str(15-num_rated)+" movies to get personalized reccomendation")
    reccomendation.to_sql("rec"+str(user), db, if_exists='replace')