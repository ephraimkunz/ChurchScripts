import os
from pipes import quote
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import datetime

# Which district
NONE = ""
DISTRICT_1 = "District 1 - Drew Pearson"
DISTRICT_2 = "District 2 - Alex Madsen"
DISTRICT_3 = "District 3 - Scott Peterson"
DISTRICT_4 = "District 4 - Cole Paullin"

# State machine states
GET_COMPS = "get comps"
GET_PEOPLE_MINISTERED_TO = "get people"
GET_DISTRICT = "get district"

class Companionship:
    def __init__(self):
        self.companions = []
        self.people_ministered_to = []
        self.district = NONE

    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return "Companionship: {}\n\tTeach: {}\n\tDistrict: {}\n".format(self.companions, self.people_ministered_to, self.district)

def extractComps(current_index, file_lines):
    companionship = Companionship()
    # Companions in form: first, space, second, [others], space
    companionship.companions.append(file_lines[current_index])
    current_index += 2
    while(current_index < len(file_lines) and file_lines[current_index] != ""):
        companionship.companions.append(file_lines[current_index])
        current_index += 1
    current_index += 1 # Skip blank space
    return companionship, current_index

def extractPeopleMinisteredTo(current_index, file_lines, companionship):
    while(current_index < len(file_lines) and file_lines[current_index] != ""):
        companionship.people_ministered_to.append(file_lines[current_index])
        current_index += 1
    current_index += 1
    return companionship, current_index

def extractDistrict(current_index, file_lines, companionship):
    if file_lines[current_index].endswith("1"):
        companionship.district = DISTRICT_1
    elif file_lines[current_index].endswith("2"):
        companionship.district = DISTRICT_2
    elif file_lines[current_index].endswith("3"):
        companionship.district = DISTRICT_3
    else:
        companionship.district = DISTRICT_4
    
    current_index += 2
    return companionship, current_index

def getDataFromAssignments(assignments):
    data = []
    current_row = 0
    current_district = ""

    # Set up column headers
    item = {
        "startRow": 0,
        "startColumn": 0,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Districts"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 1,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Companionships"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"}, 
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 2,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Ministerees"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 3,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Made Contact"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 3,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Notes"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 3,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Goals"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    item = {
        "startRow": 0,
        "startColumn": 4,
        "rowData": [{"values": [{
            "userEnteredValue":{"stringValue": "Date of Interview"},
            "userEnteredFormat":{
                "textFormat": {"bold": "true"},
                "horizontalAlignment": "CENTER"}
        }]}]
    }
    data.append(item)

    for assignment in assignments:
        current_row += 1
        if assignment.district != current_district:
            item = {
                "startRow": current_row,
                "startColumn": 0,
                "rowData": [{"values": [{
                    "userEnteredValue":{"stringValue": assignment.district},
                    "userEnteredFormat":{
                        "textFormat": {"bold": "true"},
                        "horizontalAlignment": "CENTER"}
                }]}]
            }
            current_district = assignment.district
            data.append(item)
            current_row += 1
        for comp in assignment.companions:
            item = {
                "startRow": current_row,
                "startColumn": 1,
                "rowData": [{"values": [{"userEnteredValue":{"stringValue": comp}}]}]
            }
            data.append(item)
            current_row += 1

        for person in assignment.people_ministered_to:
            item = {
                "startRow": current_row,
                "startColumn": 2,
                "rowData": [{"values": [{"userEnteredValue":{"stringValue": person}}]}]
            }
            data.append(item)
            current_row += 1
    return data


if __name__ == "__main__":

    input_file_name = "Ministering Companions Report"

    command = 'pdftotext -nopgbrk {}.pdf'.format(quote(input_file_name))
    os.system(command)

    txt_file_name = '{}.txt'.format(input_file_name)
    assignments = []
    with open(txt_file_name) as txt_file:
        file_string = txt_file.readlines()
        file_lines = [line.strip() for line in file_string]
        file_lines = file_lines[:] # Skip intro data
        file_lines = file_lines[:-3]
        print(file_lines)

        state = GET_COMPS
        current_index = 0
        companionship = None
        while current_index < len(file_lines):
            if state == GET_COMPS:
                companionship, current_index = extractComps(current_index, file_lines)
                state = GET_PEOPLE_MINISTERED_TO
            elif state == GET_PEOPLE_MINISTERED_TO:
                companionship, current_index = extractPeopleMinisteredTo(current_index, file_lines, companionship)
                state = GET_DISTRICT
            elif state == GET_DISTRICT:
                companionship, current_index = extractDistrict(current_index, file_lines, companionship)
                assignments.append(companionship)
                companionship = None
                state = GET_COMPS

    assignments.sort(key=lambda x: x.district)
    print(assignments)

    # Create Google sheet
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Google drive to move sheet to correct folder
    drive_service = build('drive', 'v3', http=creds.authorize(Http()))


    spreadsheet_body = {
        "properties": {"title": "Ministering report - {}".format(datetime.datetime.now().isoformat())},
        "sheets": [{
            "properties": {"title": "All districts"},
            "data": getDataFromAssignments(assignments)
        }]
    }

    request = service.spreadsheets().create(body=spreadsheet_body)
    response = request.execute()

    spreadsheet_id = response["spreadsheetId"]
    sheet_id = response["sheets"][0]["properties"]["sheetId"]
    url = response["spreadsheetUrl"]

    # Fit columns to correct width
    update_body = {
        "requests": [
            {
                "autoResizeDimensions": {
                    "dimensions": {
                    "sheetId": sheet_id,
                    "dimension": "COLUMNS",
                    "startIndex": 0,
                    "endIndex": 3
                    }
                }
            }
        ]
    }

    request = service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=update_body)
    response = request.execute()

    # Move file to correct folder
    results = drive_service.files().list(q="name='Elders Quorum'", pageSize=10, fields="files(id, name)").execute()
    folder_id = results["files"][0]['id']

    # Retrieve the existing parents to remove
    file = drive_service.files().get(fileId=spreadsheet_id,
                                    fields='parents').execute()

    previous_parents = ",".join(file.get('parents'))

    # Move the file to the new folder
    file = drive_service.files().update(fileId=spreadsheet_id,
                                    addParents=folder_id,
                                    removeParents=previous_parents,
                                    fields='id, parents').execute()


    print("The new sheet can be found here: {}".format(url))



