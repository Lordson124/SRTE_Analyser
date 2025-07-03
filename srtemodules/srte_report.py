import numpy as np
import pandas as pd
from fpdf import FPDF # <-- This line should be active, using the old fpdf library
# from fpdf2 import FPDF # <-- This line should be commented out

import os
# Removed requests import as automatic download is removed
from datetime import datetime
import re # Import regex module for sanitization

# Assuming comments_extractor is in the same srtemodules package
from srtemodules.comments_extractor import extract_dislikes, extract_likes

# --- Font Setup for Unicode Support ---
# Define paths for the font files within the srtemodules directory
FONT_DIR = os.path.dirname(os.path.abspath(__file__))
DEJAVU_TTF_PATH = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
DEJAVU_JSON_PATH = os.path.join(FONT_DIR, 'DejaVuSans.json')

# Removed the download_font_if_not_exists function entirely.
# Font files (DejaVuSans.ttf and DejaVuSans.json) are now expected to be
# manually placed in the srtemodules directory.

def get_report(student_list, df, semester, year):
    """
    Generates a PDF report for each student/lecturer entry in the student_list.
    Includes overall scores, percentages, and extracted comments.
    """
    # Ensure fonts are available before starting PDF generation
    # This check is now manual, as the download function is removed.
    if not os.path.exists(DEJAVU_TTF_PATH):
        raise FileNotFoundError(f"DejaVuSans.ttf not found at {DEJAVU_TTF_PATH}. Please manually place it in the srtemodules folder.")
    if not os.path.exists(DEJAVU_JSON_PATH):
        raise FileNotFoundError(f"DejaVuSans.json not found at {DEJAVU_JSON_PATH}. Please manually place it in the srtemodules folder.")


    pdf = FPDF("P", "mm", "A4")

    for _, row in student_list.iterrows():
        pdf.add_page()
        pdf.ln()

        # Add DejaVuSans font for Unicode support
        # uni=True is crucial for UTF-8 support
        pdf.add_font('DejaVuSans', '', DEJAVU_TTF_PATH, uni=True)
        pdf.add_font('DejaVuSans', 'B', DEJAVU_TTF_PATH, uni=True) # Add bold version too

        # Page header section - Use DejaVuSans for all text to be safe
        pdf.set_font("DejaVuSans", "B", 12)
        pdf.set_y(7)
        # Centering "BABCOCK UNIVERSITY" across the full page width (0)
        # Removed set_x here as 'C' alignment handles it.
        pdf.cell(0, 5, "BABCOCK UNIVERSITY", 0, 1, "C") 
        
        pdf.set_font("DejaVuSans", "B", 12) # Re-set font for next line
        pdf.set_y(12)
        pdf.set_x(57) # Keep this x for left alignment
        pdf.cell(0, 5, "OFFICE OF INSTITUTIONAL EFFECTIVENESS", 0, 1, "L")
        
        pdf.set_font("DejaVuSans", "B", 12) # Re-set font for next line
        pdf.set_y(17)
        pdf.set_x(45) # Keep this x for left alignment
        pdf.cell(0, 5, "STUDENT RATING OF TEACHING EFFECTIVENESS (SRTE)", 0, 1, "L")
        
        pdf.set_font("DejaVuSans", "B", 12) # Re-set font for next line
        pdf.set_y(22)
        pdf.set_x(49) # Keep this x for left alignment
        pdf.cell(0, 5, f"{semester} SEMESTER OF {year} ACADEMIC SESSION", 0, 1, "L")
        pdf.set_y(30)

        header_summary = ['SUMMARY OF SCORES:', 'OVERALL MEAN', 'OVERALL RATING']
        w = [75.0, 55.0, 55.0]
        height = 7
        
        pdf.set_x(15)
        pdf.set_font("DejaVuSans", "B", 12) # Ensure bold for these details
        pdf.cell(0, height, f'SCHOOL: {str(row["School"])}', 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, f'DEPARTMENT: {str(row["Dept"])}', 0, 1, "L") # Use 'Dept'
        pdf.set_x(15)
        pdf.cell(0, height, f'COURSE CODE/TITLE: {str(row["Course Title"])}', 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, f'NAME OF LECTURER: {str(row["Lecturer Name"])}', 0, 1, "L")
        pdf.set_x(15)
        pdf.ln(3)
        
        pdf.set_x(15)
        # Summary table headers - ensure bold
        pdf.set_font("DejaVuSans", "B", 12) # Ensure bold for summary headers
        for x in range(len(header_summary)):
            pdf.cell(w[x], height, header_summary[x], 0, 0, 'L')

        pdf.ln(6)
        pdf.set_x(18)
        pdf.set_font('DejaVuSans', '', 12) # Switch to regular DejaVuSans for scores
        # NaN Handling: Use pd.notna() to check for NaN and replace with empty string if true
        pdf.cell(72, height, '* \tTeaching Methodology', 0, 0, 'L')
        pdf.cell(35, height, str(row['TM Overall']) if pd.notna(row['TM Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['TM %']}%" if pd.notna(row['TM %']) else '', 0, 1, 'C')
        pdf.set_x(18)
        pdf.cell(72, height, '* \tTeacher\'s Assessment Procedure', 0, 0, 'L')
        pdf.cell(35, height, str(row['TA Overall']) if pd.notna(row['TA Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['TA %']}%" if pd.notna(row['TA %']) else '', 0, 1, 'C')
        pdf.set_x(18)
        pdf.cell(72, height, '* \tClassroom Management', 0, 0, 'L')
        pdf.cell(35, height, str(row['CM Overall']) if pd.notna(row['CM Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['CM %']}%" if pd.notna(row['CM %']) else '', 0, 1, 'C')
        pdf.set_x(18)
        pdf.cell(72, height, '* \tIntegration of Faith', 0, 0, 'L')
        pdf.cell(35, height, str(row['IF Overall']) if pd.notna(row['IF Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['IF %']}%" if pd.notna(row['IF %']) else '', 0, 1, 'C')
        pdf.set_x(18)
        pdf.cell(72, height, '* \tTeacher\'s Attendance & Punctuality', 0, 0, 'L')
        pdf.cell(35, height, str(row['PTA Overall']) if pd.notna(row['PTA Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['PTA %']}%" if pd.notna(row['PTA %']) else '', 0, 1, 'C')
        pdf.set_x(18)
        pdf.set_font('DejaVuSans', 'B', 12) # Back to bold for Evaluation Score
        pdf.cell(72, height, '* \tEvaluation Score', 0, 0, 'L')
        pdf.cell(35, height, str(row['ES Overall']) if pd.notna(row['ES Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['ES %']}%" if pd.notna(row['ES %']) else '', 0, 1, 'C')
        pdf.ln()

        # Filter comments for the current lecturer and course
        filter_lecturer = df[df['Lecturer Name'] == str(row['Lecturer Name'])]
        filter_course = filter_lecturer[filter_lecturer['Course Title'] == str(row['Course Title'])]
        
        # Print comments - Now displaying ALL aggregated comments
        pdf.set_font('DejaVuSans', 'B', 12) # Bold for comment headers
        pdf.set_x(15)
        pdf.cell(0, height, 'OPEN ENDED ASSESSMENT', 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, '1. Indicate three things you experienced in this course that you liked', 0, 1, "L")
        
        likes = extract_likes(df, filter_course) # This now returns aggregated comments
        
        pdf.set_font('DejaVuSans', '', 12) # Regular font for comments content
        
        w_comment = 170 # Width for multi_cell
        
        # Iterate through ALL aggregated comments (no more top 3 limit)
        if likes: # Only print if there are comments
            for item in likes:
                pdf.set_x(18)
                # Ensure the item is a string and strip whitespace
                pdf.multi_cell(w_comment, height, f'* \t{str(item).strip()}', 0, 'L')
                pdf.ln(2) # Add a small line break after each comment for better readability
        else:
            pdf.set_x(18)
            pdf.multi_cell(w_comment, height, '* No specific likes mentioned.', 0, 'L')
            pdf.ln(2)
        
        pdf.ln()

        pdf.set_font('DejaVuSans', 'B', 12) # Bold for comment headers
        pdf.set_x(15)
        pdf.cell(0, height, '2. List three things you experienced that you did not like', 0, 1, "L")
        
        dislikes = extract_dislikes(df, filter_course) # This now returns aggregated comments
        
        pdf.set_font('DejaVuSans', '', 12) # Regular font for comments content
        
        # Iterate through ALL aggregated comments (no more top 3 limit)
        if dislikes: # Only print if there are comments
            for item in dislikes:
                pdf.set_x(18)
                # Ensure the item is a string and strip whitespace
                pdf.multi_cell(w_comment, height, f'* \t{str(item).strip()}', 0, 'L')
                pdf.ln(2) # Add a small line break after each comment for better readability
        else:
            pdf.set_x(18)
            pdf.multi_cell(w_comment, height, '* No specific dislikes mentioned.', 0, 'L')
            pdf.ln(2)
        
        pdf.ln()

        # Official Use and Footnote sections - Use DejaVuSans
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(15)
        pdf.cell(200, height, 'Footnote:', 0, 1, 'L')
        pdf.set_font('DejaVuSans', '', 12)
        pdf.set_x(15)
        pdf.multi_cell(200, height, '1.00 - 1.99=Poor, 2.00 - 2.49=Fair, 2.50 - 3.49=Good, 3.50 - 4.49=Very Good, 4.50 - 5.00=Excellent', 0, 'L')
        
        pdf.ln()
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(80)
        pdf.cell(200, height, 'FOR OFFICIAL USE ONLY:', 0, 1, 'L')
        pdf.set_font('DejaVuSans', 'B', 12)
        # NaN Handling for 'Class Pop', 'No', 'Resp Rate'
        pdf.set_x(15)
        pdf.cell(200, height, f'No. of students who took this course: {str(row["Class Pop"]) if pd.notna(row["Class Pop"]) else ""}', 0, 1, 'L')
        
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(15)
        pdf.cell(200, height, f'No. of students who evaluated this course: {str(row["No"]) if pd.notna(row["No"]) else ""}', 0, 1, 'L')
                
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(15)
        pdf.cell(200, height, f'Percent of students who evaluated this course: {str(np.round(row["Resp Rate"],1)) if pd.notna(row["Resp Rate"]) else ""}%', 0, 1, 'L')
        
        pdf.ln()

        # Invalid evaluation note
        if pd.notna(row['No']) and pd.notna(row['Class Pop']) and row['No'] > row['Class Pop']:
            pdf.set_font('DejaVuSans', 'B', 12)
            pdf.set_x(10)
            pdf.ln()
            pdf.multi_cell(200, height, 'Note: This evaluation is invalid, as the number of students that rated this course is more than the number of registered students for this course.', 0, 'L')

        pdf.set_y(-25)
        pdf.set_font('DejaVuSans', '', 10) # Smaller font for page number
        pdf.cell(0, 2, f'Page {pdf.page_no()}', 0, 0, 'C')
    
    # Sanitize the filename for invalid characters (like / \ : * ? " < > |)
    # Replace invalid characters with an underscore
    sanitized_lecturer_name = re.sub(r'[\\/:*?"<>|]', '_', str(row['Lecturer Name']).replace(',', '').replace('.', '').strip())
    sanitized_course_title = re.sub(r'[\\/:*?"<>|]', '_', str(row['Course Title']).strip())

    output_filename = f"{sanitized_lecturer_name}_{sanitized_course_title}.pdf"
    pdf.output(output_filename, "F")
