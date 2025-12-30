# recommender.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Load dataset
movies = pd.read_csv("movies.csv")

# Fill missing genres with empty string
movies["genres"] = movies["genres"].fillna("")

# Convert genres into numerical vectors
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(movies["genres"])

# Compute similarity scores
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Create mapping of movie title -> index
indices = pd.Series(movies.index, index=movies['title']).drop_duplicates()

def recommend(title, n=5):
    """Recommend n similar movies based on genre"""
    if title not in indices:
        return ["❌ Movie not found in dataset."]
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n+1]  # skip itself
    movie_indices = [i[0] for i in sim_scores]
    return movies['title'].iloc[movie_indices].tolist()
