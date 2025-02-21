import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize WebDriver
driver = webdriver.Chrome()

# Define categories and their URLs (update with actual URLs)
categories = {
    "Women": "https://lamaretail.com/collections/woman",
    "Men": "https://lamaretail.com/collections/man",
    "Shoes": "https://lamaretail.com/collections/shoes",
    "Accessories": "https://lamaretail.com/collections/accessories",
    # "Fragrance": "https://lamaretail.com/collections/fragrance"
}

product_data = []

for category, url in categories.items():
    print(f"Scraping category: {category}")
    driver.get(url)
    time.sleep(3)  # Wait for page to load
    
    # Scroll dynamically to load more products
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Give time for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    # Extract product links
    product_elements = driver.find_elements(By.CSS_SELECTOR, "div.grid-product__content a")
    # change this to 10, used 1 for quicker scraping testing
    product_links = [product.get_attribute("href") for product in product_elements[:5]] 

    for link in product_links:
        driver.get(link)
        time.sleep(3)

        # Extract price
        try:
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-product-price] span.money"))
            )
            price = price_element.text.strip()
        except:
            price = "N/A"

        # Append extracted data
        product_data.append({
            "Category": category,
            "Link": link,
            "Price": price,
            "Discount": "No Discount",
            "Brand": "N/A",
            "Available": 1
        })

    print(f"Extracted {len(product_links)} products from {category}")

# Store in Pandas DataFrame
df = pd.DataFrame(product_data)

# Compute average price per category
df["Price"] = df["Price"].str.replace("Rs.", "").str.replace(",", "")
df["Price"] = pd.to_numeric(df["Price"], errors='coerce').fillna(0.0)
avg_price = df.groupby("Category")["Price"].mean()

# Save dataset to CSV
df.to_csv("product_data.csv", index=False)

# Print results
print(df.head())
print("\nAverage Price Per Category:\n", avg_price)

# Close browser
driver.quit()
