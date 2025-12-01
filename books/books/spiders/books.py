import scrapy
from pathlib import Path 
import datetime

import logging
logging.basicConfig(level=logging.WARNING)

from books.items import BooksItem

# Spider extracts book cards from selected categories on books.toscrape.com.
# It follows pagination links and limits crawling to the first 5 pages
# per category to keep the crawl bounded.




class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]

    def start_requests(self):
        # Seed category pages
        urls = [
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html",
            "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html",
            "https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html",
            "https://books.toscrape.com/catalogue/category/books/sequential-art_5/index.html",
            "https://books.toscrape.com/catalogue/category/books/classics_6/index.html",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={"page_num": 1})
    
    def parse(self, response):
        page = response.url.split("/")[-2]

        # #saving the content as files
        # filename = f"books-{page}.html"
        # Path(filename).write_bytes(response.body)
        # self.log(f"Saved file {filename}")

        cards = response.css(".product_pod")
        for card in cards:
            data = BooksItem()
            
            # Extracting Title
            #take a inside of h3
            title = card.css("h3 > a::text").get(default="N/A")
            data['title'] = title
            
            #Extracting price
            price = card.css(".price_color::text").get(default="N/A")
            data['price'] = price

            #Extracting Availability
            availability = card.css(".avilability")
            if len(availability.css(".icon-ok")) > 0:
                availability_text = "In Stock"
            else:
                availability_text = "Out of Stock"
            data['availability'] = availability_text

            # Extract rating            
            try:
                rating_class = card.css(".star-rating").attrib["class"]
                rating = rating_class.split(" ")[1]
            except Exception:
                print(f"Unexpected rating class format: '{rating_class}'")
                rating = "N/A"
            data['rating'] = rating

            # Extract image link
            try:
                image = card.css(".image_container img")
                image_link = image.attrib["src"].replace("../../../../media", "https://books.toscrape.com/media")
            except Exception:
                print(f"Unexpected image format: '{image}'")
                image_link = "N/A"
            data['image_link'] = image_link
            
            data['collection_name'] = page

            yield data

        # Follow pagination up to 5 pages per category using URL pattern
        page_num = response.meta.get("page_num", 1)
        if page_num < 5:
            base_dir = response.url.rsplit("/", 1)[0]
            next_url = (
                response.url.replace("index.html", f"page-{page_num + 1}.html")
                if response.url.endswith("index.html")
                else f"{base_dir}/page-{page_num + 1}.html"
            )
            yield response.follow(next_url, callback=self.parse, meta={"page_num": page_num + 1})
        



   
