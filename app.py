import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import time

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

def get_all_pages(store_url):
    """Retrieve all pagination links for the store."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    response = requests.get(store_url, headers=headers)
    if response.status_code != 200:
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    pages = [store_url]
    
    # Find pagination links (if any)
    pagination_links = soup.find_all("a", href=True)
    for link in pagination_links:
        href = link["href"]
        if "page=" in href and href not in pages:
            pages.append(href if href.startswith("http") else store_url + href)
    
    return pages

def scrape_gumroad_products(store_url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    all_pages = get_all_pages(store_url)
    
    product_links = set()
    for page in all_pages:
        response = requests.get(page, headers=headers)
        if response.status_code != 200:
            continue
        
        soup = BeautifulSoup(response.text, "html.parser")
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if "gumroad.com/l/" in href:
                product_links.add(href if href.startswith("http") else "https://gumroad.com" + href)
        time.sleep(1)  # Avoid overloading the server
    
    products = []
    for link in product_links:
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
