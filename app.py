import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

def scrape_gumroad_products(store_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(store_url, headers=headers)
    if response.status_code != 200:
        st.error("Failed to retrieve page")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find product links dynamically
    product_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "gumroad.com/l/" in href:  # Detect Gumroad product links
            if not href.startswith("http"):
                href = "https://gumroad.com" + href
            product_links.append(href)
    
    products = []
    for link in set(product_links):  # Remove duplicates
        product_response = requests.get(link, headers=headers)
        if product_response.status_code == 200:
            product_soup = BeautifulSoup(product_response.text, "html.parser")
            title = product_soup.find("title").text.strip() if product_soup.find("title") else "N/A"
            description = product_soup.find("meta", {"name": "description"})
            description = description["content"] if description else "N/A"
            image = product_soup.find("meta", {"property": "og:image"})
            image = image["content"] if image else "N/A"
            price = product_soup.find("span", class_="price")
            price = price.text.strip() if price else "Free"
            
            products.append({
                "id": title.replace(" ", "_").lower(),
                "title": title,
                "description": description,
                "link": link,
                "image_link": image,
                "price": price,
                "availability": "in stock",
                "product_type": "Digital Product",
                "brand": "PLRmix",
                "condition": "new"
            })
    
    return products

if st.button("Scrape Products"):
    data = scrape_gumroad_products(store_url)
    df = pd.DataFrame(data)
    
    if not df.empty:
        st.success("Scraping complete! Download your CSV below.")
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="gumroad_products.csv",
            mime="text/csv"
        )
    else:
        st.warning("No products found. Ensure your Gumroad store URL is correct and public.")
