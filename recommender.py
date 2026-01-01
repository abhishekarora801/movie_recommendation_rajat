# recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np

# Load dataset
movies = pd.read_csv("movies.csv")

def get_movie_titles():
    """Get sorted list of all movie titles for autocomplete"""
    return sorted(movies['title'].tolist())

# Fill missing genres with empty string
movies["genres"] = movies["genres"].fillna("")

# Convert genres into numerical vectors
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["genres"])

# Compute similarity scores
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Create mapping of movie title -> index
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

def fuzzy_match(title):
    """Find closest matching movie title"""
    if title in indices:
        return title
    
    # Convert to lowercase for comparison
    title_lower = title.lower()
    all_titles = movies['title'].str.lower()
    
    # Find titles containing the search term
    matches = all_titles[all_titles.str.contains(title_lower, na=False)]
    
    if not matches.empty:
        # Return the first match's original title
        return movies.loc[matches.index[0], 'title']
    
    return None

def get_movie_info(idx):
    """Get movie details"""
    return {
        'title': movies.iloc[idx]['title'],
        'genres': movies.iloc[idx]['genres'].split('|')
    }

def recommend(title, n=5):
    """Recommend n similar movies based on genre with enhanced details"""
    # Try fuzzy matching if exact title not found
    matched_title = fuzzy_match(title)
    
    if matched_title is None:
        return {
            'status': 'error',
            'message': '❌ Movie not found in dataset.',
            'input_title': title,
            'recommendations': []
        }
    
    idx = indices[matched_title]
    input_genres = set(movies.iloc[idx]['genres'].split('|'))
    
    # Calculate similarity scores with genre overlap consideration
    sim_scores = []
    for i, row in movies.iterrows():
        if i == idx:  # Skip the input movie
            continue
            
        movie_genres = set(row['genres'].split('|'))
        # Calculate Jaccard similarity for genre overlap
        genre_overlap = len(input_genres.intersection(movie_genres)) / len(input_genres.union(movie_genres))
        # Combine with cosine similarity for better ranking
        combined_score = (cosine_sim[idx][i] + genre_overlap) / 2
        sim_scores.append((i, combined_score))
    
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[:n]  # Get top n recommendations
    
    movie_indices = [i[0] for i in sim_scores]
    similarity_scores = [i[1] for i in sim_scores]
    
    recommendations = []
    for idx, score in zip(movie_indices, similarity_scores):
        movie = get_movie_info(idx)
        movie['similarity_score'] = round(score * 100, 1)  # Convert to percentage
        recommendations.append(movie)
    
    return {
        'status': 'success',
        'message': '✅ Found recommendations!',
        'input_title': matched_title,
        'recommendations': recommendations
    }
