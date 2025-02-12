import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

def scrape_all_products(store_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    product_links = []
    page = 1
    max_pages = 10  # Prevent infinite loop
    
    while page <= max_pages:
        response = requests.get(f"{store_url}?page={page}", headers=headers)
        if response.status_code != 200:
            break
        
        soup = BeautifulSoup(response.text, "html.parser")
        product_cards = soup.find_all("a", href=True)
        new_links = ["https://gumroad.com" + a["href"] if not a["href"].startswith("http") else a["href"] for a in product_cards if "gumroad.com/l/" in a["href"]]
        
        if not new_links:
            break
        
        product_links.extend(new_links)
        page += 1
        time.sleep(1)  # Avoid overloading the server
    
    product_links = list(dict.fromkeys(product_links))  # Remove duplicates
    products = []
    
    for link in reversed(product_links):  # Reverse list to get oldest first
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
                "item_group_id": "",
                "product_type": "Digital Product",
                "google_product_category": "",
                "additional_image_link": "",
                "sale_price": "",
                "average_review_rating": "",
                "number_of_ratings": "",
                "number_of_reviews": "",
                "description_html": "",
                "video_link": "",
                "brand": "PLRmix",
                "GTIN": "",
                "mpn": "",
                "color": "",
                "gender": "",
                "age_group": "",
                "material": "",
                "pattern": "",
                "size": "",
                "size_type": "",
                "size_system": "",
                "alt_text": "",
                "variant_names": "",
                "variant_values": "",
                "adult": "",
                "tax": "",
                "shipping": "",
                "shipping_weight": "",
                "shipping_width": "",
                "shipping_height": "",
                "free_shipping_label": "",
                "free_shipping_limit": "",
                "custom_label_0": "",
                "custom_label_1": "",
                "custom_label_2": "",
                "custom_label_3": "",
                "custom_label_4": "",
                "ad_link": "",
                "condition": "new"
            })
    
    return products

if st.button("Scrape Products"):
    data = scrape_all_products(store_url)
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
