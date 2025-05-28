# preprocess_yelp_review.py
import json
import argparse
import numpy as np

# Define GENDERS and ORIGINS, same as your federated_config or define here
GENDERS = ['Male', 'Female', 'Other', 'PreferNotToSay'] # Added 'PreferNotToSay' for more variety
ORIGINS = ['North', 'South', 'East', 'West', 'Central', 'International', 'Local'] # Added more for variety

def preprocess_review_data(input_file_path, output_file_path):
    """
    Reads review data from a JSON Lines file, removes the 'text' field,
    adds new synthetic user/environmental attributes, and writes the
    modified data to a new JSON Lines file.

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
                review_data = json.loads(line)

                # 1. Remove the 'text' field if it exists
                if 'text' in review_data:
                    del review_data['text']
                
                # 2. Add the new synthetic attributes
                review_data['gender'] = np.random.choice(GENDERS)
                review_data['origin'] = np.random.choice(ORIGINS)
                review_data['body_temperature'] = round(np.random.normal(37.0, 0.5), 2) # Rounded for realism
                review_data['last_night_sleep_duration'] = round(np.random.uniform(4, 10), 1) # Rounded
                review_data['heart_rate'] = int(np.random.normal(70, 10)) # Integer
                review_data['weather_temperature'] = round(np.random.uniform(-5, 35), 1) # Rounded
                review_data['weather_humidity'] = round(np.random.uniform(20, 90), 1) # Rounded
                
                # Write the modified JSON object to the output file
                outfile.write(json.dumps(review_data) + '\n')
                processed_count += 1

            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON on line {line_number}. Skipping.")
                error_count += 1
            except Exception as e:
                print(f"Warning: An unexpected error occurred on line {line_number}: {e}. Skipping.")
                error_count += 1
                
    print(f"\nPreprocessing complete.")
    print(f"Successfully processed {processed_count} review records.")
    if error_count > 0:
        print(f"Encountered errors on {error_count} lines (skipped).")
    print(f"Output saved to: {output_file_path}")

if __name__ == "__main__":
    # --- Create a dummy input file for testing ---
    dummy_input_filename = "dummy_yelp_review_data.json"
    sample_data = [
        {"review_id":"KU_O5udG6zPuf7AESCsWrw","user_id":"mh_-eMZ6K5RLWhZyISBhwA","business_id":"XQfwVwDr-v0ZS3_CbbE5Xw","stars":3.0,"useful":0,"funny":0,"cool":0,"text":"Clean & simple Mandarin fried rice.","date":"2018-07-07 22:09:11"},
        {"review_id":"review_2","user_id":"user_B","business_id":"biz_Y","stars":5.0,"useful":2,"funny":1,"cool":1,"text":"Amazing food and great service! Will come back.","date":"2019-01-15 12:30:00"},
        {"review_id":"review_3","user_id":"user_C","business_id":"biz_Z","stars":1.0,"useful":10,"funny":5,"cool":0,"text":"Terrible experience. Avoid.","date":"2020-05-20 18:45:00"}
    ]
    with open(dummy_input_filename, 'w', encoding='utf-8') as f:
        for record in sample_data:
            f.write(json.dumps(record) + '\n')
    # --- End of dummy file creation ---

    parser = argparse.ArgumentParser(
        description="Preprocess Yelp review data: remove 'text' and add synthetic attributes."
    )
    parser.add_argument(
        "--input", 
        type=str, 
        default=dummy_input_filename,
        help="Path to the input Yelp review JSON Lines file (e.g., yelp_academic_dataset_review.json)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="processed_yelp_review_data.json",
        help="Path to save the processed JSON Lines file"
    )
    
    args = parser.parse_args()

    print(f"Processing file: {args.input}")
    print(f"Output will be saved to: {args.output}")
    
    preprocess_review_data(args.input, args.output)

    # --- Verify the output (optional, for testing) ---
    print("\n--- Verifying a few lines from the output file ---")
    new_attributes_to_check = [
        'gender', 'origin', 'body_temperature', 'last_night_sleep_duration',
        'heart_rate', 'weather_temperature', 'weather_humidity'
    ]
    try:
        with open(args.output, 'r', encoding='utf-8') as f_out:
            for i in range(min(3, processed_count if 'processed_count' in locals() else 3)):
                line = f_out.readline().strip()
                if not line:
                    break
                print(line)
                data = json.loads(line)
                assert 'text' not in data, "Verification failed: 'text' field still present!"
                for attr in new_attributes_to_check:
                    assert attr in data, f"Verification failed: '{attr}' field missing!"
        if 'processed_count' in locals() and processed_count > 0 :
             print("Output verification successful (for checked lines): 'text' removed and new attributes added.")
    except FileNotFoundError:
        print(f"Could not find output file {args.output} for verification.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")