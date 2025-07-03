import numpy as np
import pandas as pd
from fpdf import FPDF
import os
# Removed requests import as automatic download is removed
from datetime import datetime
import re

from srtemodules.comments_extractor import extract_dislikes, extract_likes, analyze_sentiment

# --- Font Setup for Unicode Support ---
FONT_DIR = os.path.dirname(os.path.abspath(__file__))
DEJAVU_TTF_PATH = os.path.join(FONT_DIR, 'DejaVuSans.ttf')
DEJAVU_JSON_PATH = os.path.join(FONT_DIR, 'DejaVuSans.json')

# Removed the download_font_if_not_exists function entirely.
# Font files (DejaVuSans.ttf and DejaVuSans.json) are now expected to be
# manually placed in the srtemodules directory.

def get_report(student_list, df, semester, year, output_dir="."): # Added output_dir parameter
    """
    Generates a PDF report for each student/lecturer entry in the student_list.
    Includes overall scores, percentages, and extracted comments with sentiment.

    Args:
        student_list (pd.DataFrame): DataFrame containing summary data for lecturers.
        df (pd.DataFrame): DataFrame containing comments data.
        semester (str): The semester for the report (e.g., "FIRST").
        year (str): The academic session year (e.g., "2023/2024").
        output_dir (str, optional): Directory where the PDF reports should be saved.
                                    Defaults to current directory.
    """
    # Ensure fonts are available before starting PDF generation
    if not os.path.exists(DEJAVU_TTF_PATH):
        raise FileNotFoundError(f"DejaVuSans.ttf not found at {DEJAVU_TTF_PATH}. Please manually place it in the srtemodules folder.")
    if not os.path.exists(DEJAVU_JSON_PATH):
        raise FileNotFoundError(f"DejaVuSans.json not found at {DEJAVU_JSON_PATH}. Please manually place it in the srtemodules folder.")


    pdf = FPDF("P", "mm", "A4")

    for _, row in student_list.iterrows():
        pdf.add_page()
        pdf.ln()

        pdf.add_font('DejaVuSans', '', DEJAVU_TTF_PATH, uni=True)
        pdf.add_font('DejaVuSans', 'B', DEJAVU_TTF_PATH, uni=True)

        # Page header section
        pdf.set_font("DejaVuSans", "B", 12)
        pdf.set_y(7)
        pdf.cell(0, 5, "BABCOCK UNIVERSITY", 0, 1, "C") # Centered
        
        pdf.set_font("DejaVuSans", "B", 12)
        pdf.set_y(12)
        pdf.set_x(57)
        pdf.cell(0, 5, "OFFICE OF INSTITUTIONAL EFFECTIVENESS", 0, 1, "L")
        
        pdf.set_font("DejaVuSans", "B", 12)
        pdf.set_y(17)
        pdf.set_x(45)
        pdf.cell(0, 5, "STUDENT RATING OF TEACHING EFFECTIVENESS (SRTE)", 0, 1, "L")
        
        pdf.set_font("DejaVuSans", "B", 12)
        pdf.set_y(22)
        pdf.set_x(49)
        pdf.cell(0, 5, f"{semester} SEMESTER OF {year} ACADEMIC SESSION", 0, 1, "L")
        pdf.set_y(30)

        header_summary = ['SUMMARY OF SCORES:', 'OVERALL MEAN', 'OVERALL RATING']
        w = [75.0, 55.0, 55.0]
        height = 7
        
        pdf.set_x(15)
        pdf.set_font("DejaVuSans", "B", 12)
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
        pdf.set_font("DejaVuSans", "B", 12)
        for x in range(len(header_summary)):
            pdf.cell(w[x], height, header_summary[x], 0, 0, 'L')

        pdf.ln(6)
        pdf.set_x(18)
        pdf.set_font('DejaVuSans', '', 12)
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
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.cell(72, height, '* \tEvaluation Score', 0, 0, 'L')
        pdf.cell(35, height, str(row['ES Overall']) if pd.notna(row['ES Overall']) else '', 0, 0, 'C')
        pdf.cell(75, height, f"{row['ES %']}%" if pd.notna(row['ES %']) else '', 0, 1, 'C')
        pdf.ln()

        # Filter comments for the current lecturer and course
        filter_lecturer = df[df['Lecturer Name'] == str(row['Lecturer Name'])]
        filter_course = filter_lecturer[filter_lecturer['Course Title'] == str(row['Course Title'])]
        
        # --- LIKES SECTION ---
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(15)
        pdf.cell(0, height, 'OPEN ENDED ASSESSMENT', 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, '1. Indicate three things you experienced in this course that you liked', 0, 1, "L")
        
        likes_formatted, likes_polarities = extract_likes(df, filter_course)
        
        pdf.set_font('DejaVuSans', '', 12)
        w_comment = 170
        
        if likes_formatted:
            for item in likes_formatted:
                pdf.set_x(18)
                pdf.multi_cell(w_comment, height, f'* \t{item}', 0, 'L')
                pdf.ln(2)
            if likes_polarities:
                avg_likes_polarity = np.mean(likes_polarities)
                # Pass a dummy string for text, as we only need the polarity value for category determination
                _, avg_likes_category = analyze_sentiment("dummy", avg_likes_polarity) 
                pdf.set_font('DejaVuSans', 'B', 10)
                pdf.set_x(18)
                pdf.cell(0, height, f'Overall Sentiment for Likes: {avg_likes_category} (Avg. Polarity: {avg_likes_polarity:.2f})', 0, 1, 'L')
                pdf.ln(2)
        else:
            pdf.set_x(18)
            pdf.multi_cell(w_comment, height, '* No specific likes mentioned.', 0, 'L')
            pdf.ln(2)
        
        pdf.ln()

        # --- DISLIKES SECTION ---
        pdf.set_font('DejaVuSans', 'B', 12)
        pdf.set_x(15)
        pdf.cell(0, height, '2. List three things you experienced that you did not like', 0, 1, "L")
        
        dislikes_formatted, dislikes_polarities = extract_dislikes(df, filter_course)
        
        pdf.set_font('DejaVuSans', '', 12)
        
        if dislikes_formatted:
            for item in dislikes_formatted:
                pdf.set_x(18)
                pdf.multi_cell(w_comment, height, f'* \t{item}', 0, 'L')
                pdf.ln(2)
            if dislikes_polarities:
                avg_dislikes_polarity = np.mean(dislikes_polarities)
                # Pass a dummy string for text, as we only need the polarity value for category determination
                _, avg_dislikes_category = analyze_sentiment("dummy", avg_dislikes_polarity) 
                pdf.set_font('DejaVuSans', 'B', 10)
                pdf.set_x(18)
                pdf.cell(0, height, f'Overall Sentiment for Dislikes: {avg_dislikes_category} (Avg. Polarity: {avg_dislikes_polarity:.2f})', 0, 1, 'L')
                pdf.ln(2)
        else:
            pdf.set_x(18)
            pdf.multi_cell(w_comment, height, '* No specific dislikes mentioned.', 0, 'L')
            pdf.ln(2)
        
        pdf.ln()

        # Official Use and Footnote sections
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
        pdf.set_font('DejaVuSans', '', 10)
        pdf.cell(0, 2, f'Page {pdf.page_no()}', 0, 0, 'C')
    
    # Sanitize the filename for invalid characters
    sanitized_lecturer_name = re.sub(r'[\\/:*?"<>|]', '_', str(row['Lecturer Name']).replace(',', '').replace('.', '').strip())
    sanitized_course_title = re.sub(r'[\\/:*?"<>|]', '_', str(row['Course Title']).strip())

    # Construct the full output path
    full_output_filename = os.path.join(output_dir, f"{sanitized_lecturer_name}_{sanitized_course_title}.pdf")
    pdf.output(full_output_filename, "F")
