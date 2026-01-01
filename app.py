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
st.markdown("<h1 style='text-align: center;'>🎬 Movie Recommendation Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>This app recommends movies based on genre similarity. Enter a movie title below to get started!</p>", unsafe_allow_html=True)

# Load movie titles for autocomplete
from recommender import get_movie_titles

# Get all movie titles
all_movies = get_movie_titles()

# Create a text input with HTML datalist for autocomplete
st.markdown("""
    <datalist id="movies">
        {}
    </datalist>
    """.format('\n'.join(f'<option value="{movie}">' for movie in all_movies)), 
    unsafe_allow_html=True
)

# Input section with aligned columns
col1, col2 = st.columns([3, 1])

with col1:
    search_term = st.text_input(
        "Enter a movie title (e.g., Toy Story (1995))", 
        key="search_input",
        help="Start typing to see suggestions",
        value="",
        placeholder="Type to search movies...",
    )

with col2:
    n_recommendations = st.selectbox("Number of recommendations", [5, 10, 15, 20], key="n_select")

# Add the datalist to the input using JavaScript
st.markdown("""
    <script>
    const input = document.querySelector('input[aria-label="Enter a movie title (e.g., Toy Story (1995))"]');
    input.setAttribute('list', 'movies');
    </script>
    """, 
    unsafe_allow_html=True
)

# Show suggestions and recommendations as user types
if search_term:
    # Filter movies based on search term
    filtered_movies = [m for m in all_movies if search_term.lower() in m.lower()][:5]  # Limit to top 5 suggestions
    
    # Show matching suggestions
    if filtered_movies:
        st.markdown("### Matching Movies:")
        for suggestion in filtered_movies:
            st.markdown(f"- {suggestion}")
        
        # Get recommendations based on the first match
        with st.spinner('Finding similar movies...'):
            result = recommend(filtered_movies[0], n=n_recommendations)
            
            if result['status'] == 'success':
                st.success(f"Recommendations based on '{result['input_title']}':")
                
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
    else:
        st.info("No matching movies found. Try a different search term!")

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>Made with ❤️ by Rajat</p>", unsafe_allow_html=True)
