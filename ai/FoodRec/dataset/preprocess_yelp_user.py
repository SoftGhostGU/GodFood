# preprocess_yelp_user.py
import json
import argparse

def preprocess_user_data(input_file_path, output_file_path):
    """
    Reads user data from a JSON Lines file, removes the 'friends' field,
    and writes the modified data to a new JSON Lines file.

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
                user_data = json.loads(line)

                # Remove the 'friends' field if it exists
                if 'friends' in user_data:
                    del user_data['friends']
                
                # Write the modified JSON object to the output file
                outfile.write(json.dumps(user_data) + '\n')
                processed_count += 1

            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON on line {line_number}. Skipping.")
                error_count += 1
            except Exception as e:
                print(f"Warning: An unexpected error occurred on line {line_number}: {e}. Skipping.")
                error_count += 1
                
    print(f"\nPreprocessing complete.")
    print(f"Successfully processed {processed_count} user records.")
    if error_count > 0:
        print(f"Encountered errors on {error_count} lines (skipped).")
    print(f"Output saved to: {output_file_path}")

if __name__ == "__main__":
    # --- Create a dummy input file for testing ---
    dummy_input_filename = "dummy_yelp_user_data.json"
    sample_data = [
        {"user_id":"j14WgRoU_-2ZE1aw1dXrJg","name":"Daniel","review_count":4333,"yelping_since":"2009-01-25 04:35:42","useful":43091,"funny":13066,"cool":27281,"elite":"2009,2010","friends":"ueRPE0CX75ePGMqOFVj6IQ, 52oH4DrRvzzl8wh5UXyU0A","fans":3138,"average_stars":3.74,"compliment_hot":1145},
        {"user_id":"kGgAAR0m3G","name":"Jane","review_count":100,"yelping_since":"2010-02-10 10:10:10","useful":100,"funny":10,"cool":20,"elite":"","friends":"friend1, friend2, friend3","fans":50,"average_stars":4.0,"compliment_hot":10},
        {"user_id":"xyz123","name":"Alex","review_count":5,"yelping_since":"2020-01-01 00:00:00","useful":2,"funny":0,"cool":1,"elite":"","fans":1,"average_stars":3.2} # No friends field
    ]
    with open(dummy_input_filename, 'w', encoding='utf-8') as f:
        for record in sample_data:
            f.write(json.dumps(record) + '\n')
    # --- End of dummy file creation ---

    parser = argparse.ArgumentParser(description="Preprocess Yelp user data by removing the 'friends' field.")
    parser.add_argument(
        "--input", 
        type=str, 
        default=dummy_input_filename, # Default to the dummy file for easy testing
        help="Path to the input Yelp user JSON Lines file (e.g., yelp_academic_dataset_user.json)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="processed_yelp_user_data.json",
        help="Path to save the processed JSON Lines file"
    )
    
    args = parser.parse_args()

    print(f"Processing file: {args.input}")
    print(f"Output will be saved to: {args.output}")
    
    preprocess_user_data(args.input, args.output)

    # --- Verify the output (optional, for testing) ---
    print("\n--- Verifying a few lines from the output file ---")
    try:
        with open(args.output, 'r', encoding='utf-8') as f_out:
            for i in range(min(3, processed_count if 'processed_count' in locals() else 3)): # Print up to 3 lines
                line = f_out.readline().strip()
                if not line:
                    break
                print(line)
                data = json.loads(line)
                assert 'friends' not in data, "Verification failed: 'friends' field still present!"
        if 'processed_count' in locals() and processed_count > 0 :
             print("Output verification successful (for checked lines): 'friends' field removed.")
    except FileNotFoundError:
        print(f"Could not find output file {args.output} for verification.")
    except Exception as e:
        print(f"An error occurred during verification: {e}")