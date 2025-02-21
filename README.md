# Data Science Scraping Repository

This repository contains three web scraping scripts using **Selenium** and **Pandas** to extract data from different websites. The scripts automate data collection, process the extracted data, and save it for further analysis.

## Table of Contents
- [Project Overview](#project-overview)
- [Installation](#installation)
- [Scripts](#scripts)
  - [Rozee Job Scraper (rozeepagination.py)](#rozee-job-scraper-rozeepaginationpy)
  - [Lama Retail Scraper (lama.py)](#lama-retail-scraper-lamapy)
  - [YouTube Video Scraper (youtube.py)](#youtube-video-scraper-youtubepy)
- [Dependencies](#dependencies)
- [Usage](#usage)
- [Output](#output)
- [License](#license)

---

## Project Overview
This project consists of three separate web scraping scripts:
1. **Rozee.pk Job Scraper:** Extracts job listings, job details, and salary insights from Rozee.pk.
2. **Lama Retail Scraper:** Scrapes product details from **LamaRetail.com** across different categories.
3. **YouTube Video Scraper:** Extracts video data, views, duration, and upload details for a specific keyword from YouTube.

---

## Installation
Before running the scripts, install the required dependencies:
```sh
pip install selenium pandas webdriver-manager
```
Ensure you have **Google Chrome** installed and the **Chrome WebDriver** compatible with your Chrome version.

---

## Scripts

### 1️⃣ Rozee Job Scraper (`rozeepagination.py`)
**Description:**
- Scrapes job postings from **Rozee.pk** based on the query **Software Engineer**.
- Extracts job title, company, location, job link, skills, job type, and salary.
- Saves data in a CSV file.

**How to Run:**
```sh
python rozeepagination.py
```

**Output:**
- `rozee_jobs.csv` containing job details.
- Displays most common job titles, top skills, and average salary in Lahore.

---

### 2️⃣ Lama Retail Scraper (`lama.py`)
**Description:**
- Scrapes products from **LamaRetail.com** across different categories.
- Extracts product name, price, category, and availability.
- Saves data in a CSV file.

**How to Run:**
```sh
python lama.py
```

**Output:**
- `product_data.csv` containing product details.
- Displays average price per category.

---

### 3️⃣ YouTube Video Scraper (`youtube.py`)
**Description:**
- Searches for videos on YouTube with the keyword **Deepseek**.
- Extracts title, channel name, views, duration, and upload date.
- Saves data in a CSV file.

**How to Run:**
```sh
python youtube.py
```

**Output:**
- `deepseek_videos_<timestamp>.csv` containing video details.
- Displays the most viewed video and average video duration.

---

## Dependencies
Ensure you have the following installed:
- **Python 3.x**
- Selenium
- Pandas
- WebDriver Manager
- Google Chrome (latest version)

Install dependencies using:
```sh
pip install -r requirements.txt
```

---

## Usage
1. Clone the repository:
```sh
git clone https://github.com/your-username/data-science-scraping.git
cd data-science-scraping
```
2. Install dependencies.
3. Run any script as needed.

---

## Output
Each script saves the extracted data as a **CSV file** for easy analysis. The files include structured data such as job listings, product details, and YouTube video insights.

---

## License
This project is licensed under the MIT License.

---

### 🚀 Happy Scraping! 🚀

