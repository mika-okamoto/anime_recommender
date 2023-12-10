import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import re
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


ratings = pd.read_csv('app/static/data/rating.csv')
anime = pd.read_csv('app/static/data/anime.csv')

filtered_anime = anime.loc[anime['genre'].notnull() & anime['rating'].notnull() & anime['type'].notnull() & (anime['genre'].str.contains("Hentai") == False) & (anime['genre'].str.contains("Harem") == False) & (anime.type.isin(['TV', 'Movie']))]

ratings = ratings[ratings.rating != -1]
ratings = ratings[ratings.anime_id.isin(filtered_anime.anime_id)]
filtered_ratings = ratings[ratings['user_id'].map(ratings.user_id.value_counts()) >= 50]

filtered_ratings.columns = ['user_id', 'anime_id', 'user_rating']

df = pd.merge(filtered_anime, filtered_ratings, on=['anime_id','anime_id'])

def text_cleaning(text):
    text = re.sub(r'&quot;', '', text)
    text = re.sub(r'.hack//', '', text)
    text = re.sub(r'&#039;', '', text)
    text = re.sub(r'A&#039;s', '', text)
    text = re.sub(r'I&#039;', 'I\'', text)
    text = re.sub(r'&amp;', 'and', text)
    
    return text

df['name'] = df['name'].apply(text_cleaning)

rated_anime = df[['user_id', 'name', 'user_rating']]
pivot = rated_anime.pivot_table(index=['user_id'], columns=['name'], values='user_rating')

anime_pivot = pivot.apply(lambda x : (x - np.mean(x))/(np.max(x) - np.min(x)), axis=1).T.fillna(0)
anime_pivot = anime_pivot.loc[:, (anime_pivot != 0).any(axis=0)]

anime_matrix = csr_matrix(anime_pivot.values)

model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(anime_matrix)

import pickle

# save the iris classification model as a pickle file
model_pkl_file = "app/static/data/anime_recommender.pkl"  

with open(model_pkl_file, 'wb') as file:  
    pickle.dump(model_knn, file)

to_output = anime_pivot.reset_index()
to_output[['name']].to_csv('app/static/data/anime_names.csv')

anime_pivot.to_csv('app/static/data/anime_pivot.csv', index=False)

with open("app/static/data/anime_recommender.pkl", 'rb') as file:  
    model = pickle.load(file)

anime_names = pd.read_csv('app/static/data/anime_names.csv')

anime_name = 'Death Note'
query_index = anime_names[anime_names['name'] == anime_name].index[0]

anime = pd.read_csv('app/static/data/anime_pivot.csv', skiprows = lambda x : x != query_index + 1, nrows=1, header=None)

distances, indices = model.kneighbors(anime, n_neighbors = 6)

for i in range(0, len(distances.flatten())):
    if i == 0:
        print('Recommendations for {0}:\n'.format(anime_name))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, anime_names.loc[indices.flatten()[i]][0], distances.flatten()[i]))
