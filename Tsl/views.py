from django.shortcuts import render
import requests
import logging
import json
import os
from urllib.parse import urljoin
from requests.exceptions import RequestException
from django.contrib.auth import logout
from Accounts.models import Slider,Highlight,Blog,LatestEvent,LatestEventHighlight,Media,Showcase,Trending_now,FeaturedShow
from bs4 import BeautifulSoup

# Replace with your actual Google API key securely
api_key = 'AIzaSyCSexVrBoINLvu9y1WNeifx6wyjU8mQ7_Y'  # Example Google API key for YouTube Data API v3

# Set up logger
logger = logging.getLogger(__name__)


def scrape_news(url, article_selector, title_selector, link_selector, image_selector):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.vanguardngr.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 403:
            print(f"Access denied to {url}")
            return []  # Return empty list if blocked
        
        response.raise_for_status()  # Raise HTTPError for bad responses
        soup = BeautifulSoup(response.content, 'html.parser')

        print(f"Scraping {url}...")

        articles = soup.select(article_selector)
        news = []
        
        for article in articles:
            try:
                title = article.select_one(title_selector).get_text(strip=True)
                link = urljoin(url, article.select_one(link_selector)['href'])

                image_element = article.select_one(image_selector)
                image = None
                if image_element:
                    if 'src' in image_element.attrs and image_element['src'].startswith('http'):
                        image = urljoin(url, image_element['src'])
                    elif 'data-src' in image_element.attrs and image_element['data-src'].startswith('http'):
                        image = urljoin(url, image_element['data-src'])
                    elif 'srcset' in image_element.attrs:
                        srcset_parts = image_element['srcset'].split(',')
                        for part in srcset_parts:
                            image_url = part.strip().split(' ')[0]
                            if image_url.startswith('http'):
                                image = urljoin(url, image_url)
                                break

                if title and link:
                    if image:
                        news.append({'title': title, 'link': link, 'image': image})
                    else:
                        news.append({'title': title, 'link': link, 'image': None})
                else:
                    print(f"Skipping article with incomplete data: title={title}, link={link}, image={image}")
            except AttributeError as e:
                print(f"Error parsing article from {url}: {e}")
        
        print(f"Scraped {len(news)} articles from {url}")
        return news
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while scraping {url}: {http_err}")
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return []


def home(request):
    sliders = Slider.objects.filter(is_active=True).order_by('order')
    highlights = Highlight.objects.all()
    grouped_images = Trending_now.objects.order_by('Trend_order')
    Trending_Now = [grouped_images[i:i + 4] for i in range(0, len(grouped_images), 4)]  # Group into chunks of 4
    featured_shows = FeaturedShow.objects.all()
    
    # Define the websites and their CSS selectors for scraping
    news_sources = [
        {
            'url': 'https://www.vanguardngr.com/',
            'article_selector': 'article.entry',
            'title_selector': 'h3.entry-title a',
            'link_selector': 'h3.entry-title a',
            'image_selector': 'img.entry-thumbnail'
        },
    ]

    blogs = []

    # Scrape news from each source
    for source in news_sources:
        news = scrape_news(
            url=source['url'],
            article_selector=source['article_selector'],
            title_selector=source['title_selector'],
            link_selector=source['link_selector'],
            image_selector=source['image_selector']
        )
        blogs.extend(news)

    # Separate the blogs into two distinct sections
    blog_news = blogs[:6]  # First 6 for the main Blog News section
    trending_articles = blogs[6:11]  # Next 5 for the Trending Articles section

    return render(request, 'index.html', {
        'sliders': sliders,
        'highlights': highlights,
        'blogs': blog_news,  # Pass main blog news separately
        'trending_articles': trending_articles,  # Pass trending articles separately
        'Trending_Now': Trending_Now,  # Pass grouped Trending Now images
        'featured_shows': featured_shows,
    })


def get_videos_from_channel(channel_id, api_key):
    # YouTube API URL to get channel data
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&channelId={channel_id}&order=date&maxResults=10&key={api_key}'

    try:
        # Send GET request to YouTube API to fetch channel video data
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for HTTP error responses

        data = response.json()  # Parse the JSON response

        # Initialize the structure to store videos, live, upcoming, and playlists
        all_videos = {
            "live": None,         # Most recent live video (if available)
            "videos": [],         # Non-live videos
            "upcoming": [],       # Upcoming videos
        }

        # Check if 'items' exists and loop through the response data
        if 'items' in data and data['items']:
            # Separate videos into live, upcoming, and non-live
            for item in data['items']:
                live_status = item['snippet'].get('liveBroadcastContent', 'none')
                logger.debug(f"Video: {item['snippet']['title']} - Status: {live_status}")

                video_id = item.get('id', {}).get('videoId')  # Safely extract video ID

                if not video_id:
                    continue  # Skip items without a valid video ID

                if live_status == 'live':
                    all_videos['live'] = item  # Store the live video
                elif live_status == 'upcoming':
                    all_videos['upcoming'].append(item)  # Store upcoming videos
                elif live_status == 'none':
                    all_videos['videos'].append(item)  # Add non-live videos to the regular video list

        # Log the categorized videos for debugging
        logger.debug(f"Categorized videos: {all_videos}")

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
    logger.error(f"Upcoming videos: {videos_data['upcoming']}")  # Log upcoming videos

    # Helper function to extract video ID safely
    def get_video_id(video):
        return video.get('id', {}).get('videoId')

    # Determine the video ID to use for the live stream section
    live_video_id = (
        get_video_id(videos_data['live'])
        if videos_data['live']  # Use live video if available
        else (get_video_id(videos_data['videos'][0]) if videos_data['videos'] else None)  # Fall back to the most recent video
    )

    # Prepare the list of the first 4 videos (or fewer, depending on the available data)
    recent_videos = [
        video for video in videos_data['videos'] if get_video_id(video)
    ][:4]  # Ensure only valid videos are used

    # Create a list of empty card placeholders if there are fewer than 4 videos
    empty_cards = [''] * (4 - len(recent_videos))

    return render(request, 'live_tv.html', {
        'live_video_id': live_video_id,  # Pass the determined video ID
        'recent_videos': recent_videos,  # Pass the recent 4 videos
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

