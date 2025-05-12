import csv
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

SEARCH_URL = 'https://www.olx.in/items/q-car-cover'
OUTPUT_FILE = 'car_cover_listings.csv'
REMOTE_DEBUGGING_PORT = 9222
LOAD_MORE_SELECTOR = 'button[data-aut-id="btnLoadMore"]'
ITEM_SELECTOR = 'ul[data-aut-id="itemsList1"] li[data-aut-category-id="1585"]'


def init_driver(headless=False):
    options = Options()
    options.add_argument(f'--remote-debugging-port={REMOTE_DEBUGGING_PORT}')
    if headless:
        options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('debuggerAddress', f'localhost:{REMOTE_DEBUGGING_PORT}')
    return webdriver.Chrome(options=options)


def parse_listing(li):
    def get_text(selector):
        try:
            return li.find_element(By.CSS_SELECTOR, selector).text.strip().lower()
        except:
            return ''

    price = get_text('span[data-aut-id="itemPrice"]')
    title = get_text('span[data-aut-id="itemTitle"]')

    location = ''
    date_text = ''
    try:
        loc_date = li.find_element(By.CSS_SELECTOR, 'div._3rmDx')
        location = loc_date.find_element(By.CSS_SELECTOR, 'span[data-aut-id="item-location"]').text.strip().lower()
        date_text = loc_date.find_element(By.CSS_SELECTOR, 'span._2jcGx span').text.strip().lower()
    except:
        pass

    date = ''
    if date_text:
        today = datetime.now()
        if date_text == 'today':
            date = today.strftime('%b %d').lower()
        elif date_text == 'yesterday':
            date = (today - timedelta(days=1)).strftime('%b %d').lower()
        else:
            parts = date_text.split()
            try:
                days_ago = int(parts[0])
                date = (today - timedelta(days=days_ago)).strftime('%b %d').lower()
            except:
                date = date_text

    return {'title': title, 'price': price, 'location': location, 'date': date}

def load_all_items(driver):
    wait = WebDriverWait(driver, 10)
    while True:
        try:
            print("Loading more listings....")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, LOAD_MORE_SELECTOR)))
            load_btn = driver.find_element(By.CSS_SELECTOR, LOAD_MORE_SELECTOR)
            driver.execute_script("window.scrollBy(0, 300);")
            driver.execute_script("arguments[0].scrollIntoView(true);", load_btn)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", load_btn)
            time.sleep(0.5)
        except (TimeoutException, NoSuchElementException):
            break
        except ElementClickInterceptedException:
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(0.5)
            try:
                driver.execute_script("arguments[0].click();", load_btn)
                time.sleep(0.5)
            except:
                break

def scrape_to_csv(driver, url, output_file):
    driver.get(url)
    load_all_items(driver)

    items = driver.find_elements(By.CSS_SELECTOR, ITEM_SELECTOR)
    listings = [parse_listing(li) for li in items]

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'price', 'location', 'date'], quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(listings)

    print(f"saved {len(listings)} listings to {output_file}")

if __name__ == '__main__':

    from launch import Launch_Chrome
    Launch_Chrome()
    driver = init_driver(headless=False)
    try:
        scrape_to_csv(driver, SEARCH_URL, OUTPUT_FILE)
    finally:
        driver.quit()
