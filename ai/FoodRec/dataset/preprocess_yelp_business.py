# preprocess_yelp_business.py
import json
import argparse
import numpy as np

# Define the CUISINE_TYPES, same as your federated_config or define here
CUISINE_TYPES = ['Italian', 'Chinese', 'Mexican', 'Indian', 'FastFood', 
                 'Japanese', 'Thai', 'Mediterranean', 'French', 'American', 'Other'] # Added more for variety
FOOD_TEMPERATURE_TYPES = ['Hot', 'Cold', 'RoomTemp']

def add_food_attributes_to_business(input_file_path, output_file_path):
    """
    Reads business data from a JSON Lines file, adds new food-related attributes
    (cuisine_type, avg_sweetness, etc.), and writes the modified data to a
    new JSON Lines file.

    Args:
        input_file_path (str): Path to the input JSON Lines file.
        output_file_path (str): Path to the output JSON Lines file.
    """
    processed_count = 0
    error_count = 0

    with open(input_file_path, 'r', encoding='utf-8') as infile, \
         open(output_file_path, 'w', encoding='utf-8') as outfile:
        for line_number, line in enumerate(infile, 1):
            try:
                # Load the JSON object from the line
                business_data = json.loads(line)

                # Add the new food-related attributes
                business_data['cuisine_type'] = np.random.choice(CUISINE_TYPES)
                business_data['avg_sweetness'] = np.random.uniform(0, 5)
                business_data['avg_sourness'] = np.random.uniform(0, 5)
                business_data['avg_spiciness'] = np.random.uniform(0, 5)
                business_data['avg_saltiness'] = np.random.uniform(0, 5)
                business_data['food_temperature_type'] = np.random.choice(FOOD_TEMPERATURE_TYPES)
                
                # Write the modified JSON object to the output file
                outfile.write(json.dumps(business_data) + '\n')
                processed_count += 1

            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON on line {line_number}. Skipping.")
                error_count += 1
            except Exception as e:
                print(f"Warning: An unexpected error occurred on line {line_number}: {e}. Skipping.")
                error_count += 1
                
    print(f"\nPreprocessing complete.")
    print(f"Successfully processed and added attributes to {processed_count} business records.")
    if error_count > 0:
        print(f"Encountered errors on {error_count} lines (skipped).")
    print(f"Output saved to: {output_file_path}")

if __name__ == "__main__":
    # --- Create a dummy input file for testing ---
    dummy_input_filename = "dummy_yelp_business_data.json"
    sample_data = [
        {"business_id":"Pns2l4eNsfO8kk83dixA6A","name":"Abby Rappoport, LAC, CMQ","address":"1616 Chapala St, Ste 2","city":"Santa Barbara","state":"CA","postal_code":"93101","latitude":34.4266787,"longitude":-119.7111968,"stars":5.0,"review_count":7,"is_open":0,"attributes":{"ByAppointmentOnly":"True"},"categories":"Doctors, Traditional Chinese Medicine, Naturopathic\/Holistic, Acupuncture, Health & Medical, Nutritionists","hours":None},
        {"business_id":"ID_2","name":"Some Cafe","address":"123 Main St","city":"Anytown","state":"AN","postal_code":"12345","latitude":40.0,"longitude":-75.0,"stars":4.0,"review_count":100,"is_open":1,"attributes":None,"categories":"Cafe, Coffee & Tea, Restaurants","hours":{"Monday":"9:0-17:0"}},
        {"business_id":"ID_3","name":"Pizza Place","address":"456 Oak Ave","city":"Otherville","state":"OT","postal_code":"67890","latitude":39.0,"longitude":-74.0,"stars":3.5,"review_count":50,"is_open":1,"attributes":{"OutdoorSeating":"True"},"categories":"Pizza, Restaurants","hours":None}
    ]
    with open(dummy_input_filename, 'w', encoding='utf-8') as f:
        for record in sample_data:
            f.write(json.dumps(record) + '\n')
    # --- End of dummy file creation ---

    parser = argparse.ArgumentParser(
        description="Add food-related attributes to Yelp business data."
    )
    parser.add_argument(
        "--input", 
        type=str, 
        default=dummy_input_filename,
        help="Path to the input Yelp business JSON Lines file (e.g., yelp_academic_dataset_business.json)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="processed_yelp_business_data.json",
        help="Path to save the processed JSON Lines file with added attributes"
    )
    
    args = parser.parse_args()

    print(f"Processing file: {args.input}")
    print(f"Output will be saved to: {args.output}")
    
    add_food_attributes_to_business(args.input, args.output)

    # --- Verify the output (optional, for testing) ---
    print("\n--- Verifying a few lines from the output file ---")
    new_attributes_to_check = [
        'cuisine_type', 'avg_sweetness', 'avg_sourness', 
        'avg_spiciness', 'avg_saltiness', 'food_temperature_type'
    ]
    try:
        with open(args.output, 'r', encoding='utf-8') as f_out:
            for i in range(min(3, processed_count if 'processed_count' in locals() else 3)): # Print up to 3 lines
                line = f_out.readline().strip()
                if not line:
                    break
                print(line)
                data = json.loads(line)
                for attr in new_attributes_to_check:
                    assert attr in data, f"Verification failed: '{attr}' field missing!"
        if 'processed_count' in locals() and processed_count > 0:
             print("Output verification successful (for checked lines): New attributes are present.")
    except FileNotFoundError:
        print(f"Could not find output file {args.output} for verification.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")