from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
import subprocess
import os
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FastAPI + Scrapy + MongoDB",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  allow_headers=["*"],
)
# --------------------------
# MongoDB Connection
# --------------------------
client = MongoClient("mongodb+srv://sourabhs_db_user:JJuRo1D9A0PcXZkv@cluster0.dlwow6s.mongodb.net/")
db = client["books"]   


# --------------------------
# 1️⃣ Run Scrapy spider
# --------------------------

@app.post("/run-spider")
def run_spider():
    existing = db["status_update"].find_one({"status": "open"})

    if existing:
        return JSONResponse(
            {"message": "Spider is already running"}, 
            status_code=409
        )
    
    # Get absolute path of scraper directory
    scraper_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "books")


    # Run spider
    subprocess.Popen(
        ["scrapy", "crawl", "books"],
        cwd=scraper_path 
    )

    return JSONResponse({"message": "Spider started"})


# --------------------------
# 2️⃣ Serve MongoDB data grouped by collection
# --------------------------
@app.get("/all-data")
def get_all_data():

    output = {}

    collections = db.list_collection_names()

    for col in collections:
        data = list(db[col].find({}, {"_id": 0}))
        output[col] = data

    return JSONResponse(output)


# --------------------------
# Root Route
# --------------------------
@app.get("/")
def home():
    return {"message": "FastAPI + Scrapy + MongoDB is running!"}

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "books",
    "books.csv"
)

@app.delete("/delete-csv")
def delete_csv():
    if os.path.exists(CSV_PATH):
        os.remove(CSV_PATH)
        return JSONResponse({"message": "CSV deleted"})
    else:
        return JSONResponse({"message": "CSV not found"}, status_code=404)

@app.get("/download-csv")
def download_csv():
    if os.path.exists(CSV_PATH):
        return FileResponse(
            CSV_PATH,
            media_type="text/csv",
            filename="books.csv"
        )
    else:
        return JSONResponse({"message": "CSV not found"}, status_code=404)

