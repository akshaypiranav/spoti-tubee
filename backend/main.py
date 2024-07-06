from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from pytube import YouTube
from youtube_search import YoutubeSearch
import io,time
import asyncio

app = FastAPI()

origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

client_id = '34e71922e8fe41db9c15cd17c23fcbfc'
client_secret = '0e4d1ab089a94caaaba069b2b50db0ae'

client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

@app.get("/")
async def read_root():
    return {"message": "Hello World"}

@app.post("/getDetails")
async def getDetails(request: Request):
    data = await request.json()
    playlist_id = data.get('id')
    if not playlist_id:
        raise HTTPException(status_code=400, detail="Invalid playlist ID")

    try:
        results = sp.playlist_tracks(playlist_id)
    except spotipy.exceptions.SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))

    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])

    track_details = []
    for track in tracks:
        track_info = track['track']
        track_details.append({
            'name': track_info['name'],
            'artists': ', '.join([artist['name'] for artist in track_info['artists']]),
            'album_name': track_info['album']['name'],
            'album_release_date': track_info['album']['release_date'],
            'album_total_tracks': track_info['album']['total_tracks'],
            'album_type': track_info['album']['album_type'],
            'popularity': track_info['popularity'],
            'duration_ms': track_info['duration_ms'],
            'uri': track_info['uri'],
            'image_url': track_info['album']['images'][0]['url'] if track_info['album']['images'] else None,
            'track_number': track_info['track_number'],
            'disc_number': track_info['disc_number'],
            'explicit': track_info['explicit'],
            'preview_url': track_info['preview_url']
        })

    return track_details

def get_track_details(track_id):
    try:
        track = sp.track(track_id)
    except spotipy.exceptions.SpotifyException as e:
        raise HTTPException(status_code=400, detail=str(e))

    track_details = {
        'name': track['name'],
        'artists': ', '.join([artist['name'] for artist in track['artists']]),
        'album_name': track['album']['name'],
        'album_release_date': track['album']['release_date'],
        'album_total_tracks': track['album']['total_tracks'],
        'album_type': track['album']['album_type'],
        'popularity': track['popularity'],
        'duration_ms': track['duration_ms'],
        'uri': track['uri'],
        'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
        'track_number': track['track_number'],
        'disc_number': track['disc_number'],
        'explicit': track['explicit'],
        'preview_url': track['preview_url']
    }
    return track_details

def search_and_download(query):
    results = YoutubeSearch(query, max_results=1).to_dict()
    if results:
        video_url = "https://www.youtube.com" + results[0]['url_suffix']
        return download_audio(video_url)
    else:
        print("No results found for the query:", query)
        raise HTTPException(status_code=404, detail="No results found on YouTube")

def download_audio(video_url):
    try:
        yt = YouTube(video_url)
        audio_stream = yt.streams.filter(only_audio=True).first()
        audio_buffer = io.BytesIO()
        audio_stream.stream_to_buffer(audio_buffer)
        audio_buffer.seek(0)
        print("sent the data converting audio buffer to download link")
        return audio_buffer
    except Exception as e:
        print("Error occurred:", str(e))
        raise HTTPException(status_code=500, detail="Error downloading audio")

@app.post("/downloadSong")
async def download_song(request: Request):
    data = await request.json()
    track_id = data.get('id')
    if not track_id:
        raise HTTPException(status_code=400, detail="Invalid track ID")

    track_details = get_track_details(track_id)
    song_name = track_details['name']
    main_artist = track_details['artists'].split(',')[0].strip()
    print(f"Searching for '{song_name}' by {main_artist} on YouTube...")

    try:
        search_query = f"{song_name} {main_artist} official audio"
        audio_buffer = search_and_download(search_query)
        headers = {
            'Content-Disposition': f'attachment; filename="{song_name}.mp3"'
        }
        # Return the audio buffer as a StreamingResponse
        return StreamingResponse(audio_buffer, headers=headers, media_type='audio/mpeg')
    except Exception as e:
        print(f"Error downloading '{song_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to download: {str(e)}")

@app.post("/downloadAllSongs")
async def download_all_songs(request: Request):
    data = await request.json()
    playlist_id = data.get('id')
    print(playlist_id)
    return {"message": "Download started"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Handle received messages
            if data.startswith("download:"):
                playlist_id = data.split("download:")[1]
                await websocket.send_text(f"Starting download for playlist: {playlist_id}")

                results = sp.playlist_tracks(playlist_id)
                tracks = results['items']
                while results['next']:
                    results = sp.next(results)
                    tracks.extend(results['items'])

                for track in tracks:
                    track_info = track['track']
                    song_name = track_info['name']
                    main_artist = track_info['artists'][0]['name']
                    search_query = f"{song_name} {main_artist} official audio"
                    try:
                        await websocket.send_text(f"Downloading: {song_name} by {main_artist}")
                        audio_buffer = search_and_download(search_query)
                        audio_bytes = audio_buffer.getvalue()
                        await websocket.send_bytes(audio_bytes)
                        await websocket.send_text(f"Downloaded: {song_name} by {main_artist}")
                        time.delay(5)
                    except Exception as e:
                        await websocket.send_text(f"Failed to download: {song_name} by {main_artist}, error: {str(e)}")
                await websocket.send_text(f"Downloaded all the Songs in the Playlist ")

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app)
