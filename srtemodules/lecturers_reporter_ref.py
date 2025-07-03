# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'

import numpy as np
import pandas as pd

# from fpdf import FPDF
from srtemodules.srte_report import get_report


def generate_lec_report(summary, df, semester, year, lecturer=None):
    if lecturer == None:
        # Create report for all lecturers in a school
        lecturers = summary["Lecturer Name"].unique()
        for name in lecturers:
            student_list = summary[summary["Lecturer Name"] == name]

            if len(student_list) > 1:
                get_report(student_list, df, semester, year)
            elif len(student_list) == 1:
                get_report(student_list, df, semester, year)
    else:
        # Create report for a single lecturer
        student_list = summary[summary["Lecturer Name"] == lecturer]
        # student_list = student_list[student_list['Resp Rate'] >= 70]
        if len(student_list) > 1:
            get_report(student_list, df, semester, year)
        elif len(student_list) == 1:
            get_report(student_list, df, semester, year)
    # print("Report generated successfully...")
