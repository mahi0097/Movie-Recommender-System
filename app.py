import streamlit as st
import pickle
import requests
import time
import os
import gdown

# --- Download similarity.pkl from Google Drive if not already present ---
file_id = "13Vqqn6fG-QdajVjzxgK1bpSxV-yE35HR"
output_path = "similarity.pkl"

if not os.path.exists(output_path):
    print("Downloading similarity.pkl from Google Drive...")
    gdown.download(f"https://drive.google.com/uc?id={file_id}", output_path, quiet=False)
else:
    print("similarity.pkl already exists.")


# --- Fetch poster from TMDB ---
def fetch_poster(movie_id, retries=3):
    api_key = "b438a3e50b68249ae13effbe30e5df66"
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}"
    
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(1)
            
    return "https://via.placeholder.com/200x300?text=Poster+Unavailable"


# --- Recommend similar movies ---
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_posters = []
    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_posters


# --- Load preprocessed data ---
movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# --- Streamlit UI ---
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Search for a movie to get recommendations:',
    movies['title'].values
)

if st.button('Show Recommendations'):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i in range(5):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
