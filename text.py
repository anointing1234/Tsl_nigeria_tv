import requests

api_key = "YOUR_GOOGLE_API_KEY"  # Replace with your API key
channel_id = "UC2eJZ7eVkmzgOP8TMPLqaqA"  # Replace with the channel ID
url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=10&key={api_key}"

response = requests.get(url)
print(response.json())
