from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
from datetime import datetime
import re

def initialize_driver():
    """Initialize Chrome WebDriver with appropriate options."""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    # Remove headless mode to ensure proper rendering
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    return webdriver.Chrome(options=options)

def parse_duration(duration_str):
    """Convert YouTube duration string to seconds."""
    if not duration_str or duration_str == "0:00":
        return 0
    
    duration_str = duration_str.strip()
    try:
        parts = duration_str.split(':')
        if len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    except (ValueError, IndexError):
        print(f"Failed to parse duration: {duration_str}")
    return 0

def parse_views(views_str):
    """Convert view count string to integer."""
    if not views_str:
        return 0
    
    views_str = views_str.lower().replace('views', '').replace(',', '').strip()
    if 'k' in views_str:
        return int(float(views_str.replace('k', '')) * 1000)
    elif 'm' in views_str:
        return int(float(views_str.replace('m', '')) * 1000000)
    try:
        return int(views_str)
    except ValueError:
        return 0

def ensure_element_visible(driver, element):
    """Ensure element is in viewport and visible."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Allow time for the element to become visible
    return element

def get_video_info(driver, video_element):
    """Extract all information for a single video."""
    try:
        # Ensure video element is visible
        ensure_element_visible(driver, video_element)
        
        # Get basic video information
        title = video_element.find_element(By.ID, "video-title").get_attribute("title")
        video_url = video_element.find_element(By.ID, "video-title").get_attribute("href")
        
        # Get channel information
        channel_element = video_element.find_element(By.CSS_SELECTOR, "ytd-channel-name")
        channel = channel_element.text.strip()
        
        # Get metadata (views and upload date)
        metadata = video_element.find_elements(By.CSS_SELECTOR, "#metadata-line span")
        views = metadata[0].text if len(metadata) > 0 else "0 views"
        upload_date = metadata[1].text if len(metadata) > 1 else "Unknown"
        
        # Get duration using JavaScript
        thumbnail = video_element.find_element(By.CSS_SELECTOR, "ytd-thumbnail")
        duration_element = thumbnail.find_element(By.CSS_SELECTOR, "span.ytd-thumbnail-overlay-time-status-renderer")
        
        # Force visibility of duration element
        driver.execute_script("""
            arguments[0].style.visibility = 'visible';
            arguments[0].style.display = 'block';
        """, duration_element)
        
        # Move mouse to thumbnail to trigger overlay
        ActionChains(driver).move_to_element(thumbnail).perform()
        time.sleep(0.5)  # Wait for overlay to appear
        
        duration = duration_element.text.strip()
        if not duration:
            # Try getting duration through JavaScript
            duration = driver.execute_script("return arguments[0].textContent;", duration_element)
        
        return {
            'title': title,
            'channel': channel,
            'views': parse_views(views),
            'duration': parse_duration(duration),
            'duration_str': duration,
            'upload_date': upload_date,
            'video_url': video_url
        }
    except Exception as e:
        print(f"Error extracting video info: {str(e)}")
        return None

def scrape_deepseek_videos():
    """Main function to scrape Deepseek videos from YouTube."""
    driver = initialize_driver()
    videos_data = []
    
    try:
        # Navigate to YouTube search with filters
        search_query = "Deepseek"
        driver.get(f'https://www.youtube.com/results?search_query={search_query}&sp=EgIIBQ%253D%253D')
        
        # Wait for page to load completely
        time.sleep(5)
        
        # Scroll and collect videos
        videos_found = 0
        scroll_attempts = 0
        max_scroll_attempts = 15  # Increased scroll attempts
        
        while videos_found < 25 and scroll_attempts < max_scroll_attempts:
            # Find video elements
            video_elements = driver.find_elements(By.TAG_NAME, "ytd-video-renderer")
            
            for video in video_elements[videos_found:]:
                video_info = get_video_info(driver, video)
                
                if video_info:
                    print(f"\nProcessed video: {video_info['title']}")
                    print(f"Duration: {video_info['duration_str']} ({video_info['duration']} seconds)")
                    print(f"Channel: {video_info['channel']}")
                    videos_data.append(video_info)
                    videos_found += 1
                    
                    if videos_found >= 25:
                        break
            
            if videos_found < 25:
                # Scroll down
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(2)
                scroll_attempts += 1
    
    except Exception as e:
        print(f"An error occurred during scraping: {str(e)}")
    
    finally:
        driver.quit()
    
    return pd.DataFrame(videos_data)

def analyze_videos(df):
    """Analyze the scraped video data."""
    if df.empty:
        return {
            'most_viewed_video': None,
            'average_duration': '00:00:00'
        }
    
    # Find most viewed video
    most_viewed = df.loc[df['views'].idxmax()]
    
    # Calculate average duration
    avg_duration = df['duration'].mean()
    
    # Convert average duration to HH:MM:SS format
    avg_duration_formatted = time.strftime('%H:%M:%S', time.gmtime(avg_duration))
    
    return {
        'most_viewed_video': {
            'title': most_viewed['title'],
            'views': most_viewed['views'],
            'channel': most_viewed['channel'],
            'duration': most_viewed['duration_str']
        },
        'average_duration': avg_duration_formatted
    }

def main():
    print("Starting video scraping...")
    print("Note: Browser will be visible to ensure proper rendering of elements")
    
    df = scrape_deepseek_videos()
    
    if df.empty:
        print("No videos were found. Please check your internet connection and try again.")
        return
    
    print("\nAnalyzing video data...")
    analysis = analyze_videos(df)
    
    # Save to CSV
    filename = f"deepseek_videos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"\nData saved to {filename}")
    
    # Print analysis results
    print("\nAnalysis Results:")
    print(f"Most viewed video: {analysis['most_viewed_video']['title']}")
    print(f"by {analysis['most_viewed_video']['channel']}")
    print(f"with {analysis['most_viewed_video']['views']:,} views")
    print(f"Duration: {analysis['most_viewed_video']['duration']}")
    print(f"Average video duration: {analysis['average_duration']}")
    
    # Print duration statistics
    print("\nDuration Statistics:")
    print(f"Number of videos with duration: {(df['duration'] > 0).sum()}")
    print(f"Number of videos without duration: {(df['duration'] == 0).sum()}")
    print("\nSample of durations:")
    print(df[['title', 'duration_str', 'duration']].head())

if __name__ == "__main__":
    main()
