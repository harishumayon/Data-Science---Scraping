import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")  # Open browser in full-screen
options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent bot detection

# Initialize WebDriver
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Open YouTube & search for "Deepseek"
driver.get("https://www.youtube.com")
time.sleep(2)

search_box = driver.find_element(By.NAME, "search_query")
search_box.send_keys("Deepseek")
search_box.send_keys(Keys.RETURN)
time.sleep(3)

# Apply "This Year" filter
try:
    filter_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(@aria-label, "Filters")]')))
    driver.execute_script("arguments[0].scrollIntoView();", filter_button)
    filter_button.click()
    time.sleep(2)

    this_year_filter = wait.until(EC.element_to_be_clickable((By.XPATH, '//yt-formatted-string[text()="This year"]')))
    this_year_filter.click()
    time.sleep(3)
except Exception as e:
    print("⚠️ Filter button not found or YouTube blocked automation:", e)

# Scroll down dynamically to load more videos
num_videos_needed = 25
video_data = []
scroll_pause_time = 2

while len(video_data) < num_videos_needed:
    driver.execute_script("window.scrollBy(0, 2000);")
    time.sleep(scroll_pause_time)

    # Extract video elements
    videos = driver.find_elements(By.XPATH, '//ytd-video-renderer')[:num_videos_needed]
    
    for video in videos:
        try:
            title = video.find_element(By.XPATH, './/h3/a').text
            try:
                channel = video.find_element(By.XPATH, './/ytd-channel-name//a').text  
            except:
                channel = "Unknown Channel"

            views = video.find_element(By.XPATH, './/span[contains(text(), "views")]').text
            upload_date = video.find_element(By.XPATH, './/div[@id="metadata-line"]/span[2]').text
            try:
                duration = video.find_element(By.XPATH, './/span[contains(@class, "time-status")]').text.strip()
            except:
                duration = "Unknown"

            video_url = video.find_element(By.TAG_NAME, "a").get_attribute("href")

            # Open the video page in the same window
            driver.get(video_url)
            time.sleep(3)

            try:
                description = driver.find_element(By.XPATH, '//yt-formatted-string[@id="description"]').text
            except:
                description = "No description available."

            video_data.append({
                "Title": title,
                "Channel": channel,
                "Views": views,
                "Upload Date": upload_date,
                "Duration": duration,
                "Description": description,
                "URL": video_url
            })

            # Go back to search results
            driver.back()
            time.sleep(3)

            if len(video_data) >= num_videos_needed:
                break
        except Exception as e:
            print("⚠️ Error extracting video details:", e)
            continue

# Convert to Pandas DataFrame
df = pd.DataFrame(video_data)

# Save data to CSV
df.to_csv("youtube_trending.csv", index=False)
print("✅ Data saved to youtube_trending.csv!")

# Data Cleaning
df["Views"] = df["Views"].str.replace(" views", "", regex=True).str.replace(",", "", regex=True)
df["Views"] = pd.to_numeric(df["Views"], errors="coerce").fillna(0).astype(int)

# Convert Duration to minutes
duration_extracted = df["Duration"].str.extract(r'(?:(\d+):)?(\d+)')  # Extract minutes and seconds
df["Duration (mins)"] = duration_extracted[0].fillna(0).astype(float) + duration_extracted[1].astype(float) / 60

# Debugging: Print top 5 videos sorted by views
print("\n🔍 Top 5 Videos by Views:")
print(df.sort_values(by="Views", ascending=False).head())

# Find most viewed video
most_viewed = df.loc[df["Views"].idxmax()]
average_duration = df["Duration (mins)"].mean()

print("\n🔍 **Analysis**:")
print(f"🎥 Most Viewed Video: {most_viewed['Title']} ({most_viewed['Views']} views)")
print(f"⏳ Average Duration: {average_duration:.2f} minutes")

# Close browser
driver.quit()
