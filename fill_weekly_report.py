
import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import load_workbook #imports python library for reading and writting excel files
from openpyxl.drawing.image import Image

# Extract info from weekly_data.json; Needs folder path provided by reate_weekly_report_folder function
def extract_weekly_data(week_folder_path):
    weekly_data_json = "weekly_data.json"
    weekly_data_json_path =Path(week_folder_path / weekly_data_json)

    with open(weekly_data_json_path, 'r') as file:
        #data is a list of dict
        data = json.load(file)

    weekly_data = data["weekly_data"]

    event_date= weekly_data["event_date"]
    event_name= weekly_data["event_name"]
    event_type= weekly_data["event_type"]
    guest_count= weekly_data["guest_count"]

    space_fee= weekly_data["space_fee"]
    food_revenue= weekly_data["food_revenue"]
    beverage_revenue= weekly_data["beverage_revenue"]
    admin_fee= weekly_data["admin_fee"]
    sales_tax= weekly_data["sales_tax"]

    approx_food_cost= weekly_data["approx_food_cost"]
    in_house_labor= weekly_data["in_house_labor"]
    additional_labor = weekly_data["additional_labor"]
    outsourced_labor= weekly_data["outsourced_labor"]
    rentals= weekly_data["rentals"]
