Project: Books Scrapy Spider

Overview
- Scrapes book listings from selected categories on `books.toscrape.com`.
- Extracts `title`, `price`, `availability`, `rating`, `image_link`, and a `collection_name` per item.
- Follows pagination up to 5 pages per category to keep the crawl bounded.
- Stores items to a CSV (`books.csv`) and to MongoDB (collections named by category) via the pipeline.

Setup (Windows)
- Ensure Python 3.11 is installed.
- Create and activate a virtual environment:
  - `python -m venv venv`
  - `./venv/Scripts/Activate.ps1`
  Activate
  - `./venv/Scripts/activate`
- Install dependencies:
  - `cd .\books\`
  - `pip install -r requirements.txt`

Run
- From the `books` directory:
  - List spiders: `scrapy list`
  - Run the spider: `scrapy crawl books`
- Output
  - CSV: `books.csv` appended in the project root (managed by pipeline).
  - MongoDB: items inserted into database `books` with collections per category.

Approach
- Seeds category URLs in `start_requests` and passes `page_num` meta to control pagination.
- In `parse`, iterates product cards, extracts fields using CSS selectors, and yields `BooksItem` instances.
- Paginates manually using the URL pattern: starting from `.../index.html`, the next pages are `.../page-2.html`, `.../page-3.html`, etc. Generates these links and follows them via `response.follow` until `page_num` reaches 5.
- Pipeline writes items into CSV and MongoDB using `collection_name` to route data.


Scrapy Command
- `scrapy startproject books`
- `scrapy genspider books books.toscrape.com`
- `scrapy crawl books`