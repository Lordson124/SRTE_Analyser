import pandas as pd
import json
import os

def generate_lecturer_db_content(excel_file_path, sheet_name=0):
    """
    Reads an Excel file, extracts lecturer data, and formats it as a Python list of dictionaries.

    Args:
        excel_file_path (str): The full path to your Excel file (e.g., 'C:/path/to/Lecturer database.xlsx').
        sheet_name (int or str): The sheet name or index containing the lecturer data.
                                  Defaults to 0 (first sheet).

    Returns:
        str: A string containing the Python list of dictionaries, ready to be pasted.
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        print(f"Successfully loaded Excel file: {excel_file_path}")
        print(f"Columns found: {df.columns.tolist()}")

        # Define expected columns and their mappings
        # Adjust these column names if they are different in your actual Excel sheet
        official_name_col = 'Official Name'
        department_col = 'Department'
        school_col = 'School'
        aliases_col = 'Aliases' # This column is optional

        required_cols = [official_name_col, department_col, school_col]
        
        # Check if all required columns exist
        if not all(col in df.columns for col in required_cols):
            missing_cols = [col for col in required_cols if col not in df.columns]
            print(f"Error: Missing required columns in Excel sheet: {', '.join(missing_cols)}")
            print("Please ensure your Excel sheet has columns named 'Official Name', 'Department', and 'School'.")
            return None

        lecturer_data = []
        for index, row in df.iterrows():
            entry = {
                'Official Name': str(row[official_name_col]).strip() if pd.notna(row[official_name_col]) else '',
                'Department': str(row[department_col]).strip() if pd.notna(row[department_col]) else '',
                'School': str(row[school_col]).strip() if pd.notna(row[school_col]) else ''
            }
            # Add aliases only if the column exists and has a non-NaN value
            if aliases_col in df.columns and pd.notna(row[aliases_col]):
                entry['Aliases'] = str(row[aliases_col]).strip()
            else:
                entry['Aliases'] = '' # Ensure 'Aliases' key is always present, even if empty

            lecturer_data.append(entry)

        # Format the list of dictionaries as a Python string
        # Use json.dumps with indent for readability
        formatted_data = json.dumps(lecturer_data, indent=4, ensure_ascii=False)

        # Construct the final Python script content
        script_content = f"""# C:\\Users\\OIE 21\\srte\\srtemodules\\lecturer_db.py

# This list holds your lecturer data extracted from your Excel file.
# You can update this list directly as your lecturer data changes.

lecturer_data = {formatted_data}

# You can add more data structures here if needed.
"""
        return script_content

    except FileNotFoundError:
        print(f"Error: Excel file not found at '{excel_file_path}'. Please check the path.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    print("--- Lecturer Database Extractor ---")
    print("This script will help you convert your Excel lecturer database into a Python script.")
    print("Ensure your Excel file has columns like 'Official Name', 'Department', 'School', and optionally 'Aliases'.")

    # Prompt user for file path
    excel_path = input("\nEnter the FULL path to your Lecturer database Excel file (e.g., C:\\Users\\YourName\\Documents\\Lecturer database.xlsx): ")
    
    # Prompt user for sheet name/index
    sheet_input = input("Enter the sheet name or sheet number (0 for first sheet) where lecturer data is located (press Enter for default 0): ")
    try:
        sheet_name = int(sheet_input) if sheet_input.strip().isdigit() else sheet_input.strip() if sheet_input.strip() else 0
    except ValueError:
        print("Invalid sheet input. Using default sheet 0.")
        sheet_name = 0

    generated_script = generate_lecturer_db_content(excel_path, sheet_name)

    if generated_script:
        print("\n--- GENERATED LECTURER DATA FOR lecturer_db.py ---")
        print("Copy the content below and paste it into your 'C:\\Users\\OIE 21\\srte\\srtemodules\\lecturer_db.py' file.")
        print("---------------------------------------------------\n")
        print(generated_script)
        print("\n---------------------------------------------------")
        print("Done! Remember to save lecturer_db.py after pasting.")
    else:
        print("\nFailed to generate lecturer data. Please review errors above.")

