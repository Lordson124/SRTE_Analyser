import pandas as pd
from srtemodules.srte_report import get_report # Make sure this import is correct

def generate_lec_report(student_list, df, semester, year, lecturer_name=None, output_dir="."):
    """
    Generates SRTE reports for lecturers.
    If lecturer_name is provided, generates a report for that specific lecturer.
    Otherwise, generates reports for all lecturers in the student_list.

    Args:
        student_list (pd.DataFrame): DataFrame containing summary data for lecturers.
        df (pd.DataFrame): DataFrame containing comments data.
        semester (str): The semester for the report (e.g., "FIRST").
        year (str): The academic session year (e.g., "2023/2024").
        lecturer_name (str, optional): The name of a specific lecturer to report on.
                                       If None, reports for all lecturers are generated.
        output_dir (str, optional): Directory where the PDF reports should be saved.
                                    Defaults to current directory.
    """
    if lecturer_name:
        # Filter for the specific lecturer
        single_lecturer_df = student_list[student_list['Lecturer Name'] == lecturer_name]
        if not single_lecturer_df.empty:
            # Pass the filtered DataFrame and the output_dir
            get_report(single_lecturer_df, df, semester, year, output_dir)
            print(f"Report generated for {lecturer_name}")
        else:
            print(f"No data found for lecturer: {lecturer_name}")
    else:
        # Generate reports for all lecturers
        unique_lecturers = student_list['Lecturer Name'].unique()
        for lec_name in unique_lecturers:
            lec_df = student_list[student_list['Lecturer Name'] == lec_name]
            if not lec_df.empty:
                # Pass each lecturer's DataFrame and the output_dir
                get_report(lec_df, df, semester, year, output_dir)
                print(f"Report generated for {lec_name}")
            else:
                print(f"No data found for lecturer: {lec_name}")

