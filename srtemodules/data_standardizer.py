import pandas as pd
import re

def load_lecturer_database(file_path="Lecturer database.xlsx - Sheet1.csv"):
    """
    Loads the lecturer database from a CSV file and prepares lookup dictionaries.

    Args:
        file_path (str): The path to the lecturer database CSV file.

    Returns:
        tuple: A tuple containing:
            - dict: A dictionary mapping official lecturer names (lowercase) to their
                    department and school information.
            - dict: A dictionary mapping all aliases (including official names, lowercase)
                    to their official standardized name.
    """
    try:
        # Load the lecturer database directly from the provided CSV file
        lecturers_df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: Lecturer database file not found at {file_path}. Please ensure the file exists in the same directory as this script.")
        return {}, {} # Return empty dictionaries to prevent further errors
    except Exception as e:
        print(f"Error loading lecturer database: {e}")
        return {}, {}

    # Ensure 'Official Name', 'Department', 'School' columns exist
    required_cols = ['Official Name', 'Department', 'School']
    if not all(col in lecturers_df.columns for col in required_cols):
        print(f"Error: Lecturer database is missing one or more required columns: {required_cols}. Please check your CSV.")
        return {}, {}

    # Ensure 'Aliases' column exists, if not, add it for future use
    if 'Aliases' not in lecturers_df.columns:
        lecturers_df['Aliases'] = '' # Add an empty 'Aliases' column

    official_name_to_info = {}
    alias_to_official = {}

    for _, row in lecturers_df.iterrows():
        official_name = str(row['Official Name']).strip()
        department = str(row['Department']).strip()
        school = str(row['School']).strip()
        aliases_str = str(row['Aliases']).strip() if pd.notna(row['Aliases']) else ""

        # Store official info, using lowercase official name as key for lookup
        official_name_to_info[official_name.lower()] = {
            'Department': department,
            'School': school
        }

        # Add official name itself to aliases mapping (case-insensitive)
        alias_to_official[official_name.lower()] = official_name

        # Process aliases from the 'Aliases' column (comma-separated)
        if aliases_str:
            aliases = [a.strip() for a in aliases_str.split(',') if a.strip()]
            for alias in aliases:
                alias_to_official[alias.lower()] = official_name

    return official_name_to_info, alias_to_official

def standardize_lecturer_data(df):
    """
    Standardizes lecturer names, departments, and schools in a DataFrame
    based on a lecturer database. Flags lecturers not found in the database.

    Args:
        df (pd.DataFrame): The input DataFrame containing raw SRTE data,
                           expected to have a 'Lecturer Name' column.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: The DataFrame with standardized 'Lecturer Name',
                            'Department', and 'School' columns.
            - list: A list of raw lecturer names that were not found in the database.
    """
    # Load lecturer database mappings
    official_name_to_info, alias_to_official = load_lecturer_database()

    if not official_name_to_info or not alias_to_official:
        print("Standardization skipped due to missing or invalid lecturer database.")
        return df, []

    # Make a copy to avoid modifying the original DataFrame directly
    standardized_df = df.copy()
    unmatched_lecturers = []

    # Ensure 'Lecturer Name' column exists
    if 'Lecturer Name' not in standardized_df.columns:
        print("Warning: 'Lecturer Name' column not found in the input DataFrame. Skipping lecturer standardization.")
        return standardized_df, []

    # Iterate through each row to standardize lecturer name and populate department/school
    for index, row in standardized_df.iterrows():
        raw_name = str(row['Lecturer Name']).strip()
        lower_raw_name = raw_name.lower()
        
        standardized_name = alias_to_official.get(lower_raw_name)

        if standardized_name:
            # Found a match, update name and get official department/school
            standardized_df.at[index, 'Lecturer Name'] = standardized_name
            
            # Lookup department and school using the lowercase official name
            info = official_name_to_info.get(standardized_name.lower())
            if info:
                # Update 'Department' and 'School' columns based on the database
                standardized_df.at[index, 'Department'] = info.get('Department', '')
                standardized_df.at[index, 'School'] = info.get('School', '')
            else:
                # Fallback if somehow the standardized name isn't in info lookup (shouldn't happen with correct building)
                standardized_df.at[index, 'Department'] = ''
                standardized_df.at[index, 'School'] = ''
        else:
            # No match found, flag this lecturer
            unmatched_lecturers.append(raw_name)
            # You might want to decide what to do with the 'Lecturer Name' in this case:
            # - Keep the raw name (as it is currently done by default if not overwritten)
            # - Prepend a flag: standardized_df.at[index, 'Lecturer Name'] = "UNMATCHED: " + raw_name
            # - Set to a generic placeholder
            
            # For unmatched lecturers, set Department and School to empty strings
            standardized_df.at[index, 'Department'] = ''
            standardized_df.at[index, 'School'] = ''

    # Remove duplicates from the unmatched list
    unmatched_lecturers = list(set(unmatched_lecturers))

    return standardized_df, unmatched_lecturers

if __name__ == '__main__':
    # --- Example Usage (for testing data_standardizer.py directly) ---
    print("Running data_standardizer.py in standalone test mode...")

    # Define the path to your actual lecturer database CSV
    lecturer_db_file = "Lecturer database.xlsx - Sheet1.csv"

    # Create a dummy raw SRTE data DataFrame to simulate your input
    # In your main analyzer.py, this would be your actual loaded SRTE data
    dummy_srte_data = {
        'Course Title': ['CSC101', 'PHY201', 'CHM301', 'CSC101', 'MTH101', 'BIO200'],
        'Lecturer Name': ['john doe', 'Prof Jane Smith', 'Mr. Alex Brown', 'Dr. J Doe', 'Dr. Peter Jones', 'Dr. Anna Lee'],
        'Department': ['Comp Sci', 'Physics Dept', 'Chem Dept', 'Comp Sci', 'Math', 'Biology'], # This will be overwritten by standardization
        'School': ['Eng', 'Sci', 'Sci', 'Eng', 'Art', 'Sci'], # This will be overwritten by standardization
        'TM1': [4, 5, 3, 4, 2, 4],
        'TA8': [3, 4, 2, 3, 1, 3]
    }
    raw_srte_df = pd.DataFrame(dummy_srte_data)
    print("\nRaw SRTE Data (before standardization):")
    print(raw_srte_df)

    # Standardize the dummy SRTE data using your actual lecturer database
    print(f"\nAttempting to load lecturer database from: {lecturer_db_file}")
    standardized_srte_df, flagged_lecturers = standardize_lecturer_data(raw_srte_df)

    print("\nStandardized SRTE Data (after standardization):")
    print(standardized_srte_df)

    if flagged_lecturers:
        print("\nFlagged (Unmatched) Lecturers:")
        for lecturer in flagged_lecturers:
            print(f"- {lecturer}")
        print("\n^ These lecturers were not found in your lecturer database. Please add them or their aliases.")
    else:
        print("\nNo unmatched lecturers found.")