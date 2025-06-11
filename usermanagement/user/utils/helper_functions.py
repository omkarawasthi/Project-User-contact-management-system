from pymongo import MongoClient
from django.conf import settings
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

# --- function to calculate age ---
def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


