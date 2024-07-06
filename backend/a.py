from pytube import YouTube
from youtube_search import YoutubeSearch

def search_and_download(query):
    # Search for the video using the query
    results = YoutubeSearch(query, max_results=1).to_dict()
    
    # Check if any results are found
    if results:
        # Extract the first video URL from the search results
        video_url = "https://www.youtube.com" + results[0]['url_suffix']
        
        # Download the video
        download_video(video_url)
    else:
        print("No results found for the query:", query)

def download_video(video_url):
    try:
        # Create a YouTube object with the video URL
        yt = YouTube(video_url)
        
        # Select the highest resolution stream
        stream = yt.streams.get_highest_resolution()
        
        # Download the video
        stream.download()
        
        print("Download completed successfully!")
    except Exception as e:
        print("Error occurred:", str(e))

if __name__ == "__main__":
    # Input the search query
    query = input("Enter the search query: ")
    
    # Search and download the video
    search_and_download(query)
