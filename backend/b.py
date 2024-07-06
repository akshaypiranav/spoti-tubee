import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from pytube import YouTube
from youtube_search import YoutubeSearch
import os

# Spotify API credentials
client_id = '34e71922e8fe41db9c15cd17c23fcbfc'
client_secret = '0e4d1ab089a94caaaba069b2b50db0ae'

# Initialize Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_main_artist(track_artists):
    # Get the main artist from the list of artists
    return track_artists.split(',')[0].strip()

def get_playlist_tracks(playlist_url):
    # Extract playlist ID from the URL
    playlist_id = playlist_url.split('/')[-1]

    # Retrieve tracks from the playlist
    tracks = sp.playlist_tracks(playlist_id)['items']
    
    # Extract track details
    track_details = []
    for track in tracks:
        track_info = track['track']
        track_name = track_info['name']
        track_artists = ', '.join([artist['name'] for artist in track_info['artists']])
        track_details.append({'name': track_name, 'artists': track_artists})
    
    return track_details

def search_and_download(query):
    # Search for the video using the query
    results = YoutubeSearch(query, max_results=1).to_dict()
    
    # Check if any results are found
    if results:
        # Extract the first video URL from the search results
        video_url = "https://www.youtube.com" + results[0]['url_suffix']
        
        # Download the audio
        download_audio(video_url)
    else:
        print("No results found for the query:", query)

def download_audio(video_url):
    try:
        # Create a YouTube object with the video URL
        yt = YouTube(video_url)
        
        # Select the audio stream
        audio_stream = yt.streams.filter(only_audio=True).first()
        
        # Create a folder for storing downloaded audio
        folder_path = os.path.join(os.getcwd(), "downloaded_audio")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        
        # Download the audio
        audio_stream.download(output_path=folder_path)
        
        print("Download completed successfully!")
    except Exception as e:
        print("Error occurred:", str(e))

def main():
    # Spotify playlist URL
    playlist_url = "https://open.spotify.com/playlist/7uFemBErrjIzBQFSWMO3kg"
    
    # Get track details from the Spotify playlist
    track_details = get_playlist_tracks(playlist_url)
    
    # Create a folder for storing downloaded audio
    if not os.path.exists("downloaded_audio"):
        os.makedirs("downloaded_audio")
    
    # Search for each song on YouTube and download the audio
    for track in track_details:
        song_name = track['name']
        artists = track['artists']
        main_artist = get_main_artist(artists)
        print(f"Searching for '{song_name}' by {main_artist} on YouTube...")
        try:
            search_query = f"{song_name} {main_artist} official audio"
            search_and_download(search_query)
        except Exception as e:
            print(f"Error downloading '{song_name}': {e}")

if __name__ == "__main__":
    main()
