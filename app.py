import time
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

# Streamlit UI
st.title("Gumroad Product Scraper")
st.write("Enter your Gumroad store link below to scrape product details.")

store_url = st.text_input("Gumroad Store URL", "https://plrmix.gumroad.com/")

def scrape_all_products(store_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(store_url)
        time.sleep(3)
        
        # Scroll to load all products
        last_height = 0
        while True:
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        product_links = []
        for element in page.query_selector_all("a[href*='/l/']"):
            href = element.get_attribute("href")
            if href and "gumroad.com/l/" in href:
                if not href.startswith("http"):
                    href = "https://gumroad.com" + href
                product_links.append(href)
        
        browser.close()
    
    products = []
    for link in product_links:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(link)
            time.sleep(2)
            
            title = page.title() if page.title() else "N/A"
            description = page.query_selector("meta[name='description']").get_attribute("content") if page.query_selector("meta[name='description']") else "N/A"
            image = page.query_selector("meta[property='og:image']").get_attribute("content") if page.query_selector("meta[property='og:image']") else "N/A"
            price = page.query_selector(".price").text_content().strip() if page.query_selector(".price") else "Free"
            
            browser.close()
            
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
