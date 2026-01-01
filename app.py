# app.py
import streamlit as st
from recommender import recommend

# Page config
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# Load external CSS
with open('styles.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Title and description
st.title("🎬 Movie Recommendation Portal")
st.markdown("""
This app recommends movies based on genre similarity. Enter a movie title below to get started!
""")

# Load movie titles for autocomplete
from recommender import get_movie_titles

# Input section
col1, col2 = st.columns([3, 1])
with col1:
    movie = st.selectbox("Enter a movie title", get_movie_titles(), key="movie_input")
with col2:
    n_recommendations = st.selectbox("Number of recommendations", [5, 10, 15, 20], key="n_select")

# Recommendation section
if st.button("🔍 Find Similar Movies"):
    if movie:
        with st.spinner('Finding similar movies...'):
            result = recommend(movie, n=n_recommendations)
            
            if result['status'] == 'success':
                st.success(f"Found recommendations based on '{result['input_title']}'!")
                
                # Display recommendations
                for movie in result['recommendations']:
                    with st.container():
                        st.markdown(f"""
                        <div class="movie-card">
                            <h3>{movie['title']}</h3>
                            <p class="similarity-score">Similarity: {movie['similarity_score']}%</p>
                            <p>Genres: {' '.join([f'<span class="genre-tag">{g}</span>' for g in movie['genres']])}</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.error(result['message'])
                st.info("Try entering a different movie title!")
    else:
        st.warning("Please enter a movie title!")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ by Rajat")
