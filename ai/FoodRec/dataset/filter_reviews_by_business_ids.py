# filter_reviews_by_business_ids.py
import json
import argparse
import os

def load_business_ids_from_file(business_file_path):
    """
    Loads all 'business_id' (or 'restaurant_id') values from a JSON Lines business file.
    """
    business_ids = set()
    if not os.path.exists(business_file_path):
        print(f"Error: Business ID file not found at {business_file_path}")
        return business_ids

    with open(business_file_path, 'r', encoding='utf-8') as f:
        for line_number, line in enumerate(f, 1):
            try:
                data = json.loads(line)
                # Accommodate both 'business_id' and 'restaurant_id' as possible keys
                if 'business_id' in data:
                    business_ids.add(data['business_id'])
                elif 'restaurant_id' in data: # If it was renamed earlier
                    business_ids.add(data['restaurant_id'])
                # else:
                #     print(f"Warning: No 'business_id' or 'restaurant_id' found in line {line_number} of {business_file_path}")
            except json.JSONDecodeError:
                print(f"Warning: Skipping malformed JSON line {line_number} in {business_file_path}: {line.strip()}")
    print(f"Loaded {len(business_ids)} unique business/restaurant IDs from {os.path.basename(business_file_path)}.")
    return business_ids

def filter_reviews(review_file_path, business_ids_to_keep, output_review_file_path):
    """
    Filters reviews from review_file_path, keeping only those whose
    'business_id' (or 'restaurant_id') is in business_ids_to_keep.
    Writes the filtered reviews to output_review_file_path.
    """
    if not os.path.exists(review_file_path):
        print(f"Error: Review file not found at {review_file_path}")
        return

    kept_reviews_count = 0
    skipped_reviews_count = 0
    error_lines_count = 0

    with open(review_file_path, 'r', encoding='utf-8') as infile, \
         open(output_review_file_path, 'w', encoding='utf-8') as outfile:
        for line_number, line in enumerate(infile, 1):
            try:
                review_data = json.loads(line)
                review_business_id = None
                if 'business_id' in review_data:
                    review_business_id = review_data['business_id']
                elif 'restaurant_id' in review_data: # If it was renamed in your review_processed file
                    review_business_id = review_data['restaurant_id']
                
                if review_business_id and review_business_id in business_ids_to_keep:
                    outfile.write(line) # Write the original line
                    kept_reviews_count += 1
                elif review_business_id:
                    skipped_reviews_count +=1
                # else:
                #     print(f"Warning: No 'business_id' or 'restaurant_id' found in review line {line_number}. Skipping.")
                #     skipped_reviews_count +=1

            except json.JSONDecodeError:
                print(f"Warning: Could not decode JSON in review file on line {line_number}. Skipping.")
                error_lines_count += 1
            except Exception as e:
                print(f"Warning: An unexpected error occurred on review line {line_number}: {e}. Skipping.")
                error_lines_count += 1
    
    print(f"\nFiltering complete.")
    print(f"Kept {kept_reviews_count} reviews.")
    print(f"Skipped {skipped_reviews_count} reviews (business_id not in target list or missing).")
    if error_lines_count > 0:
        print(f"Encountered errors on {error_lines_count} lines in the review file.")
    print(f"Filtered reviews saved to: {output_review_file_path}")

if __name__ == "__main__":
    # --- Create dummy input files for testing ---
    dummy_reviews_file = "dummy_yelp_review_processed.json"
    dummy_businesses_file = "dummy_yelp_business_with_food_attrs_1.json" # Simulates one of your split business files
    dummy_output_reviews_file = "dummy_yelp_review_processed_1.json"

    # Sample business IDs to keep
    target_biz_ids = ["biz_A_keep", "biz_C_keep", "biz_E_keep"]
    
    sample_businesses = [
        {"business_id": "biz_A_keep", "name": "Restaurant A"},
        {"business_id": "biz_B_skip", "name": "Restaurant B"},
        {"business_id": "biz_C_keep", "name": "Cafe C"},
        {"business_id": "biz_D_skip", "name": "Bar D"},
        {"business_id": "biz_E_keep", "name": "Diner E"},
    ]
    with open(dummy_businesses_file, 'w', encoding='utf-8') as f:
        for record in sample_businesses:
            f.write(json.dumps(record) + '\n')

    sample_reviews = [
        {"review_id": "r1", "user_id": "u1", "business_id": "biz_A_keep", "stars": 5.0}, # Keep
        {"review_id": "r2", "user_id": "u2", "business_id": "biz_B_skip", "stars": 3.0}, # Skip
        {"review_id": "r3", "user_id": "u1", "business_id": "biz_C_keep", "stars": 4.0}, # Keep
        {"review_id": "r4", "user_id": "u3", "business_id": "biz_A_keep", "stars": 2.0}, # Keep
        {"review_id": "r5", "user_id": "u2", "business_id": "biz_D_skip", "stars": 1.0}, # Skip
        {"review_id": "r6", "user_id": "u4", "business_id": "biz_E_keep", "stars": 5.0}, # Keep
        {"review_id": "r7", "user_id": "u5", "restaurant_id": "biz_A_keep", "stars": 4.0}, # Keep (testing restaurant_id key)
        {"review_id": "r8", "user_id": "u6", "business_id": "biz_F_not_in_biz_file", "stars": 3.0}, # Skip
    ]
    with open(dummy_reviews_file, 'w', encoding='utf-8') as f:
        for record in sample_reviews:
            f.write(json.dumps(record) + '\n')
    # --- End of dummy file creation ---

    parser = argparse.ArgumentParser(
        description="Filter reviews based on business IDs from another file."
    )
    parser.add_argument(
        "--reviews_input", 
        type=str, 
        default=dummy_reviews_file, # For easy testing
        help="Path to the input review JSON Lines file (e.g., yelp_review_processed.json)"
    )
    parser.add_argument(
        "--businesses_input", 
        type=str, 
        default=dummy_businesses_file, # For easy testing
        help="Path to the business JSON Lines file containing the target business_ids (e.g., yelp_business_with_food_attrs_1.json)"
    )
    parser.add_argument(
        "--reviews_output", 
        type=str, 
        default=dummy_output_reviews_file, # For easy testing
        help="Path to save the filtered review JSON Lines file (e.g., yelp_review_processed_1.json)"
    )
    
    args = parser.parse_args()

    print(f"Filtering reviews from: {args.reviews_input}")
    print(f"Using business IDs from: {args.businesses_input}")
    print(f"Saving filtered reviews to: {args.reviews_output}")
    
    # 1. Load the set of business IDs to keep
    business_ids_to_filter_by = load_business_ids_from_file(args.businesses_input)
    
    if not business_ids_to_filter_by:
        print("No business IDs loaded from the businesses file. Cannot filter reviews. Exiting.")
    else:
        # 2. Filter the reviews and write to the output file
        filter_reviews(args.reviews_input, business_ids_to_filter_by, args.reviews_output)

        # --- Optional: Verify the output (for dummy data) ---
        if args.reviews_input == dummy_reviews_file:
            print("\n--- Verifying filtered dummy reviews output ---")
            output_biz_ids_found = set()
            kept_count_verify = 0
            if os.path.exists(args.reviews_output):
                with open(args.reviews_output, 'r', encoding='utf-8') as f_out:
                    for line in f_out:
                        try:
                            data = json.loads(line)
                            biz_id = data.get('business_id') or data.get('restaurant_id')
                            if biz_id:
                                output_biz_ids_found.add(biz_id)
                                kept_count_verify +=1
                        except json.JSONDecodeError:
                            pass # Already handled in main function
                
                print(f"Number of reviews in output file: {kept_count_verify}")
                print(f"Business IDs found in output: {output_biz_ids_found}")
                
                # For dummy data, we expect reviews for "biz_A_keep", "biz_C_keep", "biz_E_keep"
                expected_output_ids = {"biz_A_keep", "biz_C_keep", "biz_E_keep"}
                if output_biz_ids_found == expected_output_ids and kept_count_verify == 5 : # 5 reviews match in dummy data
                    print("Dummy data verification successful: Correct business IDs and count found in output.")
                else:
                    print(f"Dummy data verification Mismatch: Expected IDs {expected_output_ids} (5 reviews), Got IDs {output_biz_ids_found} ({kept_count_verify} reviews).")

            else:
                print(f"Output file {args.reviews_output} not found for verification.")