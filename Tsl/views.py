from django.shortcuts import render
import requests
import logging
from django.contrib.auth import logout
from Accounts.models import Slider,Highlight,Blog,LatestEvent,LatestEventHighlight,Media,Showcase

# Replace with your actual Google API key securely
api_key = 'AIzaSyCSexVrBoINLvu9y1WNeifx6wyjU8mQ7_Y'  # Example Google API key for YouTube Data API v3

# Set up logger
logger = logging.getLogger(__name__)

def home(request):
    sliders = Slider.objects.filter(is_active=True).order_by('order')
    highlights =  Highlight.objects.all()
    blogs = Blog.objects.all()
    return render(request, 'index.html',{
        'sliders': sliders,
        'highlights':highlights,
        'blogs': blogs,
        }) 


def get_videos_from_channel(channel_id, api_key):
    # YouTube API URL to get channel data
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&maxResults=5&key={api_key}'

    try:
        # Send GET request to YouTube API to fetch channel video data
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP error responses
        
        data = response.json()  # Parse the JSON response

        # Initialize the structure to store videos, live, and playlists
        all_videos = {
            "live": None,  # Most recent live video (if available)
            "videos": [],  # Non-live videos
            "playlists": []  # Playlists if any
        }

        # Check if 'items' exists and loop through the response data
        if 'items' in data and data['items']:
            # Lists to keep track of live, upcoming, and non-live video candidates
            live_video_candidates = []
            past_live_video_candidates = []

            # Separate videos into live, past live, and non-live
            for item in data['items']:
                live_status = item['snippet'].get('liveBroadcastContent', 'none')
                
                if live_status == 'live':
                    live_video_candidates.append(item)  # Collect live videos
                elif live_status == 'upcoming':
                    all_videos['videos'].append(item)  # Store upcoming videos
                elif live_status == 'none':
                    # For non-live videos, check if they were previously live (to display later)
                    past_live_video_candidates.append(item)

            # If there are any live video candidates, choose the most recent one
            if live_video_candidates:
                live_video_candidates.sort(key=lambda x: x['snippet']['publishedAt'], reverse=True)
                all_videos['live'] = live_video_candidates[0]  # Get the most recent live video
            elif past_live_video_candidates:
                # If no live video, show the most recent past live video
                past_live_video_candidates.sort(key=lambda x: x['snippet']['publishedAt'], reverse=True)
                all_videos['live'] = past_live_video_candidates[0]  # Get the most recent past live video

        return all_videos

    except requests.exceptions.RequestException as e:
        # Handle errors in the request, such as connectivity issues
        logger.error(f"Error fetching data from YouTube API: {e}")
        return {"error": "Failed to fetch videos from YouTube API"}


def live_tv(request):
    channel_id = 'UC2eJZ7eVkmzgOP8TMPLqaqA'  # Example YouTube Channel ID

    logger.error(f"Fetching videos for channel ID: {channel_id}")  # Log the channel ID being used

    # Call the function to fetch video data from the YouTube channel
    videos_data = get_videos_from_channel(channel_id, api_key)

    # If there's an error, handle it accordingly
    if 'error' in videos_data:
        logger.error(f"Error fetching videos: {videos_data['error']}")  # Log the error message
        return render(request, 'live_tv.html', {'error': videos_data['error'], 'channel_id': channel_id})

    # Log the data retrieved from the API for debugging
    logger.error(f"Live video: {videos_data['live']}")  # Log live video data
    logger.error(f"Videos: {videos_data['videos']}")  # Log regular videos data

    # Calculate remaining cards needed (if there are less than 3 videos)
    remaining_cards = 3 - len(videos_data['videos'])

    # Create a list of empty card placeholders based on remaining cards
    empty_cards = [''] * remaining_cards

    return render(request, 'live_tv.html', {
        'live_video_id': videos_data['live']['id']['videoId'] if videos_data['live'] else None,  # Pass live video ID
        'videos': videos_data['videos'],  # Pass other videos
        'channel_id': channel_id,  # Pass the channel ID for YouTube icon fallback
        'empty_cards': empty_cards,  # Pass the list of empty cards
    })



def ondemand(request):
    sliders = Slider.objects.filter(is_active=True).order_by('order')
    events = LatestEvent.objects.all()
    highlights = LatestEventHighlight.objects.all()
    showcases = Showcase.objects.all().order_by('display_order')
    media_items = Media.objects.all().order_by('display_order')
    return render(request, 'ondemand.html',{
        'sliders': sliders,
        'events': events,
        'highlights': highlights,
        'showcases': showcases,
        'media_items': media_items,
        })


def contact(request):
    return render(request, 'contact.html')


def About(request):
    return render(request, 'about.html')


def login(request):
    return render(request, 'forms/login.html')

def signup(request):
    return render(request,'forms/signup.html')

def send_pass(request):
    return render(request,'forms/send_password_reset.html')

def reset_pass(request):
    return render(request,'forms/reset_password.html')

