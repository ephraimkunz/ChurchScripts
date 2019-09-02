# MinisteringReport
Create a Google Sheets spreadsheet to report ministering, given a pdf from Leader and Clerk resources

## Introduction
We needed a way to record ministering interviews each quarter. Google Sheets allows collaborative editing, but it was labor intensive to create this spreadsheet. Why not automate it?

## Getting started
* Get the PDF which we will use to generate our report
  1. Go to the Church's [website](lds.org)
  2. Sign in on the upper left
  3. Click 'Leader and Clerk Resources' in the upper left
  4. Under the 'Organizations' tab, under the 'Ministering' subheading, click Elder's Quorum
  5. Click the Print button under the 'Companionships' tab.
  6. Select 'Companionships Report' and 'Single Copy'. Make sure contact information is not included.
  7. Put this PDF in the same directory as the python file in the cloned repo.
* Install Google API tools. Do this with `pip install --upgrade google-api-python-client`. 
* Get Google API access permission. Follow the guide [here](https://developers.google.com/sheets/api/quickstart/python). Just do step 1. You'll also need to add the Google Drive API under the same project. No need to generate more oauth credentials.
* Do `brew install poppler` on Mac.
* Make any changes necessary in create_ministering_report.py. At the very least, you will want to change the name of the folder to put the generated Google Sheet in. Unless yours is also named Elders Quorum.
* Run everything with `python create_ministering_report.py`. We use Python 2.

## Future work
* Clean up code to be more modular / object oriented.
* Add ability to create and download PDF automatically.
* Multiple tabs on Sheet for multiple districts?
