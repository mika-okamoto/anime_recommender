## Anime Recommender

Flask application for recommending animes based on nearest neighbors calculated with cosine similarity to user rankings on myanimelist.net. 

Includes: 
- English <--> Japanese (日本語) translations, allowing users to query/view anime names in either language
- Title autocomplete / name searching for closest anime title to user's input based on inferred language
- Searchable & filterable database of animes pulled from anime websites for easy lookup
- Anime recommendations by similarity to inputted anime(s)
- Integrated chatbot to answer specific questions about the recommendations

See: `app/__init__.py`, `app/static/javascript/autocomplete.js`, and `app/static/javascript/chatbot.js` for app functionality code.
