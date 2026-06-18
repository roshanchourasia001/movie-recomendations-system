import pickle
import streamlit as st
import requests


@st.cache_data
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}"
    params = {
        "api_key": "04c968aaf588f6b5929897b43b7b3aec",
        "language": "en-US"
    } 

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP errors

        data = response.json()
        poster_path = data.get("poster_path")

        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            return "https://via.placeholder.com/500x750?text=No+Image"

    except requests.exceptions.RequestException as e:
        print(f"TMDB error for movie_id {movie_id}: {e}")
        return "https://via.placeholder.com/500x750?text=Error"

import requests

@st.cache_data
def fetch_key(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos"
    params = {
        "api_key": "04c968aaf588f6b5929897b43b7b3aec",
        "language": "en-US"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        for video in data.get("results", []):
            if video.get("site") == "YouTube" and video.get("type") == "Trailer":
                return video.get("key")

    except requests.exceptions.RequestException as e:
        print(f"Trailer error for movie_id {movie_id}: {e}")

    return None



def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )

    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_ids.append(movie_id)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids



st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl','rb'))
similarity = pickle.load(open('similarity.pkl','rb'))


movie_list = movies['title'].tolist()
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)




if st.button('Show Recommendation'):
    names, posters, ids = recommend(selected_movie)

    trailer_links = []
    for movie_id in ids:
        key = fetch_key(movie_id)
        if key:
            trailer_links.append(f"https://www.youtube.com/watch?v={key}")
        else:
            trailer_links.append(None)

    col1, col2, col3, col4, col5 = st.columns(5)

    for idx, col in enumerate([col1, col2, col3, col4, col5]):
        with col:
            st.text(names[idx])

            if trailer_links[idx]:
                st.markdown(
                    f"""
                    <a href="{trailer_links[idx]}" target="_blank">
                        <img src="{posters[idx]}" width="180">
                    </a>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.image(posters[idx])
                st.caption("Trailer not available")


