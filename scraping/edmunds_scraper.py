import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "https://www.edmunds.com/cars-for-sale/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

cars = []
for listing in soup.find_all('div', class_='listing-item'):
    name = listing.find('h2', class_='title').text.strip()
    price = listing.find('span', class_='price').text.strip().replace('$', '').replace(',', '')
    details = listing.find('div', class_='details').text.strip().split(',')
    year = int(details[0])
    miles = details[1].strip()
    
    cars.append({
        'name': name,
        'price': float(price),
        'year': year,
        'miles': miles
    })

df = pd.DataFrame(cars)
df.to_csv('data/edmunds_listings.csv', index=False)
print(f"Scraped {len(cars)} cars and saved to CSV.")