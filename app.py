# app.py
import streamlit as st
from recommender import recommend

st.set_page_config(page_title="Movie Recommender", page_icon="🎬")

st.title("🎬 Movie Recommendation Portal")

movie = st.text_input("Enter a movie title (e.g., Toy Story (1995))")

if st.button("Recommend"):
    recs = recommend(movie)
    st.subheader("You might also like:")
    for r in recs:
        st.write("👉", r)
