# split_json_lines.py
import json
import argparse
import os

def split_json_lines_file(input_file_path, output_dir, num_splits):
    """
    Splits a JSON Lines file into a specified number of smaller files.

    Args:
        input_file_path (str): Path to the input JSON Lines file.
        output_dir (str): Directory where the split files will be saved.
        num_splits (int): The number of smaller files to create.
    """
    if not os.path.exists(input_file_path):
        print(f"Error: Input file not found at {input_file_path}")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # First, count the total number of lines (records) in the input file
    total_lines = 0
    with open(input_file_path, 'r', encoding='utf-8') as infile:
        for _ in infile:
            total_lines += 1
    
    if total_lines == 0:
        print("Input file is empty. No splits created.")
        return

    lines_per_split = (total_lines + num_splits - 1) // num_splits  # Ceiling division

    print(f"Total lines in input file: {total_lines}")
    print(f"Targeting approximately {lines_per_split} lines per split file.")

    output_file_handles = []
    output_file_paths = []
    base_filename = os.path.splitext(os.path.basename(input_file_path))[0]

    try:
        # Open all output files
        for i in range(num_splits):
            output_filename = f"{base_filename}_{i+1}.json"
            output_filepath = os.path.join(output_dir, output_filename)
            output_file_paths.append(output_filepath)
            # Open in append mode initially, then truncate if they exist from a previous run
            # Or simply open in write mode, which overwrites. Let's use write mode for simplicity.
            output_file_handles.append(open(output_filepath, 'w', encoding='utf-8'))

        current_file_index = 0
        lines_in_current_file = 0
        processed_lines_total = 0

        with open(input_file_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                output_file_handles[current_file_index].write(line)
                lines_in_current_file += 1
                processed_lines_total +=1

                if lines_in_current_file >= lines_per_split and current_file_index < num_splits - 1:
                    # Move to the next output file, unless it's the last one
                    # (the last file might get fewer or more lines to accommodate the total)
                    current_file_index += 1
                    lines_in_current_file = 0
            
            print(f"\nFinished processing {processed_lines_total} lines.")

    except Exception as e:
        print(f"An error occurred during splitting: {e}")
    finally:
        # Close all output files
        for handle in output_file_handles:
            if handle and not handle.closed:
                handle.close()
    
    print(f"\nSplitting complete. {num_splits} files created in '{output_dir}':")
    for path in output_file_paths:
        if os.path.exists(path): # Check if file was actually created (might not if input was empty or very small)
             print(f" - {os.path.basename(path)}")


if __name__ == "__main__":
    # --- Create a dummy input file for testing ---
    dummy_input_filename = "dummy_large_reviews.json"
    num_dummy_records = 105  # Example: 105 records, split into 10 files -> ~11 per file
    
    with open(dummy_input_filename, 'w', encoding='utf-8') as f:
        for i in range(num_dummy_records):
            record = {
                "review_id": f"review_{i+1}",
                "user_id": f"user_{(i % 20) + 1}", # Some repeating users
                "data_field": f"Some data for record {i+1}"
            }
            f.write(json.dumps(record) + '\n')
    # --- End of dummy file creation ---

    parser = argparse.ArgumentParser(
        description="Split a JSON Lines file into multiple smaller files."
    )
    parser.add_argument(
        "--input", 
        type=str, 
        default=dummy_input_filename, # Default to dummy for easy testing
        help="Path to the input JSON Lines file (e.g., yelp_review_processed.json)"
    )
    parser.add_argument(
        "--output_dir", 
        type=str, 
        default="split_reviews",
        help="Directory to save the split output files"
    )
    parser.add_argument(
        "--splits", 
        type=int, 
        default=10,
        help="Number of smaller files to create"
    )
    
    args = parser.parse_args()

    if args.splits <= 0:
        print("Error: Number of splits must be a positive integer.")
    else:
        print(f"Splitting file: {args.input}")
        print(f"Number of splits: {args.splits}")
        print(f"Output directory: {args.output_dir}")
        
        split_json_lines_file(args.input, args.output_dir, args.splits)

        # --- Optional: Verify the number of lines in created files (for dummy data) ---
        if args.input == dummy_input_filename:
            print("\n--- Verifying split files (for dummy data) ---")
            total_lines_in_splits = 0
            for i in range(args.splits):
                split_filename = os.path.join(args.output_dir, f"{os.path.splitext(dummy_input_filename)[0]}_{i+1}.json")
                if os.path.exists(split_filename):
                    with open(split_filename, 'r', encoding='utf-8') as sf:
                        count = sum(1 for _ in sf)
                        print(f"File {os.path.basename(split_filename)} has {count} lines.")
                        total_lines_in_splits += count
                else:
                    # This might happen if num_splits > total_lines in original file
                    print(f"File {os.path.basename(split_filename)} was not created (likely no lines assigned).")
            
            if total_lines_in_splits == num_dummy_records:
                print(f"\nVerification successful: Total lines in split files ({total_lines_in_splits}) "
                      f"matches original dummy records ({num_dummy_records}).")
            elif total_lines_in_splits > 0 :
                print(f"\nVerification warning: Total lines in split files ({total_lines_in_splits}) "
                      f"does not exactly match original dummy records ({num_dummy_records}). This can happen with rounding.")
            else:
                print(f"\nVerification: No lines found in split files.")