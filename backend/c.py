import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Spotify API credentials
client_id = '34e71922e8fe41db9c15cd17c23fcbfc'
client_secret = '0e4d1ab089a94caaaba069b2b50db0ae'

# Initialize Spotipy client
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def get_playlist_tracks(playlist_url):
    # Extract playlist ID from the URL
    playlist_id = playlist_url.split('/')[-1]
    
    # Retrieve tracks from the playlist
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    
    # Loop through all pages of the playlist
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    
    # Extract track details
    track_details = []
    for track in tracks:
        track_info = track['track']
        track_name = track_info['name']
        track_artists = ', '.join([artist['name'] for artist in track_info['artists']])
        album_info = track_info['album']
        album_name = album_info['name']
        album_release_date = album_info['release_date']
        album_total_tracks = album_info['total_tracks']
        album_type = album_info['album_type']
        popularity = track_info['popularity']
        duration_ms = track_info['duration_ms']
        uri = track_info['uri']
        image_url = album_info['images'][0]['url'] if album_info['images'] else None
        track_number = track_info['track_number']
        disc_number = track_info['disc_number']
        explicit = track_info['explicit']
        preview_url = track_info['preview_url']

        track_details.append({
            'name': track_name,
            'artists': track_artists,
            'album_name': album_name,
            'album_release_date': album_release_date,
            'album_total_tracks': album_total_tracks,
            'album_type': album_type,
            'popularity': popularity,
            'duration_ms': duration_ms,
            'uri': uri,
            'image_url': image_url,
            'track_number': track_number,
            'disc_number': disc_number,
            'explicit': explicit,
            'preview_url': preview_url
        })
    
    return track_details

def main():
    # Spotify playlist URL
    playlist_url = "https://open.spotify.com/playlist/6jHRReNG2KeCSU4GY76omf"
    
    # Get track details from the Spotify playlist
    track_details = get_playlist_tracks(playlist_url)
    
    # Print track details
    for idx, track in enumerate(track_details, start=1):
        print(f"Track {idx}:")
        print(f"Name: {track['name']}")
        print(f"Artists: {track['artists']}")
        print(f"Album Name: {track['album_name']}")
        print(f"Album Release Date: {track['album_release_date']}")
        print(f"Album Total Tracks: {track['album_total_tracks']}")
        print(f"Album Type: {track['album_type']}")
        print(f"Popularity: {track['popularity']}")
        print(f"Duration (ms): {track['duration_ms']}")
        print(f"URI: {track['uri']}")
        print(f"Image URL: {track['image_url']}")
        print(f"Track Number: {track['track_number']}")
        print(f"Disc Number: {track['disc_number']}")
        print(f"Explicit: {track['explicit']}")
        print(f"Preview URL: {track['preview_url']}\n")

if __name__ == "__main__":
    main()
