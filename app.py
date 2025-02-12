import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

def scrape_all_products(store_url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(store_url)
    time.sleep(3)
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    
    products = []
    product_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='/l/']")
    product_links = list(set([elem.get_attribute("href") for elem in product_elements]))
    driver.quit()
    
    for link in product_links:
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(link)
        time.sleep(2)
        
        try:
            title = driver.find_element(By.TAG_NAME, "title").text.strip()
        except:
            title = "N/A"
        
        try:
            description = driver.find_element(By.NAME, "description").get_attribute("content")
        except:
            description = "N/A"
        
        try:
            image = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")
        except:
            image = "N/A"
        
        try:
            price = driver.find_element(By.CLASS_NAME, "price").text.strip()
        except:
            price = "Free"
        
        driver.quit()
        
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
