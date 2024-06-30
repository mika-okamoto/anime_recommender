import os

from flask import Flask, render_template, request, jsonify
import pandas as pd
import pickle
import jellyfish
import openai
import gradio as gr

openai.api_key = ""

def create_app():
    app = Flask(__name__, instance_relative_config=True)

    df = pd.read_csv('app/static/data/anime_df.csv')
    system_prompt = ""

    @app.route('/', methods = ("GET", "POST"))
    def index():
        table_html = df.to_html(classes='table table-striped', index=False, border=0)
        return render_template("index.html", table_html = table_html)
    
    @app.route('/chatbot', methods = ("GET", "POST"))
    def chatbot():
        global system_prompt
        prefs, recs = request.args.get('prefs', ''), request.args.get('recs', '')
        system_prompt = f"You are a helpful chatbot who provides information and recommendations about animes. This user said that they want animes like {prefs}, and was recommended to watch {recs}."
        return render_template("chatbot.html", prefs = prefs, recs = recs)
    
    @app.route('/get_response', methods=['POST'])
    def get_response():
        prompt_json = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": request.form['user_message']}
        ]
        chat_completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt_json,
            temperature=0.0,
            max_tokens=1000
        )
        response = chat_completion['choices'][0].message.content
        return jsonify({'response': response})

    @app.route('/autocomplete', methods=['GET'])
    def autocomplete():
        name = request.args.get('q', '')
        return jsonify(list(suggest(name)['suggestion'])[:5])

    @app.route('/recommend', methods=['GET'])
    def recommend():
        recs = []
        animes = request.args.get('q', '').split(',')
        animes = [list(suggest(anime_name)['name'])[0] for anime_name in animes]

        with open("app/static/data/anime_recommender.pkl", 'rb') as file:  
            model = pickle.load(file)

        anime_names = pd.read_csv('app/static/data/anime_names.csv')

        try:
            query_index = [anime_names[anime_names['name'] == name].index[0] + 1 for name in animes]
            anime = pd.read_csv('app/static/data/anime_pivot.csv', skiprows = lambda x : x not in query_index, nrows=len(animes), header=None)
            for i in range(len(animes)):
                anime.loc[i] /= anime.loc[i].mean()
            anime = pd.DataFrame(anime.sum()).T
            distances, indices = model.kneighbors(anime, n_neighbors = 5 + len(animes))
            for i in range(0, len(distances.flatten())):
                recs.append(anime_names.loc[indices.flatten()[i]][0])
            recs = [movie for movie in recs if movie not in animes]

            df = pd.read_csv('app/static/data/anime_df.csv')
            df = df[df.Title.isin(recs)]
            sortidx = dict(zip(recs, range(len(recs))))
            df.insert(0, column='Ranking', value = df['Title'].map(sortidx) + 1)
            df.sort_values(by = 'Ranking', ascending=True, inplace = True)            
            return jsonify(df.to_html(classes='table table-striped', index=False, border=0))
        except:
            return jsonify("No Recommendations Found")

    return app

def suggest(name):
    translated = pd.read_csv('app/static/data/translated.csv')
    translated['jaro_sim_ja'] = translated.apply(lambda row: jellyfish.jaro_similarity(name.lower(), row['japanese'].lower()), axis=1)
    translated['jaro_sim_en'] = translated.apply(lambda row: jellyfish.jaro_similarity(name.lower(), row['english'].lower()), axis=1)
    translated['jaro_sim'] = translated.apply(lambda row : max(row['jaro_sim_ja'], row['jaro_sim_en']), axis = 1)
    translated['suggestion'] = translated.apply(lambda row : row['english'] if row['jaro_sim_en'] == row['jaro_sim'] else row['japanese'], axis = 1)
    return translated.sort_values(by = 'jaro_sim', ascending=False)
