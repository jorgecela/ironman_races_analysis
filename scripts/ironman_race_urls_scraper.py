"""
scrape_ironman_races.py

This script scrapes all Ironman races listed on https://www.ironman.com/races.
For each race, it collects:
- Race name and type (IRONMAN, 70.3, 5150, etc.)
- Location
- Race URL
- Swim, Bike, Run terrain types (if available)

The full race list is saved as 'all_ironman_races.csv'.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# -----------------------
# Setup
# -----------------------

driver = webdriver.Chrome()
driver.maximize_window()
driver.get("https://www.ironman.com/races")
wait = WebDriverWait(driver, 20)
race_data = []


# -----------------------
# Race Extraction Function
# -----------------------

def extract_races():
    """
    Extracts race information from currently loaded race cards.
    Appends results to the global race_data list.
    """
    wrappers = driver.find_elements(By.CSS_SELECTOR, ".highlighted-card-wrapper")

    for wrapper in wrappers:
        try:
            title = wrapper.find_element(By.TAG_NAME, "h2").text.strip()
            location = wrapper.find_element(By.CSS_SELECTOR, ".country-flag-formatter .label").text.strip()
            url = wrapper.find_element(By.CSS_SELECTOR, "a.button--secondary").get_attribute("href")

            # Determine race type based on title content
            if "5150" in title:
                race_type = "5150 Triathlon Series"
            elif "70.3" in title:
                race_type = "IRONMAN 70.3"
            elif "4:18:4" in title:
                race_type = "4:18:4"
            else:
                race_type = "IRONMAN"

            # Default values
            swim_type = bike_type = run_type = ""

            # Extract terrain types from icons
            icon_fields = wrapper.find_elements(By.CLASS_NAME, "icon-field-item")
            for field in icon_fields:
                try:
                    label = field.find_element(By.CLASS_NAME, "icon-field-label").text.strip().lower()
                    value = field.find_element(By.CLASS_NAME, "icon-field-value").text.strip()

                    if "swim" in label:
                        swim_type = value
                    elif "bike" in label:
                        bike_type = value
                    elif "run" in label:
                        run_type = value
                except:
                    # Skip silently if field extraction fails
                    continue

            # Append result
            race_data.append({
                "Race Name": title,
                "Race Type": race_type,
                "Location": location,
                "URL": url,
                "Swim": swim_type,
                "Bike": bike_type,
                "Run": run_type
            })

        except Exception as e:
            print(f"⚠️ Error parsing race card: {e}")


# -----------------------
# Main Scraper Logic
# -----------------------

# Wait for initial content to load and extract
wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "highlighted-card-wrapper")))
extract_races()

# Paginate through all races using "Load More"
while True:
    try:
        current_count = len(driver.find_elements(By.CLASS_NAME, "highlighted-card-wrapper"))

        # Locate and scroll to Load More button
        load_more_btn = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.text-link--chevron-down[rel='next']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", load_more_btn)
        time.sleep(1)

        # Click using JavaScript
        driver.execute_script("arguments[0].click();", load_more_btn)

        # Wait until new race cards appear
        max_retries = 10
        for _ in range(max_retries):
            time.sleep(2.5)
            new_count = len(driver.find_elements(By.CLASS_NAME, "highlighted-card-wrapper"))
            if new_count > current_count:
                print(f"✅ Loaded more races: {new_count - current_count} new")
                break
        else:
            print("⏳ Waited but no new races loaded.")
            break

        extract_races()

    except Exception as e:
        print("🚫 No more races to load or error occurred.")
        break

# -----------------------
# Save Data
# -----------------------

df = pd.DataFrame(race_data).drop_duplicates()
df.to_csv("all_ironman_races.csv", index=False, encoding="utf-8-sig")
print("✅ Races saved to 'all_ironman_races.csv'")

# -----------------------
# Cleanup
# -----------------------

driver.quit()
