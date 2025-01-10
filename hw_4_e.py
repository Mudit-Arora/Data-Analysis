# -*- coding: utf-8 -*-
"""HW 4 E

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kzDwjT8BdcNwZTDGQwwxUgDUj_WHIHHQ
"""

import kagglehub

# Download latest version
path = kagglehub.dataset_download("crowdflower/twitter-airline-sentiment")

print("Path to dataset files:", path)

import pandas as pd
data = pd.read_csv(path + "/Tweets.csv")
print(data.head())

##### PART A ######

unique_users = data['name'].unique()
num_unique_users = len(unique_users)
print("Number of unique users:", num_unique_users)

from sklearn.feature_extraction.text import TfidfVectorizer

def get_top_words(user_tweets, top_n=5):
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(user_tweets)
    feature_names = vectorizer.get_feature_names_out()

    # Get top words for each user
    top_words = []
    for i in range(tfidf_matrix.shape[0]):
        row = tfidf_matrix[i].toarray()[0]
        top_word_indices = row.argsort()[-top_n:][::-1]
        top_words.extend([feature_names[j] for j in top_word_indices])

    return top_words

# Group tweets by user and compute top words
user_tweets = data.groupby('name')['text'].apply(list)
top_words_by_user = user_tweets.apply(get_top_words)

print(top_words_by_user)

##### PART B ######

airline_user_counts = data.groupby(['airline', 'name'])['tweet_id'].count().reset_index()
airline_user_counts.rename(columns={'tweet_id': 'tweet_count'}, inplace=True)

most_active_users = airline_user_counts.loc[airline_user_counts.groupby('airline')['tweet_count'].idxmax()]

result = pd.merge(most_active_users, data, on=['airline', 'name'], how='left')

final_result = result[['airline', 'name', 'tweet_count', 'text',  'airline_sentiment']]

print(final_result)

###### PART C #####

missing_tweet_location = data['tweet_location'].isnull().sum()
missing_user_timezone = data['user_timezone'].isnull().sum()

print("Missing values in 'tweet_location':", missing_tweet_location)
print("Missing values in 'user_timezone':", missing_user_timezone)

data_cleaned = data.dropna(subset=['tweet_location', 'user_timezone'])

print(data_cleaned)

#### PART D ######

data_cleaned['tweet_created'] = pd.to_datetime(data_cleaned['tweet_created'], errors='coerce')
print(f"\nData types after parsing 'tweet_created': {data_cleaned.dtypes}")

##### PART E #####

import re

def is_philadelphia(location):
    # Define patterns to match Philadelphia variations
    patterns = [
        r"philadelphia",  # Basic spelling
        r"philly",        # Common abbreviation
        r"phila\.?",     # Abbreviation with optional period
        r"phily",         # Misspelling
    ]

    # Check if any pattern matches the location (case-insensitive)
    for pattern in patterns:
        if re.search(pattern, location, re.IGNORECASE):
            return True
    return False

philadelphia_tweets = data_cleaned['tweet_location'].apply(is_philadelphia).sum()

print("Total tweets from Philadelphia (including variations):", philadelphia_tweets)

all_locations = data_cleaned['tweet_location'].unique()
philadelphia_spellings = [loc for loc in all_locations if is_philadelphia(loc)]
print("Different spellings of Philadelphia:", philadelphia_spellings)

filtered_data = data_cleaned[data_cleaned['airline_sentiment_confidence'] > 0.6]
filtered_data.to_csv('filtered_tweets.csv', index=False)
print(filtered_data)