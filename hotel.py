import requests
import csv
import json
from datetime import datetime, timedelta
import time

# This function tries to get data from the website, and it will try multiple times if it fails
def get_hotel_data(url, attempts=5):
    try_count = 0
    wait_time = 5  # Start by waiting 5 seconds before trying again
    while try_count < attempts:
        try:
            # Using a browser-like header to make the request look more real
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.text
                hotel_data = json.loads(data)
                # Replace 'target_rates_field' with the correct path to the data you need
                return hotel_data['target_rates_field']  # Adjust based on what you find
            else:
                print(f"Failed to get data, status code: {response.status_code}")
                return []
        except Exception as error:
            print(f"Try {try_count + 1} failed: {error}")
            try_count += 1
            print(f"Waiting {wait_time} seconds before trying again...")
            time.sleep(wait_time)
            wait_time *= 2  # Wait longer each time it fails
    print("Gave up after too many tries, moving on to the next one.")
    return []

# This function processes the data and adds check-in/check-out info
def handle_rates(hotel_rates, check_in_date, check_out_date):
    processed_list = []
    for rate in hotel_rates:
        room_name = rate.get('room_name', 'Unknown Room')
        rate_name = rate.get('rate_name', 'Standard Rate')
        guest_count = rate.get('number_of_guests', 'Unknown Guests')
        cancel_rules = rate.get('cancellation_policy', 'Check Terms')
        price = rate.get('price', 'Not Available')
        top_deal = rate.get('top_deal', False)
        currency = rate.get('currency', 'USD')

        processed_list.append({
            "Hotel_ID": "18482",  # You can update this if needed
            "Check_In": check_in_date,
            "Check_Out": check_out_date,
            "Room": room_name,
            "Rate_Plan": rate_name,
            "Guests": guest_count,
            "Cancellation_Policy": cancel_rules,
            "Price": price,
            "Is_Top_Deal": top_deal,
            "Currency": currency
        })

    return processed_list

# This function saves all the collected data into one CSV file
def save_to_csv(all_data, filename='rates_output.csv'):
    try:
        with open(filename, 'w', newline='') as file:
            columns = ['Hotel_ID', 'Check_In', 'Check_Out', 'Room', 'Rate_Plan', 'Guests', 'Cancellation_Policy', 'Price', 'Is_Top_Deal', 'Currency']
            writer = csv.DictWriter(file, fieldnames=columns)
            writer.writeheader()
            for data_chunk in all_data:
                for item in data_chunk:
                    writer.writerow(item)
        print(f"Saved everything to {filename}")
    except IOError:
        print("Couldn't save the file, something went wrong.")

# This function creates a list of date combinations for check-in and check-out
def make_date_pairs(start_date, days_count):
    date_list = []
    for i in range(days_count):
        check_in = start_date + timedelta(days=i)
        check_out = check_in + timedelta(days=1)
        date_list.append((check_in.strftime('%Y-%m-%d'), check_out.strftime('%Y-%m-%d')))
    return date_list

# Main script starts here
hotel_id = '18482'
base_url = f'https://www.qantas.com/hotels/properties/{hotel_id}'
start_date = datetime.strptime('2024-09-01', '%Y-%m-%d')
date_pairs = make_date_pairs(start_date, 25)

all_data_collected = []  # This list will hold all the rate details we get

for check_in, check_out in date_pairs:
    # Make the URL for each check-in/check-out date
    url = (
        f"{base_url}?adults=2&checkIn={check_in}&checkOut={check_out}&children=0&infants=0&"
        "location=London%2C%20England%2C%20United%20Kingdom&page=1&payWith=cash&searchType=list&sortBy=popularity"
    )
    print(f"Working on URL: {url}")
    
    # Try to get and process the data
    rates = get_hotel_data(url)
    if rates:  # Only process if we got data back
        processed_rates = handle_rates(rates, check_in, check_out)
        all_data_collected.append(processed_rates)
    
    # Wait before making the next request so we don't hit the server too hard
    time.sleep(10)  # Waiting 10 seconds between requests

# After getting all the data, save it into a CSV file
save_to_csv(all_data_collected, filename='rates_output.csv')
