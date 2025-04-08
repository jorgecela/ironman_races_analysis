"""
Ironman Results Scraper.py

────────────────────────────────────────────────────────────────────────────
🏊 🚴 🏃 IRONMAN Race Results Scraper
────────────────────────────────────────────────────────────────────────────

🔍 What It Does:
---------------
This script automates the process of scraping detailed athlete results
from the official IRONMAN race results pages (e.g., https://www.ironman.com/races).
It handles:
- Multiple race dates per event (dropdown selection)
- Pagination through all result pages
- Various athlete result types (Finishers, DNF, DNS, DQ)
- Dynamic data extraction with retries and error handling

📥 What It Needs:
-----------------
- A CSV file (e.g., `all_ironman_races.csv`) with at least:
    - 'Race' — The name of the race
    - 'URL' — Direct race page URL (without "-results" suffix — script appends this if needed)
- Chrome WebDriver installed and accessible (tested with Selenium)

📤 What It Produces:
--------------------
- For each race, a CSV is saved to: `data/results/races/<race_name>.csv`
- Each CSV includes per-athlete results like:
    - Name, Designation (FINISHER, DNF, DNS, DQ)
    - Swim/Bike/Run/Transition/Finish times
    - Division, Gender, and Overall ranks (if available)

🧠 Features & Logic:
---------------------
- Headless-like navigation through race iframes and dropdowns
- Retries on failures (selectors, page reloads, pagination)
- Optional toggle for:
    - Showing 100 rows per page (SET_ROWS_TO_100)
    - Processing all pages vs. just the first (ENABLE_PAGINATION)
- Driver restarts after every race date to mitigate memory leaks

⚠️ Known Notes:
----------------
- Dynamic elements on the results page may cause intermittent failures
- Some races may not have results or may have iframe loading issues
- Network speed and WebDriver version can impact timing
- Always review logs to see if races failed and need reprocessing

────────────────────────────────────────────────────────────────────────────
"""


import os
import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# -----------------------
# Configurable Settings
# -----------------------

SET_ROWS_TO_100 = True      # Try to show 100 rows per page
ENABLE_PAGINATION = True    # Enable full table pagination

# -----------------------
# Load Race Data
# -----------------------

race_data = pd.read_csv("data/urls/all_ironman_races.csv")
race_data['URL'] = race_data['URL'].apply(
    lambda x: x.strip() + "-results" if isinstance(x, str) and not x.strip().endswith("-results") else x
)


# Ensure output directory exists
output_directory = "data/urls/all_ironman_races/"
os.makedirs(output_directory, exist_ok=True)

race_date_counter = 0  # Track how many race dates have been processed

# -----------------------
# Process Each Race
# -----------------------

for index, row in race_data.iterrows():
    race_url = row['URL']
    race_name = row['Race Name']
    print(f"\n📍 Processing: {race_name} | {race_url}")

    safe_race_name = re.sub(r'\W+', '_', race_name)
    csv_filename = os.path.join(output_directory, f"{safe_race_name}.csv")
    race_results = []

    # Start WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(race_url)

    try:
        # Switch into iframe
        iframe = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.coh-iframe"))
        )
        driver.get(iframe.get_attribute("src"))

        # Open dropdown and collect all race date options
        dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='combobox']"))
        )
        dropdown.click()

        options = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
        )
        race_dates = [option.text for option in options]
        print(f"🗓️ Found {len(race_dates)} race dates.")

        ActionChains(driver).send_keys(Keys.ESCAPE).perform()  # Close dropdown

        # -----------------------
        # Loop Through Race Dates
        # -----------------------

        for i in range(len(race_dates)):
            # Optional: Restart WebDriver every race date to clear memory
            if race_date_counter > 0 and race_date_counter % 1 == 0:
                print("🔄 Restarting driver to clear memory...")

                for attempt in range(10):
                    try:
                        driver.quit()
                        driver = webdriver.Chrome()
                        driver.maximize_window()
                        driver.get(race_url)

                        iframe = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.coh-iframe"))
                        )
                        driver.get(iframe.get_attribute("src"))
                        time.sleep(5)
                        break
                    except Exception as e:
                        print(f"⚠️ Retry {attempt+1} on driver restart failed: {str(e)[:100]}")
                        time.sleep(3)

            # Select race date
            for attempt in range(5):
                try:
                    dropdown = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='combobox']"))
                    )
                    dropdown.click()
                    options = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li[role='option']"))
                    )
                    current_option = options[i]
                    race_date_text = current_option.text
                    print(f"➡️ Selecting race date: {race_date_text}")
                    current_option.click()
                    time.sleep(1)
                    break
                except Exception as e:
                    print(f"Retry {attempt+1} on selecting race date failed: {str(e)[:100]}")
                    time.sleep(0.5)

            race_date_counter += 1

            # -----------------------
            # Set Table to 100 Rows
            # -----------------------
            if SET_ROWS_TO_100:
                for attempt in range(5):
                    try:
                        rows_dropdown = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.MuiTablePagination-select"))
                        )
                        rows_dropdown.click()
                        option_100 = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//li[contains(text(),'100')]"))
                        )
                        option_100.click()
                        print("📊 Set rows per page to 100.")
                        time.sleep(10)  # Wait for reload
                        break
                    except Exception as e:
                        print(f"Retry {attempt+1} on setting rows: {str(e)[:100]}")
                        time.sleep(0.5)

            # -----------------------
            # Loop Through Table Pages
            # -----------------------

            pagination_active = True
            while pagination_active:
                rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='row'][data-rowindex]"))
                )
                print(f"📋 Found {len(rows)} rows on this page.")

                # -----------------------
                # Process Each Athlete Row
                # -----------------------

                for row_number in range(len(rows)):

                    def get_text(xpath, retries=3, delay=0.5):
                        for attempt in range(retries):
                            try:
                                return driver.find_element(By.XPATH, xpath).text
                            except Exception:
                                time.sleep(delay)
                        return "N/A"

                    def get_text_by_data_field(row_index, field_name, retries=3, delay=0.5):
                        xpath_variants = [
                            f"//div[@data-rowindex='{row_index}']//div[@data-field='{field_name}']/p",
                            f"//div[@data-rowindex='{row_index}']//div[@data-field='{field_name}']/span/p"
                        ]
                        for attempt in range(retries):
                            for xpath in xpath_variants:
                                try:
                                    return driver.find_element(By.XPATH, xpath).text
                                except:
                                    continue
                            time.sleep(delay)
                        return "N/A"

                    for attempt in range(10):
                        try:
                            rows = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='row'][data-rowindex]"))
                            )
                            row = rows[row_number]
                            row_index = row.get_attribute("data-rowindex")
                            driver.execute_script("arguments[0].scrollIntoView(true);", row)
                            row.click()

                            designation = get_text("//h6[contains(text(),'Designation')]/preceding-sibling::h6")

                            # Handle different athlete result scenarios
                            if designation in {"DNS", "DQ"}:
                                race_results.append({
                                    "Race Name": race_name,
                                    "Race Date": race_date_text,
                                    "Athlete": get_text_by_data_field(row_index, "athlete"),
                                    "Designation": designation,
                                })

                            elif designation == "DNF":
                                race_results.append({
                                    "Race Name": race_name,
                                    "Race Date": race_date_text,
                                    "Athlete": get_text_by_data_field(row_index, "athlete"),
                                    "Designation": designation,
                                    "Swim Time": get_text_by_data_field(row_index, "wtc_swimtimeformatted"),
                                    "Transition 1": get_text_by_data_field(row_index, "wtc_transition1timeformatted"),
                                    "Bike Time": get_text_by_data_field(row_index, "wtc_biketimeformatted"),
                                    "Transition 2": get_text_by_data_field(row_index, "wtc_transitiontime2formatted"),
                                    "Run Time": get_text_by_data_field(row_index, "wtc_runtimeformatted"),
                                    "Finish Time": get_text_by_data_field(row_index, "wtc_finishtimeformatted"),
                                })

                            else:
                                race_results.append({
                                    "Race Name": race_name,
                                    "Race Date": race_date_text,
                                    "Athlete": get_text_by_data_field(row_index, "athlete"),
                                    "Div Rank": get_text("//h6[contains(text(),'Div Rank')]/preceding-sibling::h6"),
                                    "Gender Rank": get_text("//h6[contains(text(),'Gender Rank')]/preceding-sibling::h6"),
                                    "Overall Rank": get_text("//h6[contains(text(),'Overall Rank')]/preceding-sibling::h6"),
                                    "Designation": designation,
                                    "Division": get_text("//h6[contains(text(),'Division')]/preceding-sibling::h6"),
                                    "Swim Time": get_text_by_data_field(row_index, "wtc_swimtimeformatted"),
                                    "Transition 1": get_text_by_data_field(row_index, "wtc_transition1timeformatted"),
                                    "Bike Time": get_text_by_data_field(row_index, "wtc_biketimeformatted"),
                                    "Transition 2": get_text_by_data_field(row_index, "wtc_transitiontime2formatted"),
                                    "Run Time": get_text_by_data_field(row_index, "wtc_runtimeformatted"),
                                    "Finish Time": get_text_by_data_field(row_index, "wtc_finishtimeformatted"),
                                })

                            row.click()  # Close row
                            break
                        except Exception as e:
                            print(f"Retry {attempt+1} on row {row_number+1}: {str(e)[:100]}")
                            time.sleep(0.2)

                # -----------------------
                # Go to Next Page (if enabled)
                # -----------------------
                if ENABLE_PAGINATION:
                    for attempt in range(5):
                        try:
                            next_button = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Go to next page']"))
                            )
                            if "Mui-disabled" in next_button.get_attribute("class"):
                                pagination_active = False
                                break
                            next_button.click()
                            WebDriverWait(driver, 10).until(EC.staleness_of(rows[0]))
                            break
                        except:
                            time.sleep(0.2)
                    else:
                        pagination_active = False
                else:
                    pagination_active = False

        # -----------------------
        # Save Results for This Race
        # -----------------------

        df_race = pd.DataFrame(race_results)
        df_race.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        print(f"✅ Saved: {csv_filename}")

    except Exception as e:
        print(f"🚨 Error processing {race_url}: {str(e)[:100]}")
    finally:
        driver.quit()

print("\n🎉 All races processed!")
