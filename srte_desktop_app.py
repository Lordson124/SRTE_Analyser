import sys
import os
import pandas as pd
import glob
import pathlib
from zipfile import ZipFile
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTextEdit, QLineEdit, QCheckBox, QComboBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QStandardPaths # QStandardPaths for Documents folder

# --- Import your existing SRTE modules ---
# Ensure your srtemodules directory is correctly added to sys.path
# This is crucial for the desktop app to find your modules
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import your modules
from srtemodules.analyzer import analyze
from srtemodules.data_standardizer import standardize_lecturer_data
from srtemodules.lecturers_reporter_ref import generate_lec_report # This function will be updated
# from srtemodules.srte_report import get_report # Not directly called here, but by generate_lec_report


# --- Worker Thread for Long-Running Tasks ---
# GUI applications should never run long-running tasks directly on the main thread,
# as it will freeze the UI. We'll use a QThread for report generation.
class ReportGeneratorWorker(QThread):
    # Signals to communicate back to the main GUI thread
    finished = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    report_generated = pyqtSignal(str) # Signal to pass the generated PDF path or zip path

    def __init__(self, sum_data, com_data, semester, session, lecturer_name=None):
        super().__init__()
        self.sum_data = sum_data
        self.com_data = com_data
        self.semester = semester
        self.session = session
        self.lecturer_name = lecturer_name
        self.output_path = "" # To store the final output path (PDF or Zip)

    def run(self):
        try:
            self.progress.emit("Determining output directory...")
            # Define output directory: User's Documents/SRTE_Reports
            documents_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            output_dir = os.path.join(documents_path, "SRTE_Reports")
            os.makedirs(output_dir, exist_ok=True) # Create directory if it doesn't exist
            
            self.progress.emit("Starting report generation...")
            
            # Call your existing report generation logic, passing the output_dir
            # generate_lec_report will now save files to this directory
            generate_lec_report(
                self.sum_data, self.com_data, self.semester, self.session, self.lecturer_name, output_dir
            )
            
            if self.lecturer_name: # Single lecturer report
                # Assuming generate_lec_report saves a single PDF with a specific name
                # We need to find that specific PDF. This is a bit fragile.
                # A better way would be for generate_lec_report to return the path.
                # For now, let's assume it's named consistently.
                sanitized_lecturer_name = re.sub(r'[\\/:*?"<>|]', '_', str(self.lecturer_name).replace(',', '').replace('.', '').strip())
                # This part is tricky as we don't have the course title here.
                # It's better if generate_lec_report returns the actual filename.
                # For now, we'll just open the directory.
                self.output_path = output_dir # Point to the directory for single reports
                self.report_generated.emit(f"Report for {self.lecturer_name} generated successfully!")
            else: # All lecturers reports - need to zip them
                self.progress.emit("Zipping all generated reports...")
                zip_filename = os.path.join(output_dir, f"SRTE_Reports_{self.session}_{self.semester}.zip")
                
                # Get all PDF files generated in the output_dir for this run
                # This assumes no other PDFs are being generated concurrently or are left over
                pdf_files = glob.glob(os.path.join(output_dir, "*.pdf"))

                if not pdf_files:
                    self.error.emit("No PDF reports were found to zip.")
                    self.finished.emit()
                    return

                with ZipFile(zip_filename, 'w') as zippedObj:
                    for pdf_path in pdf_files:
                        zippedObj.write(pdf_path, os.path.basename(pdf_path)) # Add to zip
                        pathlib.Path(pdf_path).unlink() # Clean up: remove original PDF after zipping

                self.output_path = zip_filename
                self.report_generated.emit(f"All reports generated and zipped to {os.path.basename(zip_filename)}!")
            
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Error during report generation: {e}")
            self.finished.emit()


class SRTEApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SRTE Analytics Desktop Application")
        self.setGeometry(100, 100, 1000, 750) # Adjusted size for better layout

        self.init_ui()

        self.raw_data_df = None
        self.summary_data_df = None
        self.comment_data_df = None

    def init_ui(self):
        main_layout = QHBoxLayout() # Main layout: Menu on left, Content on right

        # --- Left Menu Panel ---
        menu_layout = QVBoxLayout()
        menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.menu_label = QLabel("<h3>Menu Items</h3>")
        menu_layout.addWidget(self.menu_label)

        self.action_selector = QComboBox()
        self.action_selector.addItems(["Select action", "Upload Data", "Generate Reports"])
        self.action_selector.currentIndexChanged.connect(self.display_content_panel)
        menu_layout.addWidget(self.action_selector)

        # Add a placeholder for file upload buttons that will be dynamically shown
        self.upload_raw_btn = QPushButton("Upload Raw Data (Excel)...")
        self.upload_raw_btn.clicked.connect(self.upload_raw_data)
        self.upload_raw_btn.setVisible(False) # Hidden by default
        menu_layout.addWidget(self.upload_raw_btn)

        self.upload_summary_btn = QPushButton("Upload SRTE Summary (Excel)...")
        self.upload_summary_btn.clicked.connect(self.upload_summary_data)
        self.upload_summary_btn.setVisible(False)
        menu_layout.addWidget(self.upload_summary_btn)

        self.upload_comment_btn = QPushButton("Upload SRTE Comment (Excel)...")
        self.upload_comment_btn.clicked.connect(self.upload_comment_data)
        self.upload_comment_btn.setVisible(False)
        menu_layout.addWidget(self.upload_comment_btn)

        self.analyze_data_btn = QPushButton("Analyze and Standardize Data")
        self.analyze_data_btn.clicked.connect(self.analyze_and_standardize)
        self.analyze_data_btn.setVisible(False)
        menu_layout.addWidget(self.analyze_data_btn)

        self.check_new_codes_btn = QPushButton("Check New Course Codes")
        self.check_new_codes_btn.clicked.connect(self.check_new_course_codes)
        self.check_new_codes_btn.setVisible(False)
        menu_layout.addWidget(self.check_new_codes_btn)

        menu_layout.addStretch(1) # Pushes content to top

        main_layout.addLayout(menu_layout, 1) # Menu takes 1/4 width

        # --- Right Content Panel ---
        self.content_panel = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_panel.setLayout(self.content_layout)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.status_label = QLabel("<h3>Status: Ready</h3>")
        self.content_layout.addWidget(self.status_label)

        # Use a QScrollArea for the QTextEdit to ensure scrollability for large dataframes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.data_display_area = QTextEdit()
        self.data_display_area.setReadOnly(True)
        self.data_display_area.setPlaceholderText("Uploaded data or analysis results will appear here...")
        scroll_area.setWidget(self.data_display_area)
        self.content_layout.addWidget(scroll_area)

        # Report Generation Inputs (initially hidden)
        self.report_inputs_widget = QWidget()
        self.report_inputs_layout = QVBoxLayout()
        self.report_inputs_widget.setLayout(self.report_inputs_layout)

        input_row1 = QHBoxLayout()
        self.session_input = QLineEdit()
        self.session_input.setPlaceholderText("e.g., 2023/2024")
        input_row1.addWidget(QLabel("Session:"))
        input_row1.addWidget(self.session_input)

        self.semester_input = QLineEdit()
        self.semester_input.setPlaceholderText("e.g., FIRST or SECOND")
        input_row1.addWidget(QLabel("Semester:"))
        input_row1.addWidget(self.semester_input)
        self.report_inputs_layout.addLayout(input_row1)

        self.single_lecturer_checkbox = QCheckBox("Generate only one Lecturer's report")
        self.single_lecturer_checkbox.stateChanged.connect(self.toggle_lecturer_input)
        self.report_inputs_layout.addWidget(self.single_lecturer_checkbox)

        self.lecturer_name_input = QLineEdit()
        self.lecturer_name_input.setPlaceholderText("Enter Lecturer name (Standardized name expected!)")
        self.lecturer_name_input.setVisible(False) # Hidden by default
        self.report_inputs_layout.addWidget(self.lecturer_name_input)

        self.generate_report_btn = QPushButton("Generate Report")
        self.generate_report_btn.clicked.connect(self.generate_reports)
        self.report_inputs_layout.addWidget(self.generate_report_btn)

        self.open_output_folder_btn = QPushButton("Open Output Folder")
        self.open_output_folder_btn.clicked.connect(self.open_output_folder)
        self.open_output_folder_btn.setVisible(False) # Hidden until reports are generated
        self.report_inputs_layout.addWidget(self.open_output_folder_btn)
        
        self.report_inputs_widget.setVisible(False) # Hidden by default
        self.content_layout.addWidget(self.report_inputs_widget)


        self.content_layout.addStretch(1) # Pushes content to top

        main_layout.addWidget(self.content_panel, 3) # Content takes 3/4 width

        self.setLayout(main_layout)
        self.display_content_panel(0) # Initialize with "Select action" view

    def display_content_panel(self, index):
        action = self.action_selector.itemText(index)

        # Hide all specific action widgets
        self.upload_raw_btn.setVisible(False)
        self.upload_summary_btn.setVisible(False)
        self.upload_comment_btn.setVisible(False)
        self.analyze_data_btn.setVisible(False)
        self.check_new_codes_btn.setVisible(False)
        self.report_inputs_widget.setVisible(False)
        self.open_output_folder_btn.setVisible(False) # Hide output button on panel change
        
        self.data_display_area.clear() # Clear display area on action change
        self.status_label.setText("<h3>Status: Ready</h3>")

        if action == "Upload Data":
            self.upload_raw_btn.setVisible(True)
            self.analyze_data_btn.setVisible(True)
            self.check_new_codes_btn.setVisible(True)
            self.status_label.setText("<h3>Status: Upload Raw Data</h3>")
        elif action == "Generate Reports":
            self.upload_summary_btn.setVisible(True)
            self.upload_comment_btn.setVisible(True)
            self.report_inputs_widget.setVisible(True)
            self.status_label.setText("<h3>Status: Upload Summary & Comment Data</h3>")

    def toggle_lecturer_input(self, state):
        self.lecturer_name_input.setVisible(state == Qt.CheckState.Checked.value)

    def upload_raw_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Raw SRTE Data (Excel)", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                self.status_label.setText("<h3>Status: Reading raw data...</h3>")
                QApplication.processEvents() # Update UI immediately
                
                df = pd.read_excel(file_path)
                # Assuming the last two columns are not part of the core data
                df = df[df.columns[0:-2]] 
                
                header = [
                    "Course Title", "Lecturer Name", "TM1", "TM2", "TM3", "TM4", "TM5", "TM6", "TM7",
                    "TA8", "TA9", "TA10", "TA11", "TA12", "CM13", "CM14", "CM15", "CM16",
                    "IF17", "IF18", "IF19", "IF20", "IF21", "PTA22", "PTA23",
                ]
                if len(df.columns) == len(header):
                    df.columns = header
                    self.raw_data_df = df
                    self.data_display_area.setText(self.raw_data_df.to_html(index=False))
                    self.status_label.setText("<h3>Status: Raw data uploaded successfully.</h3>")
                else:
                    QMessageBox.warning(self, "Column Mismatch", 
                                        f"Error: The uploaded file has {len(df.columns)} columns, but {len(header)} columns were expected. Please check your raw data file format.")
                    self.status_label.setText("<h3>Status: Raw data upload failed.</h3>")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read raw Excel file: {e}")
                self.status_label.setText("<h3>Status: Raw data upload failed.</h3>")

    def upload_summary_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SRTE Summary Data (Excel)", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                self.status_label.setText("<h3>Status: Reading summary data...</h3>")
                QApplication.processEvents()
                
                df = pd.read_excel(file_path)
                df = df.dropna(axis=0) # Drop rows with any NaN values
                self.summary_data_df = df
                self.data_display_area.setText(self.summary_data_df.to_html(index=False))
                self.status_label.setText("<h3>Status: Summary data uploaded successfully.</h3>")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read summary Excel file: {e}")
                self.status_label.setText("<h3>Status: Summary data upload failed.</h3>")

    def upload_comment_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open SRTE Comment Data (Excel)", "", "Excel Files (*.xlsx)")
        if file_path:
            try:
                self.status_label.setText("<h3>Status: Reading comment data...</h3>")
                QApplication.processEvents()
                
                df = pd.read_excel(file_path)
                # Assuming columns 2 to 25 are not comments as per your srteapp.py
                df = df.drop(df.columns[2:25], axis=1) 
                
                header_col = ["Course Title", "Lecturer Name", "Course likes", "Course dislikes"]
                if len(df.columns) == len(header_col):
                    df.columns = header_col
                    self.comment_data_df = df
                    self.data_display_area.setText(self.comment_data_df.to_html(index=False))
                    self.status_label.setText("<h3>Status: Comment data uploaded successfully.</h3>")
                else:
                    QMessageBox.warning(self, "Column Mismatch", 
                                        f"Error: Comment file has {len(df.columns)} columns, but {len(header_col)} columns were expected. Please check your comment file format.")
                    self.status_label.setText("<h3>Status: Comment data upload failed.</h3>")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read comment Excel file: {e}")
                self.status_label.setText("<h3>Status: Comment data upload failed.</h3>")

    def analyze_and_standardize(self):
        if self.raw_data_df is None:
            QMessageBox.warning(self, "Missing Data", "Please upload raw SRTE data first.")
            return

        self.status_label.setText("<h3>Status: Analyzing and Standardizing data...</h3>")
        QApplication.processEvents() # Update UI immediately

        try:
            results_dict = analyze(self.raw_data_df.copy())

            output_text = "Analysis Results by School:\n\n"
            for school_name, school_df in results_dict.items():
                output_text += f"--- {school_name} ---\n"
                output_text += school_df.to_string() + "\n\n"
            
            self.data_display_area.setText(output_text)
            self.status_label.setText("<h3>Status: Analysis and standardization completed.</h3>")
            QMessageBox.information(self, "Success", "SRTE Analysis and Lecturer Standardization completed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {e}")
            self.status_label.setText("<h3>Status: Analysis failed.</h3>")

    def check_new_course_codes(self):
        if self.raw_data_df is None:
            QMessageBox.warning(self, "Missing Data", "Please upload raw SRTE data first.")
            return

        from srtemodules.coursecode import courses # Import here to avoid circular dependency if coursecode depends on analyzer
        
        self.status_label.setText("<h3>Status: Checking new course codes...</h3>")
        QApplication.processEvents()

        try:
            new_codes = []
            temp_df = self.raw_data_df.copy()
            temp_df["new"] = temp_df["Course Title"].str.strip()
            temp_df["new"] = temp_df["new"].str.split(" ")
            temp_df["new"] = temp_df["new"].apply(lambda x: x[0])
            temp_df["new"] = temp_df["new"].str.split(r"\d")
            temp_df["new"] = temp_df["new"].apply(lambda x: x[0])
            unique_codes = temp_df["new"].unique()

            for code in unique_codes:
                if code not in courses:
                    new_codes.append(code)

            if new_codes:
                self.data_display_area.setText("#### New Course Codes Found:\n" + ", ".join(new_codes))
                self.status_label.setText("<h3>Status: New course codes found.</h3>")
            else:
                self.data_display_area.setText("No new course codes found.")
                self.status_label.setText("<h3>Status: No new course codes found.</h3>")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to check new course codes: {e}")
            self.status_label.setText("<h3>Status: Course code check failed.</h3>")


    def generate_reports(self):
        if self.summary_data_df is None or self.comment_data_df is None:
            QMessageBox.warning(self, "Missing Data", "Please upload both SRTE Summary and Comment files first.")
            return

        session = self.session_input.text().strip()
        semester = self.semester_input.text().strip()
        lecturer_name = self.lecturer_name_input.text().strip() if self.single_lecturer_checkbox.isChecked() else None

        if not session or not semester:
            QMessageBox.warning(self, "Missing Input", "Please enter both session and semester.")
            return

        if self.single_lecturer_checkbox.isChecked() and not lecturer_name:
            QMessageBox.warning(self, "Missing Input", "Please enter the lecturer's name if generating a single report.")
            return
        
        self.status_label.setText("<h3>Status: Standardizing summary data for reports...</h3>")
        QApplication.processEvents()
        try:
            standardized_sum_data, unmatched_summary_lecturers = standardize_lecturer_data(self.summary_data_df.copy())
            
            if unmatched_summary_lecturers:
                warning_msg = "Warning: Some lecturers in the uploaded summary file were not found in the database:\n"
                for name in sorted(unmatched_summary_lecturers):
                    warning_msg += f"- {name}\n"
                warning_msg += "Please update your lecturer database for full consistency."
                QMessageBox.warning(self, "Lecturer Standardization Warning", warning_msg)
            else:
                self.status_label.setText("<h3>Status: Lecturers in summary data standardized.</h3>")

            self.report_worker = ReportGeneratorWorker(
                standardized_sum_data, self.comment_data_df.copy(), semester, session, lecturer_name
            )
            self.report_worker.finished.connect(self.report_generation_finished)
            self.report_worker.error.connect(self.report_generation_error)
            self.report_worker.progress.connect(self.update_status_label)
            self.report_worker.report_generated.connect(self.handle_report_generated)
            
            self.status_label.setText("<h3>Status: Generating reports... (This may take a while)</h3>")
            self.generate_report_btn.setEnabled(False) # Disable button during generation
            self.open_output_folder_btn.setVisible(False) # Hide output button until finished
            self.report_worker.start() # Start the worker thread

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed during summary data standardization: {e}")
            self.status_label.setText("<h3>Status: Report generation failed.</h3>")


    def report_generation_finished(self):
        self.generate_report_btn.setEnabled(True) # Re-enable button
        self.status_label.setText("<h3>Status: Report generation complete.</h3>")
        # Show the "Open Output Folder" button after completion
        self.open_output_folder_btn.setVisible(True) 

    def report_generation_error(self, message):
        QMessageBox.critical(self, "Report Generation Error", message)
        self.generate_report_btn.setEnabled(True)
        self.status_label.setText("<h3>Status: Report generation failed.</h3>")
        self.open_output_folder_btn.setVisible(True) # Still allow opening folder if some reports were made

    def update_status_label(self, message):
        self.status_label.setText(f"<h3>Status: {message}</h3>")

    def open_output_folder(self):
        # Determine the path to open based on whether a single file or a zip was generated
        output_path_to_open = self.report_worker.output_path if hasattr(self.report_worker, 'output_path') and self.report_worker.output_path else \
                              os.path.join(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation), "SRTE_Reports")
        
        if os.path.exists(output_path_to_open):
            # Use platform-specific command to open the file/folder
            if sys.platform == "win32":
                os.startfile(output_path_to_open)
            elif sys.platform == "darwin": # macOS
                os.system(f"open \"{output_path_to_open}\"")
            else: # linux variants
                os.system(f"xdg-open \"{output_path_to_open}\"")
        else:
            QMessageBox.warning(self, "Path Not Found", f"Output path does not exist: {output_path_to_open}")


    def handle_report_generated(self, message):
        # This signal is emitted when reports are successfully generated (single or zipped)
        QMessageBox.information(self, "Reports Generated", message)
        # The open_output_folder_btn is made visible in report_generation_finished


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = SRTEApp()
    ex.show()
    sys.exit(app.exec())
