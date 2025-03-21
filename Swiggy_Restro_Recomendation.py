import streamlit as st
import pandas as pd
import numpy as np
import pickle
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity

# Load Data
swiggy_data = pd.read_csv('C:/Users/dell/Documents/Guvi Lectures/Swiggy model/swiggy_cleaned_model.csv')

# Load Encoder and Encoded Data
with open('C:/Users/dell/Documents/Guvi Lectures/Swiggy model/encoder_today.pkl', 'rb') as file:
    encoder = pickle.load(file)

encoded_data = load_npz('C:/Users/dell/Documents/Guvi Lectures/Swiggy model/encoded_data_sparse.npz')  # Load sparse matrix directly

# Streamlit App
st.title('Restaurant Recommendation System')
st.sidebar.header('User Input Preferences')

# User Inputs
selected_city = st.sidebar.selectbox('Select City', swiggy_data['city'].unique())
selected_cuisines = st.sidebar.multiselect('Select Cuisines', swiggy_data['cuisine'].unique())
min_rating = st.sidebar.slider('Minimum Rating', 0.0, 5.0, 3.0)
max_cost = st.sidebar.slider('Maximum cost',0,1000)

# Filter dataset based on user inputs
filtered_df = swiggy_data[(swiggy_data['city'] == selected_city) &
                         (swiggy_data['rating'] >= min_rating) &
                         (swiggy_data['cuisine'].isin(selected_cuisines))&
                         (swiggy_data['cost'] <= max_cost)]

if filtered_df.empty:
    st.write("No matching restaurants found. Try adjusting your filters.")
else:
    # Compute similarity matrix for filtered data only
    filtered_indices = filtered_df.index.tolist()
    filtered_encoded_data = encoded_data[filtered_indices]

    similarity_matrix = cosine_similarity(filtered_encoded_data)

    # Select a random restaurant from the filtered list for recommendations
    selected_index = np.random.choice(filtered_indices)

    # Get similarity scores
    similarity_scores = similarity_matrix[filtered_indices.index(selected_index)]

    # Get top 5 similar restaurants
    similar_indices = np.argsort(similarity_scores)[::-1][1:6]
    recommended_restaurants = filtered_df.iloc[similar_indices]

    st.write('### Recommended Restaurants')
    st.write(recommended_restaurants[['name', 'city', 'cuisine', 'rating', 'cost']])