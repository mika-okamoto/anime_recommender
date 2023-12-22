import os

from flask import Flask, render_template, request
import pandas as pd
import pickle


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route('/', methods = ("GET", "POST"))
    def index():
        recs = []
        if request.method == "POST":
            recs = []
            anime_name = request.form.get('anime-name')
            with open("app/static/data/anime_recommender.pkl", 'rb') as file:  
                model = pickle.load(file)

            anime_names = pd.read_csv('app/static/data/anime_names.csv')

            try:
                query_index = anime_names[anime_names['name'] == anime_name].index[0]
                anime = pd.read_csv('app/static/data/anime_pivot.csv', skiprows = lambda x : x != query_index + 1, nrows=1, header=None)
                distances, indices = model.kneighbors(anime, n_neighbors = 6)

                for i in range(1, len(distances.flatten())):
                    recs.append('{0}: {1}'.format(i, anime_names.loc[indices.flatten()[i]][0]))
                    # print('{0}: {1}, with distance of {2}:'.format(i, anime_names.loc[indices.flatten()[i]][0], distances.flatten()[i]))
                return render_template("index.html", anime_name = anime_name, recs = recs)
            except: 
                return render_template("index.html", anime_name = anime_name)
            
        return render_template("index.html")

    return app


# need anime lookup page/table (query from csv for idx name based on anime_names.csv)
# ideally search for words (non case sensitive) & translate between engl/japanese to show either

# first fix to be non-case sensitive searching
# then be able to query for including any one of the words (excluding stopwords)
# or just search straight out?
# want to display all of the anime options 

# for more advanced maybe let you click on the anime options to select that as the name and then use that w/ the submit button