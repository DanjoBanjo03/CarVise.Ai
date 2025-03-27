from selenium.webdriver import Safari
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import random
import csv
import os

def get_autotrader_urls_safari():
    """Collect listing URLs from AutoTrader.ca using Safari"""
    driver = Safari()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    time.sleep(1)
    
    try:
        print("🌐 Opening AutoTrader.ca...")
        driver.get("https://www.autotrader.ca/cars/?rcp=100&rcs=0&prx=100&loc=Toronto%20ON")
        
        # Cookie handling
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Accept') or contains(., 'Agree')]")
            ))
            cookie_btn.click()
            print("✅ Cookies accepted")
        except TimeoutException:
            print("⚠️  No cookie popup found")

        # Scroll to load listings
        print("🖱️  Scrolling page...")
        # for i in range(3):
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     time.sleep(random.uniform(2, 3))  # Longer delays for Safari
        #     print(f"↕️  Scroll {i+1}/3 complete")
        #     wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.inner-link")))

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 3))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.inner-link")))

        # Extract URLs
        print("🔍 Finding listings...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        unique_urls = set()
        for link in soup.select("a.inner-link"):
            href = link.get("href")
            if href and "/a/" in href:  # Filter only listing links
                full_url = f"https://www.autotrader.ca{href}"
                unique_urls.add(full_url.split("?")[0])  # Remove URL parameters
        
        return list(unique_urls)

    finally:
        print("🧹 Closing URL collector browser...")
        driver.quit()

def scrape_car_details(driver, url):
    """Scrape individual car listing details"""
    try:
        time.sleep(2)
        print(f"🚗 Navigating to: {url}")
        driver.get(url)
        
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "p.hero-price"))
            )
        except TimeoutException:
            print(f"⏰ Timeout waiting for price on {url}")
            return None
            
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        price_element = soup.find("p", class_="hero-price")
        title_element = soup.find("h1", class_='hero-title')

        specs = {}
        spec_elements = soup.select('span[id^="spec-key-"]')

        for spec in spec_elements:
            try:
                key = spec.text.strip().lower().replace(" ", "_").replace("'", "").replace("-", "")
                value_id = spec['id'].replace("key", "value")
                value_element = spec.find_next('span', id=value_id)
                
                # Clean kilometer values
                raw_value = value_element.find('strong').text.strip()
                
                # Handle all kilometer variations
                if key in ['kilometres', 'km', 'mileage']:
                    # Remove ALL non-numeric characters using regex
                    cleaned_value = ''.join(filter(str.isdigit, raw_value))
                    if cleaned_value:  # Only convert if we got digits
                        specs[key] = int(cleaned_value)
                    else:
                        specs[key] = 0
                        print(f"⚠️  Invalid kilometer value: {raw_value}")
                else:
                    specs[key] = raw_value  # Keep other values as-is
                    
            except Exception as e:
                print(f"⚠️  Error parsing spec: {str(e)}")

        
        return {
            "url": url,
            "price": int(price_element.text.strip().replace(",", "")) if price_element else 0,
            "title": title_element.text.strip() if title_element else "Title N/A",
            **specs
        }

    except Exception as e:
        print(f"🚨 Failed to scrape {url}: {str(e)}")
        return None

def get_autotrader_data():
    """Main scraping workflow"""
    try:
        listing_urls = get_autotrader_urls_safari()
        print(f"🎉 Found {len(listing_urls)} listings to scrape")
        
        car_data = []
        for idx, url in enumerate(listing_urls[:100]):  # Test with 5 first
            print(f"\n📋 Processing {idx+1}/{len(listing_urls)}")
            
            driver = Safari()
            driver.maximize_window()
            
            try:
                data = scrape_car_details(driver, url)
                if data:
                    car_data.append(data)
                time.sleep(random.uniform(3, 5))  # Longer delays for Safari
            finally:
                driver.quit()
        
        return car_data

    except Exception as e:
        print(f"🚨 Main error: {str(e)}")
        return []

def save_to_csv(data):
    """Save results to CSV in scraping/data directory"""
    valid_data = [item for item in data if item is not None]
    
    # Create directory if it doesn't exist
    os.makedirs('data', exist_ok=True)

    fieldnames = set()
    for item in valid_data:
        fieldnames.update(item.keys())
    
    csv_path = os.path.join('data', 'car_prices.csv')

    base_fields = ["url", "title", "price"]
    ordered_fields = base_fields + [f for f in sorted(fieldnames) if f not in base_fields]
    
    with open(csv_path, "w", newline="") as f:
        # writer = csv.DictWriter(f, fieldnames=["url", "title", "price"], 
        #                         quoting=csv.QUOTE_MINIMAL)
        writer = csv.DictWriter(f, fieldnames=ordered_fields, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        writer.writerows(valid_data)
    print(f"💾 Data saved to {csv_path}")

if __name__ == "__main__":    
    car_data = get_autotrader_data()
    save_to_csv(car_data)
    
    if car_data:
        print("\nSample Data:")
        for item in car_data[:3]:
            print(f"• {item['title']} - {item['price']}")