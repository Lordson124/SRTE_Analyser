import base64
import glob
import os
import pathlib
from os.path import basename
from zipfile import ZipFile

import pandas as pd
import streamlit as sl
from fpdf import FPDF # This will now point to the older fpdf library
from PIL import Image

# --- CRITICAL PATH MODIFICATION FOR MODULE DISCOVERY ---
import sys
# Get the directory where srteapp.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))
# Get the parent directory of current_dir (which should be 'srte' folder)
# This assumes srtemodules is directly inside the 'srte' folder
project_root = os.path.join(current_dir)

# Add the project root to sys.path if it's not already there
# This ensures Python can find 'srtemodules'
if project_root not in sys.path:
    sys.path.insert(0, project_root) # Insert at the beginning for priority

print("--- sys.path after modification in srteapp.py ---")
print(sys.path)
print("-------------------------------------------------")
# -------------------------------------------------------

# Import the core analysis function (now includes lecturer standardization internally)
from srtemodules.analyzer import analyze
# Import the new data standardizer specifically for the "Generate Reports" path
from srtemodules.data_standardizer import standardize_lecturer_data
from srtemodules.coursecode import courses
from srtemodules.lecturers_reporter_ref import generate_lec_report

# Removed the import for download_font_if_not_exists as it's no longer in srte_report.py
# from srtemodules.srte_report import download_font_if_not_exists


sl.set_page_config(layout="wide")


# check for new course codes and extract them
def extract_new_codes(new):
    new["new"] = new["Course Title"].str.strip()
    new["new"] = new["new"].str.split(" ")
    new["new"] = new["new"].apply(lambda x: x[0])
    new["new"] = new["new"].str.split(r"\d")
    new["new"] = new["new"].apply(lambda x: x[0])
    new = new["new"].unique()

    new_codes = []

    for code in new:
        if code in courses:
            pass
        else:
            new_codes.append(code)

    return new_codes


# outputs analysis results for downloads
def reportdownload(pdf_b64, name):
    href = f'<a href="data:application/pdf;base64, {pdf_b64}" download="{name}.pdf">Click Here to Download SRTE report for {name}</a>'
    return href


# outputs analysis results for downloads
def zipsummaries(zip_b64, name):
    href = f'<a href="data:application/zip;base64, {zip_b64}" download="{name}">Click Here to Download SRTE summaries</a>'

    return href


# outputs analysis results for downloads
def zipdownload(zip_b64, name):
    href = f'<a href="data:application/zip;base64, {zip_b64}" download="{name}">Click Here to Download SRTE reports</a>'
    return href


@sl.cache_data
def readdata(datafile):
    """Reads the raw SRTE data Excel file."""
    df = pd.read_excel(datafile)
    # Assuming the last two columns are not part of the core data
    df = df[df.columns[0:-2]]
    return df

@sl.cache_data
def read_comment_data(datafile):
    """Reads the comments data Excel file."""
    df = pd.read_excel(datafile)
    # Assuming columns 2 to 25 are not comments
    df = df.drop(df.columns[2:25], axis=1)
    return df

@sl.cache_data
def read_summary_data(datafile):
    """Reads the summary data Excel file."""
    df = pd.read_excel(datafile)
    df = df.dropna(axis=0) # Drop rows with any NaN values
    return df

    
def main():
    # Removed the explicit call to download_font_if_not_exists() here,
    # as the function itself was removed from srte_report.py.
    # Font files (DejaVuSans.ttf and DejaVuSans.json) are now expected
    # to be manually placed in the srtemodules directory.
    # download_font_if_not_exists() 

    sl.title("OIE Analytics tool")

    nav_menu, content_canvas = sl.columns((1, 3))

    with nav_menu:
        sl.markdown("### Menu items")

        option = sl.selectbox(
            "Choose actions", ("Select action", "Upload Data", "Generate Reports")
        )

        if option == "Upload Data":
            file = nav_menu.file_uploader("Choose SRTE Raw Data file (Excel)...", type=["xlsx"], key="file")

            if file is not None:
                dataset = readdata(file)
                # Define expected headers for the raw data
                header = [
                    "Course Title", "Lecturer Name", "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7",
                    "TA8", "TA9", "TA10", "TA11", "TA12", "CM13", "CM14", "CM15", "CM16",
                    "IF17", "IF18", "IF19", "IF20", "IF21", "PTA22", "PTA23",
                ]
                
                # Check if the number of columns matches the header length before assigning
                if len(dataset.columns) == len(header):
                    dataset.columns = header
                else:
                    content_canvas.error(f"Error: The uploaded file has {len(dataset.columns)} columns, but {len(header)} columns were expected. Please check your raw data file format.")
                    sl.stop() # Stop execution if column mismatch

                sl.session_state["dataset"] = dataset

                content_canvas.subheader("View uploaded raw dataset")
                display = content_canvas.dataframe(dataset)
                btn = content_canvas.button("Analyze and Standardize Data")

                if btn:
                    # analyze responses
                    # The analyze function itself now handles lecturer standardization internally
                    # It will print warnings for unmatched lecturers to the console/Streamlit logs
                    results = analyze(dataset)
                    content_canvas.success("SRTE Analysis and Lecturer Standardization completed successfully!")

                    # Create a zip file for school-wise summaries
                    zippedObj = ZipFile("srte_summaries.zip", "w")

                    for school_name, school_df in results.items():
                        # Save each school's analyzed data to an Excel file
                        excel_filename = f"{school_name}.xlsx"
                        school_df.to_excel(excel_filename, index=True)
                        # Add the generated Excel file to the zip archive
                        zippedObj.write(excel_filename, basename(excel_filename))
                        # Clean up: remove the individual Excel file after adding to zip
                        pathlib.Path(excel_filename).unlink()

                    # Close zipfile object
                    zippedObj.close()

                    # Provide download link for the zipped summaries
                    with open("srte_summaries.zip", "rb") as fin:
                        zip_base64 = base64.b64encode(fin.read()).decode("utf-8")

                    content_canvas.markdown(
                        zipsummaries(zip_base64, "srte_summaries.zip"),
                        unsafe_allow_html=True,
                    )

                    # Clean up: remove the zip file itself
                    pathlib.Path("srte_summaries.zip").unlink()

            else:
                display = content_canvas.info("Upload the raw SRTE data file to continue...")

        elif option == "Generate Reports":
            # upload files
            summary_file = sl.file_uploader("Upload SRTE Summary file (Excel)...", type=["xlsx"], key="sum_file")
            comment_file = sl.file_uploader("Upload SRTE Comment file (Excel)...", type=["xlsx"], key="com_file")

            header_col = [
                    "Course Title",
                    "Lecturer Name",
                    "Course likes", # Assuming this is column 2 (index 2) for extract_likes
                    "Course dislikes" # Assuming this is column 3 (index 3) for extract_dislikes
                ]

            if summary_file is not None and comment_file is not None:
                # read files to dataframe
                sum_data = read_summary_data(summary_file)
                com_data = read_comment_data(comment_file)

                # Ensure comment data columns are correctly named for extractor
                if len(com_data.columns) == len(header_col):
                    com_data.columns = header_col
                else:
                    content_canvas.error(f"Error: Comment file has {len(com_data.columns)} columns, but {len(header_col)} columns were expected. Please check your comment file format.")
                    sl.stop() # Stop execution if column mismatch

                sl.session_state["dataset"] = sum_data # Storing summary data in session state

                with content_canvas:
                    sl.subheader("View uploaded dataset")

                    # --- IMPORTANT: Standardize sum_data here as well ---
                    sl.markdown("Standardizing lecturers in summary data...")
                    sum_data, unmatched_summary_lecturers = standardize_lecturer_data(sum_data)

                    if unmatched_summary_lecturers:
                        sl.warning("Warning: Some lecturers in the uploaded summary file were not found in the database:")
                        for name in sorted(unmatched_summary_lecturers):
                            sl.write(f"- {name}")
                        sl.markdown("Please update your lecturer database for full consistency.")
                    else:
                        sl.success("Lecturers in summary data standardized successfully or no new names found.")
                    # ----------------------------------------------------

                    # --- DEBUG: Print columns of sum_data after standardization ---
                    print("Columns of sum_data after standardization:", sum_data.columns.tolist())
                    # --------------------------------------------------------------

                    # create two columns for displaying dataframes
                    data_col1, data_col2 = sl.columns(2)
                    data_col1.markdown("##### View summary data")
                    display_data = data_col1.dataframe(sum_data) # Display standardized data
                    data_col2.markdown("##### View comments data")
                    display_comment = data_col2.dataframe(com_data)
                    
                    # create 3 columns for textbox inputs
                    col1, col2, col3 = sl.columns(3)

                    session = col1.text_input("Enter session", key="session_input")
                    semester = col2.text_input("Enter semester", key="semester_input")
                    
                    checked = sl.checkbox(
                        "Check this box to generate only one Lecturer's report", key="single_lecturer_checkbox"
                    )
                    
                    lecturer = None # Initialize lecturer variable
                    if checked:
                        lecturer = col3.text_input("Enter Lecturer name (Standardized name expected!)", key="lecturer_name_input")
                        if lecturer and lecturer.lower() not in [n.lower() for n in sum_data['Lecturer Name'].unique()]:
                            sl.warning("The entered lecturer name might not match any standardized name in the summary data. Please use a name from the standardized data above.")


                report_btn = content_canvas.button("Generate Report", key="generate_report_button")

                if report_btn:
                    if not session or not semester:
                        content_canvas.error("Please enter both session and semester to generate reports.")
                        sl.stop()

                    if checked and not lecturer:
                        content_canvas.error("Please enter the lecturer's name if you checked to generate a single report.")
                        sl.stop()
                    
                    # Generate reports
                    if checked:
                        # Generate report for a single lecturer
                        # generate_lec_report will receive the already standardized sum_data
                        generate_lec_report(
                            sum_data, com_data, semester, session, lecturer
                        )

                        # Get PDF files in current directory
                        pdf_file_path = glob.glob(os.path.join(os.getcwd(), "*.pdf"))

                        if not pdf_file_path:
                            content_canvas.warning("No PDF reports were generated. Check the lecturer name or data.")
                        else:
                            # Make files available for download and remove from current directory
                            for report_path in pdf_file_path:
                                # Extract the file name
                                report_name = pathlib.Path(report_path).stem # Gets name without extension
                                
                                # Read pdf file and convert to base64 string
                                with open(report_path, "rb") as pdf_file:
                                    pdf_base64 = base64.b64encode(pdf_file.read()).decode("utf-8")

                                content_canvas.markdown(
                                    reportdownload(pdf_base64, report_name),
                                    unsafe_allow_html=True,
                                )
                                content_canvas.success(f"Report for {report_name} generated!")

                                # Clean up: remove the individual PDF file
                                pathlib.Path(report_path).unlink()

                    else:
                        # Generate reports for all lecturers
                        # generate_lec_report will receive the already standardized sum_data
                        generate_lec_report(sum_data, com_data, semester, session)
                        content_canvas.success("All lecturer reports generated and bundled into a zip file!")

                        # Get PDF files in current directory
                        pdf_file_path = glob.glob(os.path.join(os.getcwd(), "*.pdf"))

                        if not pdf_file_path:
                            content_canvas.warning("No PDF reports were generated for all lecturers. Check your data.")
                        else:
                            # Create a zip file object
                            zippedObj = ZipFile("srte_reports.zip", "w")

                            # Add files to zip and remove from directory
                            for report_path in pdf_file_path:
                                zippedObj.write(report_path, basename(report_path)) # Add to zip
                                pathlib.Path(report_path).unlink() # Remove original PDF

                            # Close zipfile object
                            zippedObj.close()

                            # Provide download link for the zipped reports
                            with open("srte_reports.zip", "rb") as fin:
                                zip_base64 = base64.b64encode(fin.read()).decode("utf-8")

                            content_canvas.markdown(
                                zipdownload(zip_base64, "srte_reports.zip"),
                                unsafe_allow_html=True,
                            )

                            # Clean up: remove the zip file itself
                            pathlib.Path("srte_reports.zip").unlink()

            else:
                display = content_canvas.info(
                    "Upload the SRTE Summary and Comment files to continue..."
                )
        
        # This section is for checking new course codes, seems independent of the main analysis/report flow
        if option == "Upload Data" and sl.session_state.get("file") is not None:
            # This condition ensures the button only appears after a raw data file has been uploaded
            nav_menu.markdown("---") # Separator
            nav_menu.markdown("**Check for New Course Codes**")
            btn = nav_menu.button("Check New Course Codes")

            if btn:
                if "dataset" in sl.session_state:
                    df = sl.session_state.dataset
                    new_codes = extract_new_codes(df)
                    content_canvas.markdown("#### New Course Codes Found:")
                    if new_codes:
                        content_canvas.success(", ".join(new_codes))
                    else:
                        content_canvas.info("No new course codes found.")
                else:
                    content_canvas.warning("Please upload and analyze data first to check for new course codes.")


if __name__ == "__main__":
    main()
