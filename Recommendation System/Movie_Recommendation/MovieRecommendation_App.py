import os
import streamlit as st
import pandas as pd
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import requests
from urllib.parse import quote

st.set_page_config(page_title="Movie Recommender", layout="wide")

# Load movie data
movie_data = pd.read_csv("movie_data_preprocessed.csv")

# Embedding function
embedding_fn = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load vector store
vector_store = Chroma(persist_directory="./chroma_movies", embedding_function=embedding_fn)

OMDB_API_KEY = "e1bd2d70"

# Function to fetch poster from OMDb or fallback
def fetch_fallback_poster(title):
    return f"https://via.placeholder.com/300x450.png?text={title.replace(' ', '+')}"

def fetch_poster_from_omdb(title):
    try:
        response = requests.get(f"http://www.omdbapi.com/?t={title}&apikey={OMDB_API_KEY}")
        data = response.json()
        return data["Poster"] if data.get("Poster") != "N/A" else fetch_fallback_poster(title)
    except:
        return fetch_fallback_poster(title)

# Function to recommend similar movies
def recommend(movie_title: str, k=5):
    movie_row = movie_data[movie_data["title"] == movie_title]
    if movie_row.empty:
        return [], []
    query = movie_row.iloc[0]["tags"]
    results = vector_store.similarity_search(query, k=k+1)

    recommended_titles = []
    recommended_posters = []

    for doc in results:
        title = doc.metadata["title"]
        if title != movie_title:
            recommended_titles.append(title)
            recommended_posters.append(fetch_poster_from_omdb(title))

    return recommended_titles, recommended_posters

# Function to display grid of movies (clickable poster + plain title)
def display_movie_grid(titles, posters, num_cols=5):
    cols = st.columns(num_cols)
    for i in range(len(titles)):
        with cols[i]:
            encoded_title = quote(titles[i])
            st.markdown(
                f'<a href="?movie={encoded_title}" target="_self">'
                f'<img src="{posters[i]}" width="150" style="border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); cursor:pointer;">'
                f'</a>',
                unsafe_allow_html=True
            )
            st.caption(titles[i])

# --- Add CSS Styling ---
st.markdown(
    """
    <style>
    /* Style the Back to Home button */
    div.stButton > button {
        background-color: #007acc;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 8px 16px;
        margin-top: 15px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #005f99;
        cursor: pointer;
    }
    /* Center captions below images */
    .stCaption {
        text-align: center;
        font-weight: 600;
        margin-top: 5px;
        font-size: 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Streamlit app
st.title("🎬 Movie Recommendation System (GenAI powered)")

# Check if a movie is selected via query params
movie_param = st.query_params.get("movie")

if movie_param:
    movie_param = movie_param[0] if isinstance(movie_param, list) else movie_param

    # Detailed view of clicked movie
    st.subheader(f"🎬 Movie Details: {movie_param}")

    try:
        response = requests.get(f"http://www.omdbapi.com/?t={movie_param}&apikey={OMDB_API_KEY}")
        data = response.json()

        st.image(data["Poster"] if data.get("Poster") != "N/A" else fetch_fallback_poster(movie_param), width=200)
        st.markdown(f"**IMDb Rating:** {data.get('imdbRating', 'N/A')}")
        st.markdown(f"**Actors:** {data.get('Actors', 'N/A')}")
        st.markdown(f"**Plot:** {data.get('Plot', 'N/A')}")
        st.markdown(f"**Released:** {data.get('Released', 'N/A')} | **Runtime:** {data.get('Runtime', 'N/A')}")
        st.markdown(f"**Genre:** {data.get('Genre', 'N/A')} | **Director:** {data.get('Director', 'N/A')}")
    except:
        st.error("Could not fetch movie details.")

    # Back to Home button clears query params and reloads home
    st.markdown(
        """
        <a href="./">
            <button style="
                background-color:#007acc;
                color:white;
                padding:8px 16px;
                font-weight:600;
                border:none;
                border-radius:8px;
                cursor:pointer;
                margin-top:15px;
            ">
                🔙 Back to Home
            </button>
        </a>
        """,
    unsafe_allow_html=True
    )

    # Show similar movies
    st.markdown("### You may also like:")
    titles, posters = recommend(movie_param)
    if titles:
        display_movie_grid(titles, posters)
    else:
        st.info("No similar movies found.")

else:
    # Movie selection + recommendations
    movie_list = movie_data['title'].values
    selected_movie = st.selectbox("Select a movie to get recommendations:", movie_list)

    if st.button("Show Recommendations"):
        titles, posters = recommend(selected_movie)
        if titles:
            display_movie_grid(titles, posters)
        else:
            st.warning("No recommendations found.")
