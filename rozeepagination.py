from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd
from collections import Counter
import re

# Initialize WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open Rozee.pk job search page
url = "https://www.rozee.pk/search/result?q=Software+Engineer&l=Pakistan"
driver.get(url)

# Wait for jobs section to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "jobs")))

job_list = []
job_links = set()  # To avoid duplicates
max_jobs = 30

while len(job_list) < max_jobs:
    job_cards = driver.find_elements(By.XPATH, '//*[@id="jobs"]//div[contains(@class, "job")]')

    for job in job_cards:
        if len(job_list) >= max_jobs:
            break
        
        try:
            job_title = job.find_element(By.XPATH, './/h3[@class="s-18"]/a/bdi').text
            company_name = job.find_element(By.XPATH, './/bdi[@class="float-left"]/a[contains(@class, "display-inline")]').text
            city = job.find_elements(By.XPATH, './/bdi[@class="float-left"]/a[contains(@class, "display-inline")]')[1].text
            job_link = job.find_element(By.XPATH, './/h3[@class="s-18"]/a').get_attribute("href")
            
            if job_link not in job_links:  # Avoid duplicates
                job_links.add(job_link)
                job_list.append({
                    "Job Title": job_title,
                    "Company": company_name,
                    "City": city,
                    "Job Link": job_link
                })
        except:
            continue

    # Try to find and click the "Next" button if available
    try:
        next_button = driver.find_element(By.XPATH, '//a[@class="next" and @href="javascript:;"]')
        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(3)  # Wait for next page to load
    except:
        print("✅ No more pages to navigate.")
        break

# Now visit each job link and extract additional details
for index, job in enumerate(job_list):
    driver.get(job["Job Link"])
    time.sleep(2)

    print(f"🔄 Extracting details for job {index+1} of {len(job_list)}: {job['Job Title']}")

    # Extract Required Skills
    try:
        skills_elements = driver.find_elements(By.XPATH, '//div[@class="jcnt font16"]/a')
        job["Skills"] = ", ".join([skill.text.strip() for skill in skills_elements])
    except:
        job["Skills"] = "Not Found"

    # Extract Job Type
    try:
        job_type_elements = driver.find_elements(By.XPATH, '//div[contains(@class, "col-lg-7")]/a[contains(@class, "jblk")]')
        job_types = []

        for jt in job_type_elements:
            text = jt.text.strip()
            if text and text not in job_types:
                job_types.append(text)
            if len(job_types) == 2:  # Stop if we already have 2 job types
                break

        job["Job Type"] = " / ".join(job_types) if job_types else "Not Found"
    except:
        job["Job Type"] = "Not Found"

    # Extract Salary
    try:
        salary_element = driver.find_element(By.XPATH, '//div[contains(@class, "mrsl mt10 ofa font18 text-right text-dark d-flex align-items-center")]')
        job["Salary"] = salary_element.text.strip()
    except:
        job["Salary"] = "Not Found"

# Convert to Pandas DataFrame
df = pd.DataFrame(job_list)

# Identify Most Common Job Titles
job_title_counts = Counter(df["Job Title"])
top_job_titles = job_title_counts.most_common(5)

# Identify Most Frequently Required Skills
all_skills = []
for skills in df["Skills"]:
    if skills != "Not Found":
        all_skills.extend(skills.split(", "))

skill_counts = Counter(all_skills)
top_skills = skill_counts.most_common(10)

# Calculate Average Salary for Lahore Jobs
lahore_salaries = []
for _, row in df[df["City"].str.contains("Lahore", case=False, na=False)].iterrows():
    salary_text = row["Salary"]
    if salary_text != "Not Found":
        salary_numbers = re.findall(r'\d+', salary_text.replace(",", ""))  # Extract numbers
        if salary_numbers:
            avg_salary = sum(map(int, salary_numbers)) / len(salary_numbers)  # Average if range
            lahore_salaries.append(avg_salary)

average_salary_lahore = sum(lahore_salaries) / len(lahore_salaries) if lahore_salaries else "Not Available"

# Save data to CSV
df.to_csv("rozee_jobs.csv", index=False)

# Print Results
print("\n✅ Job scraping complete! Data saved to 'rozee_jobs.csv'.")
print("\n📌 Top 5 Most Common Job Titles:")
for title, count in top_job_titles:
    print(f"- {title}: {count} listings")

print("\n🔥 Top 10 Most In-Demand Skills:")
for skill, count in top_skills:
    print(f"- {skill}: {count} times")

print(f"\n💰 Average Salary for Jobs in Lahore: {average_salary_lahore}")

# Close browser
driver.quit()
