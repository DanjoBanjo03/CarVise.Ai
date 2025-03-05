from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random

def get_autotrader_urls_chrome():
    options = ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    
    try:
        print("🌐 Opening AutoTrader.ca...")
        driver.get("https://www.autotrader.ca/cars/?rcp=15&rcs=0&prx=100&loc=Toronto%20ON")
        
        # Accept cookies
        try:
            cookie_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Accept') or contains(., 'Agree')]")
            ))
            cookie_btn.click()
            print("✅ Cookies accepted")
        except:
            print("⚠️  No cookie popup found")

        # Scroll 3 times to load all listings
        print("🖱️  Scrolling page...")
        for i in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1.2, 2.3))
            print(f"↕️  Scroll {i+1}/3 complete")
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.inner-link")))  # Wait for listings

        # Extract URLs
        print("🔍 Finding listings...")
        soup = BeautifulSoup(driver.page_source, "html.parser")
        urls = []
        
        for link in soup.select("a.inner-link"):
            href = link.get("href")
            if href:
                if not href.startswith("http"):
                    href = f"https://www.autotrader.ca{href}"
                urls.append(href)
        
        print(f"✅ Found {len(urls)} listings")
        return urls

    except Exception as e:
        print(f"🚨 Error: {str(e)}")
        return []

    finally:
        print("🧹 Closing browser...")
        driver.quit()
        print("✅ Done!")

if __name__ == "__main__":
    urls = get_autotrader_urls_chrome()
    print("\nSample URLs:")
    for url in urls[:5]:
        print(f"👉 {url}")