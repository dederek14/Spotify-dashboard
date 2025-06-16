import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Django

import matplotlib.pyplot as plt
import io
import base64

# Setup Spotify API once at import time
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="ce6d50e0ce16467d9c8f4f1a69db4fe1",
    client_secret="147a7623727b4419a9db26a2d3da2586"
))

def load_and_clean_data(df):
    df['endTime'] = pd.to_datetime(df['endTime'])
    df['year'] = df['endTime'].dt.year
    df['month'] = df['endTime'].dt.month
    df['day'] = df['endTime'].dt.day
    df['hour'] = df['endTime'].dt.hour
    df['weekday'] = df['endTime'].dt.day_name()
    df['date'] = df['endTime'].dt.date
    return df[df['msPlayed'] >= 20000]

def get_artist_genres(artist_id):
    artist = sp.artist(artist_id)
    return artist.get('genres', [])

def get_track_info(track_name, artist_name):
    query = f"track:{track_name} artist:{artist_name}"
    results = sp.search(q=query, type='track', limit=1)
    items = results['tracks']['items']
    if not items:
        return {'id': None, 'popularity': None, 'genres': []}
    track = items[0]
    artist_id = track['artists'][0]['id']
    return {
        'id': track['id'],
        'popularity': track['popularity'],
        'genres': get_artist_genres(artist_id)
    }

def enrich_with_spotify_data(df):
    df = df.copy()
    df['track_id'] = None
    df['popularity'] = None
    df['genres'] = None

    for i, row in df.iterrows():
        info = get_track_info(row['trackName'], row['artistName'])
        print(f"Enriched {row['trackName']} by {row['artistName']}: "
          f"pop={info['popularity']}, genres={info['genres']}")
        df.at[i, 'track_id']   = info['id']
        df.at[i, 'popularity'] = info['popularity']
        df.at[i, 'genres']     = ", ".join(info['genres'])


    return df


matplotlib.use('Agg')  # Non-GUI backend for server
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd


def plot(df):
    df['endTime'] = pd.to_datetime(df['endTime'])

    # ---- Plot 1: Songs per Day ----
    df_daily = df.groupby(df['endTime'].dt.date).size().reset_index(name='song_count')
    df_daily['endTime'] = pd.to_datetime(df_daily['endTime'])
    df_daily = df_daily.set_index('endTime')

    plt.figure(figsize=(10, 4))
    df_daily['song_count'].plot(title='Songs Listened per Day', color='green')
    plt.xlabel('Date')
    plt.ylabel('Songs')
    plt.grid(True)
    plt.tight_layout()

    buf_day = io.BytesIO()
    plt.savefig(buf_day, format='png')
    plt.close()
    buf_day.seek(0)
    img_day = base64.b64encode(buf_day.read()).decode('ascii')
    buf_day.close()

    # ---- Plot 2: Songs per Hour ----
    df['hour'] = df['endTime'].dt.hour
    df_hourly = df.groupby('hour').size().reset_index(name='song_count')

    plt.figure(figsize=(8, 4))
    plt.bar(df_hourly['hour'], df_hourly['song_count'], color='skyblue')
    plt.title('Songs Listened per Hour of Day')
    plt.xlabel('Hour (0–23)')
    plt.ylabel('Songs')
    plt.grid(True)
    plt.tight_layout()

    buf_hour = io.BytesIO()
    plt.savefig(buf_hour, format='png')
    plt.close()
    buf_hour.seek(0)
    img_hour = base64.b64encode(buf_hour.read()).decode('ascii')
    buf_hour.close()

    return img_day, img_hour

import pandas as pd
import os
import pandas as pd

def analyze(df):
    # Step 1: Clean and enrich
    df = load_and_clean_data(df)
    df = enrich_with_spotify_data(df)

    # Step 2: Merge with Kaggle audio features
    
    csv_path = os.path.join(os.path.dirname(__file__), 'tracks_features.csv')
    df_kaggle = pd.read_csv(csv_path)

    df = pd.merge(
        df,
        df_kaggle,
        how='left',
        left_on='track_id',
        right_on='id'
    )

    # Optional: drop duplicate audio features if needed
    # Step 3: Save if you want
    df.to_csv("your_songs_enriched.csv", index=False)

    # Step 4: Return df and stats (same as before)
    return df, {
        "total_songs": int(len(df)),
        "unique_artists": int(df['artistName'].nunique()),
        "top_genres": df['genres'].value_counts().head(5).to_dict(),
        "most_active_hour": int(df['hour'].mode().iloc[0]),
        "top artist": df['artistName'].value_counts().head(10),
        "top track": df['trackName'].value_counts().head(5).to_dict(),
        "avg_valence": round(df['valence'].mean(skipna=True), 3),
        "avg_energy": round(df['energy'].mean(skipna=True), 3),
        "liveness": round(df['liveness'].mean(skipna=True), 3),

    }
