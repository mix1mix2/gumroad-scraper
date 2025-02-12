import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

if st.button("Scrape Products"):
    def scrape_gumroad_products(store_url):
        response = requests.get(store_url)
        if response.status_code != 200:
            st.error("Failed to retrieve page")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Find product listings
        products = []
        for product in soup.find_all("div", class_="product-card"):  # Adjust class name if needed
            title = product.find("h2").text.strip() if product.find("h2") else "N/A"
            link = product.find("a")["href"] if product.find("a") else "N/A"
            image = product.find("img")["src"] if product.find("img") else "N/A"
            
            # Get product details from individual page
            product_response = requests.get(link)
            if product_response.status_code == 200:
                product_soup = BeautifulSoup(product_response.text, "html.parser")
                description = product_soup.find("meta", {"name": "description"})
                description = description["content"] if description else "N/A"
                
                price = product_soup.find("span", class_="price")
                price = price.text.strip() if price else "Free"
            else:
                description, price = "N/A", "N/A"
            
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
        st.warning("No products found or an error occurred.")
