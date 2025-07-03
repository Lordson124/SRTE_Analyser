import pandas as pd
import numpy as np
from fpdf import FPDF
from srtemodules.comments_extractor import extract_likes, extract_dislikes

def get_report(student_list, df, semester, year):
    pdf = FPDF('P','mm','A4')
                
    for _, row in student_list.iterrows():
        pdf.add_page()
        pdf.ln()
        # Page header section
        pdf.set_font('Times','B',12)
        pdf.set_y(7)
        pdf.set_x(80)
        pdf.cell(0, 5, "BABCOCK UNIVERSITY", 0, 1, 30)
        pdf.set_font('Times','B',12)
        pdf.set_y(12)
        pdf.set_x(57)
        pdf.cell(0, 5, "OFFICE OF INSTITUTIONAL EFFECTIVENESS", 0, 1, "L")
        pdf.set_font('Times','B',12)
        pdf.set_y(17)
        pdf.set_x(45)
        pdf.cell(0, 5, "STUDENT RATING OF TEACHING EFFECTIVENESS (SRTE)", 0, 1, "L")
        pdf.set_font('Times','B',12)
        pdf.set_y(22)
        pdf.set_x(49)
        pdf.cell(0, 5, "{} SEMESTER OF {} ACADEMIC SESSION".format(semester, year), 0, 1, "L")
        pdf.set_font('Times','B',12)
        pdf.set_y(30)

        header = ['SUMMARY OF SCORES:', 'OVERALL MEAN', 'OVERALL RATING']
        w = [75.0, 55.0, 55.0]
        height = 7
        # count +=1
        pdf.set_x(15)
        pdf.cell(0, height, 'SCHOOL: {}'.format(str(row['School'])), 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, 'DEPARTMENT: {}'.format(str(row['Dept'])), 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, 'COURSE CODE/TITLE: {}'.format(str(row['Course Title'])), 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, 'NAME OF LECTURER: {}'.format(str(row['Lecturer Name'])), 0, 1, "L")
        pdf.set_x(15)
        pdf.ln(3)
        
        pdf.set_x(15)
        for x in range(0,3):
            pdf.cell(w[x],height,header[x],0,0,'L')

        pdf.ln(6)
        pdf.set_x(18)
        pdf.set_font('Times','',12)
        pdf.cell(72,height,'* \tTeaching Methodology',0,0,'L')
        pdf.cell(35,height,str(row['TM Overall']),0,0,'C')
        pdf.cell(75,height,str(row['TM %'])+'%',0,1,'C')
        pdf.set_x(18)
        pdf.cell(72,height,'* \tTeacher\'s Assessment Procedure',0,0,'L')
        pdf.cell(35,height,str(row['TA Overall']),0,0,'C')
        pdf.cell(75,height,str(row['TA %'])+'%',0,1,'C')
        pdf.set_x(18)
        pdf.cell(72,height,'* \tClassroom Management',0,0,'L')
        pdf.cell(35,height,str(row['CM Overall']),0,0,'C')
        pdf.cell(75,height,str(row['CM %'])+'%',0,1,'C')
        pdf.set_x(18)
        pdf.cell(72,height,'* \tIntegration of Faith',0,0,'L')
        pdf.cell(35,height,str(row['IF Overall']),0,0,'C')
        pdf.cell(75,height,str(row['IF %'])+'%',0,1,'C')
        pdf.set_x(18)
        pdf.cell(72,height,'* \tTeacher\'s Attendance & Punctuality',0,0,'L')
        pdf.cell(35,height,str(row['PTA Overall']),0,0,'C')
        pdf.cell(75,height,str(row['PTA %'])+'%',0,1,'C')
        pdf.set_x(18)
        pdf.set_font('Times','B',12)
        pdf.cell(72,height,'* \tEvaluation Score',0,0,'L')
        pdf.cell(35,height,str(row['ES Overall']),0,0,'C')
        pdf.cell(75,height,str(row['ES %'])+'%',0,1,'C')
        pdf.ln()

        filter_lecturer = df[df['Lecturer Name'] == str(row['Lecturer Name'])]
        filter_course = filter_lecturer[filter_lecturer['Course Title'] == str(row['Course Title'])]
        # filter_course = filter_course.head(3)
        
        # Print comments
        pdf.set_x(15)
        pdf.cell(0, height, 'OPEN ENDED ASSESSMENT', 0, 1, "L")
        pdf.set_x(15)
        pdf.cell(0, height, '1. Indicate three things you experienced in this course that you liked', 0, 1, "L")
        
        likes = extract_likes(df, filter_course)
        
        pdf.set_font('Times','',12)
        
        w = 170        
        count = 0
        new_collection = []

        for i, item in enumerate(likes,1):
            count += 1
            if count <= 3:
                new_collection.append(item)
                if count == 3:
                    joined_text = ', '.join([i for i in new_collection])
                    pdf.set_x(18)
                    pdf.multi_cell(w,height, '* \t{}'.format((str((joined_text.encode("ascii", "ignore")).decode()).capitalize()).strip()),0,'L')
                    count = 0
                    new_collection.clear()
                elif count < 3 and item == likes[-1]:
                    joined_text = ', '.join([i for i in new_collection])
                    pdf.set_x(18)
                    pdf.multi_cell(w,height, '* \t{}'.format((str((joined_text.encode("ascii", "ignore")).decode()).capitalize()).strip()),0,'L')
        
        pdf.ln()

        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.cell(0, height, '2. List three things you experienced that you did not like', 0, 1, "L")
        
        dislikes = extract_dislikes(df, filter_course)
        
        pdf.set_font('Times','',12)
        
        count = 0
        new_collection = []

        for i, item in enumerate(dislikes,1):
            count += 1
            if count <= 3:
                new_collection.append(item)
                if count == 3:
                    joined_text = ', '.join([i for i in new_collection])
                    pdf.set_x(18)
                    pdf.multi_cell(w,height, '* \t{}'.format((str((joined_text.encode("ascii", "ignore")).decode()).capitalize()).strip()),0,'L')
                    count = 0
                    new_collection.clear()
                elif count < 3 and item == dislikes[-1]:
                    joined_text = ', '.join([i for i in new_collection])
                    pdf.set_x(18)
                    pdf.multi_cell(w,height, '* \t{}'.format((str((joined_text.encode("ascii", "ignore")).decode()).capitalize()).strip()),0,'L')
        

        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.ln()
        
        '''pdf.cell(200,height,
            'This evaluation was done by {} of {} registered students {} {}{} student\'s participation.'.format(row['No'], int(np.round(row['Class Pop'],0)), '=', np.round(row['Resp Rate'],1), '%'),
            0,1,'L'
        )'''
        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.cell(200,height,'Footnote:',0,1,'L')
        pdf.set_font('Times','',12)
        pdf.set_x(15)
        pdf.cell(200,height,'1.00 - 1.99=Poor, 2.00 - 2.49=Fair, 2.50 - 3.49=Good, 3.50 - 4.49=Very Good, 4.50 - 5.00=Excellent',0,1,'L')    
    
        pdf.ln()
        #pdf.dashed_line(15, 200, 45,200, dash_length=1, space_length=1)
        pdf.set_font('Times','B',12)
        pdf.set_x(80)
        pdf.cell(200,height,'FOR OFFICIAL USE ONLY:',0,1,'L')
        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.cell(200,height,'No. of students who took this course: {}'.format(row['Class Pop']),0,1,'L')
        
        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.cell(200,height,'No. of students who evaluated this course: {}'.format(row['No']),0,1,'L')
                 
        pdf.set_font('Times','B',12)
        pdf.set_x(15)
        pdf.cell(200,height,'Percent of students who evaluated this course: {}{}'.format(np.round(row['Resp Rate'],1), '%'),0,1,'L')
        
        pdf.ln()
        '''pdf.ln()
        pdf.set_font('Times','',12)
        pdf.set_x(15)
        image_path = './ccc.PNG'
        pdf.cell(200,height,"Schedule Officer's Signature:",0,0,'L')
        
        pdf.set_x(65)
        pdf.image(image_path,pdf.get_x(),pdf.get_y(),40,10)
        #pdf.cell(200,height,pdf.image(image_path,pdf.get_x(),pdf.get_y(),40,20),0,0,'L')
        
        from datetime import datetime
        date_time = datetime.today().strftime("%d/%m/%Y")
        
        pdf.set_font('Times','',12)
        pdf.set_x(120)
        pdf.cell(200,height,'Date: {}'.format(date_time),0,1,'L')
        
        pdf.ln()
        pdf.ln()
        pdf.set_font('Times','',12)
        pdf.set_x(15)
        pdf.cell(200,height,"AVP, IE's Signature:____________________",0,0,'L')
        
        pdf.set_font('Times','',12)
        pdf.set_x(120)
        pdf.cell(200,height,'Date:____________________',0,1,'L')'''
        

        if row['No'] > row['Class Pop']:
            pdf.set_font('Times','B',12)
            pdf.set_x(10)
            pdf.ln()
            pdf.multi_cell(200,height,'Note: This evaluation is invalid, as the number of students that rated this course is more than the number of registered students for this course.',0,'L')

        pdf.set_y(-25)
        pdf.cell(0,2,'Page {}'.format(pdf.page_no()),0,0,'C')
    pdf.output("{}.pdf".format(str(row["Lecturer Name"]).replace(",", "").replace(".", "")), "F")