PhishViz

About the Project

PhishViz is a social engineering reporting application developed to convert GoPhish results into graphical outputs and assist with reporting. This project aims to facilitate the creation, editing, and reporting of phishing templates used in security tests. Users can add customer information, work on pre-made templates, and download the data in Excel format.

Important Note:
You need to update the API URL on line 7 in report.py according to your project. Example usage:

API_URL = "https://gophish-server:3333/api/campaigns/?api_key=api_key"

Features
	•	Phishing Template Management:
	•	Add, edit, and delete phishing templates.
	•	Dynamic template editing with CKEditor.
	•	Sample Data:
	•	Display the generated data in a table.
	•	Create and download sample data in Excel format.
	•	Customer Information:
	•	Enter and store customer information.
	•	GoPhish Results Reporting:
	•	Retrieve campaign data from the GoPhish API.
	•	Export campaign timeline data into an Excel report with specified columns.
	•	Indicate the processed campaign ID in the report file name and console output.
	•	Graphical Reporting:
	•	Reporting with graphical outputs of GoPhish results (using Matplotlib).

How to Install

1. Create a Virtual Environment

python3 -m venv venv
source venv/bin/activate    # For Linux/MacOS
# or
venv\Scripts\activate       # For Windows

2. Install Dependencies

All dependencies required to run the project are specified in the requirements.txt file. Install all dependencies using the following command:

pip install -r requirements.txt

3. Start the Application

To run the main interface:

python3 app.py

How to Use

Phishing Template Management
	1.	Log in to the PhishViz interface and navigate to the Phishing Templates page.
	2.	Use the “Add New Template” button to create a template.
	3.	You can edit existing templates or delete them.

Sample Data
	1.	View the data as a table on the Sample Data page.
	2.	Use the “Download” link to download the Excel file.

Reporting GoPhish Results (report.py)

The report.py tool retrieves campaign data from the GoPhish API and lists the IDs and names of existing campaigns. The user selects the campaign ID they wish to report from the list. The timeline data of the selected campaign is then exported to an Excel report with the following columns:
	•	People who received the email
	•	People who read the email
	•	Email reading date and time
	•	People who clicked the link
	•	People who had a data breach
	•	Number of times executed

Steps for Use:
	1.	Run the following command:

python3 report.py


	2.	When the script runs, it will list the IDs and names of the current campaigns on the screen. For example:

Current campaigns:
ID: 15 - Name: Test1
ID: 17 - Name: Test2
ID: 18 - Name: Test3
...


	3.	Enter the campaign ID you wish to report. The timeline data of the selected campaign will be generated as a file named Campaign_Report_ID_<selected_id>.xlsx. The console output will indicate which campaign ID was processed.

Usage Video

You can watch the video with detailed explanations on how to use the project via the following link:

https://www.linkedin.com/feed/update/urn:li:activity:7289951322726916096/

PhishViz Demo Video

Technical Details
	•	Language & Framework: Python 3.13, Flask
	•	Database: Flask-SQLAlchemy
	•	Excel Support: Pandas, xlsxwriter
	•	Template Editing: CKEditor integration
	•	Graphing: Matplotlib (for graphical reporting)
	•	Modern & Responsive Interface: Bootstrap

Support

If you encounter any issues, you can get help through the following channels:

- **Twitter:** [sefabasnak](https://twitter.com/sefabasnak)
- **LinkedIn:** [linkedin/in/sefabasnak](https://www.linkedin.com/in/sefabasnak)

© 2025 PhishViz. All Rights Reserved.
