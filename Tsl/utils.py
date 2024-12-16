# import requests

# # api_key = 'AIzaSyCSexVrBoINLvu9y1WNeifx6wyjU8mQ7_Y'  # Replace with your actual Google API key
# # channel_id = 'UC2eJZ7eVkmzgOP8TMPLqaqA'   # Example YouTube Channel ID

# logger.error(f"Fetching videos for channel ID: {channel_id}")  # Log the channel ID being used


# def get_videos_from_channel(channel_id, api_key):
#     # Google YouTube Data API v3 URL to get channel metadata
#     url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"

#     all_videos = {
#         "live": None,  # We only need the first live video
#         "videos": [],
#         "playlists": []
#     }

#     try:
#         # Send GET request to Google's YouTube API to fetch channel data
#         response = requests.get(url)
#         response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        
#         data = response.json()  # Parse the JSON response

#         # Check if 'items' data is available in the response
#         if 'items' in data and len(data['items']) > 0:
#             # Get the channel's playlist ID for uploaded videos
#             uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']

#             # Now, get the videos from the uploads playlist
#             videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&maxResults=5&key={api_key}"
#             videos_response = requests.get(videos_url)
#             videos_response.raise_for_status()

#             videos_data = videos_response.json()

#             # Check if 'items' contains video data
#             if 'items' in videos_data:
#                 all_videos['videos'] = [{
#                     "video_id": video['snippet']['resourceId']['videoId'],
#                     "title": video['snippet']['title'],
#                     "url": f"https://www.youtube.com/watch?v={video['snippet']['resourceId']['videoId']}"
#                 } for video in videos_data['items']]

#             # Optional: Fetch the live stream data (if available)
#             # You can extend this part as needed based on the specific requirements
#             live_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&eventType=live&type=video&key={api_key}"
#             live_response = requests.get(live_url)
#             live_response.raise_for_status()

#             live_data = live_response.json()
#             if 'items' in live_data and len(live_data['items']) > 0:
#                 all_videos['live'] = {
#                     "id": live_data['items'][0]['id']['videoId'],
#                     "title": live_data['items'][0]['snippet']['title'],
#                     "url": f"https://www.youtube.com/watch?v={live_data['items'][0]['id']['videoId']}"
#                 }

#         return all_videos

#     except requests.exceptions.RequestException as e:
#         # Handle errors in the request, such as connectivity issues
#         print(f"Error fetching data from YouTube API: {e}")
#         return {"error": "Failed to fetch videos from YouTube API"}


# videos = get_videos_from_channel(channel_id, api_key)

# print(videos)
