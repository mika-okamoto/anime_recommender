import os

from flask import Flask, render_template
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import re
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
import pickle


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    
    @app.route('/')
    def index():
        return render_template("index.html")
    
    @app.route('/rec')
    def rec():

        with open("app/static/data/anime_recommender.pkl", 'rb') as file:  
            model = pickle.load(file)

        anime_names = pd.read_csv('app/static/data/anime_names.csv')

        anime_name = 'One Punch Man'
        query_index = anime_names[anime_names['name'] == anime_name].index[0]

        anime = pd.read_csv('app/static/data/anime_pivot.csv', skiprows = lambda x : x != query_index + 1, nrows=1, header=None)

        distances, indices = model.kneighbors(anime, n_neighbors = 6)
        toreturn = ''

        for i in range(0, len(distances.flatten())):
            if i == 0:
                toreturn += 'Recommendations for {0}:\n'.format(anime_name)
                print('Recommendations for {0}:\n'.format(anime_name))
            else:
                toreturn += '{0}: {1}, with distance of {2}:\n'.format(i, anime_names.loc[indices.flatten()[i]][0], distances.flatten()[i])
                print('{0}: {1}, with distance of {2}:'.format(i, anime_names.loc[indices.flatten()[i]][0], distances.flatten()[i]))
        return toreturn
        # turn this into a html page with a form to input anime name
        # turn into list & do the loop html thing about it??

    return app
