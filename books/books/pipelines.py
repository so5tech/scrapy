# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
import logging
import os
import csv


class BooksPipeline:
    def open_spider(self, spider):
        # Create MongoDB connection when spider starts
        logging.getLogger("pymongo").setLevel(logging.WARNING)
        self.client = MongoClient('mongodb+srv://sourabhs_db_user:JJuRo1D9A0PcXZkv@cluster0.dlwow6s.mongodb.net/')
        self.db = self.client["books"]
        # self.collection = self.db["books"]

        # CSV setup
        self.csv_file_path = "books.csv"
        # Check if file exists
        file_exists = os.path.isfile(self.csv_file_path)
        self.csv_file = open(self.csv_file_path, "a", newline="", encoding="utf-8")
        self.csv_writer = None
        if not file_exists:
            self.headers_written = False
        else:
            self.headers_written = True

    def close_spider(self, spider):
        # Close connection when spider finishes
        self.client.close()

        self.csv_file.close()

    def process_item(self, item, spider):
        # Insert each item one by one
        collection_name = item['collection_name']  
        item_copy = dict(item)          
        item_copy.pop('collection_name', None)  
        self.db[collection_name].insert_one(dict(item))

        # --- CSV insertion ---
        if not self.headers_written:
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=item_copy.keys())
            self.csv_writer.writeheader()
            self.headers_written = True
        elif self.csv_writer is None:
            self.csv_writer = csv.DictWriter(self.csv_file, fieldnames=item_copy.keys())

        self.csv_writer.writerow(item_copy)

        return item

