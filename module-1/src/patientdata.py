import csv
from datetime import datetime, timezone
import pyinputplus as pyip
import tabulate
import re

DATE_FORMAT = "%Y-%m-%d"
PATIENT_ID_FORMAT = r"^P-[0-9]+$"

### GENERAL FUNCTIONS ###

def isEmptyDatabase(database):
    print(len(database))
    if len(database) < 2: return True
    else: return False

def get_current_datetime_str():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

def get_current_date_str():
    return datetime.today().strftime(DATE_FORMAT)

def date_to_str(date):
    return date.strftime(DATE_FORMAT)

def custom_filter(data, header, key, val):
    # get index of key in header
    index = header.index(key)
    
    # filter data where row[index] = val for each row in data
    filtered_data = list(filter(lambda row: row[index] == val, data))
    return filtered_data

def get_dict_of_list_data_header(database):
    # convert values of db into list without the header row
    data = list(database.values())[1:]
    # get header row from db
    header = database['column']
    return data, header

def display_dict_of_list(database):
    data, header = get_dict_of_list_data_header(database)
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def get_list_of_dict_data_header(database):
    data = [[i] + list(row.values())[1:] for i, row in enumerate(database[1:])]
    header = database[0]
    return data, header

def display_list_of_dict(database):
    data, header = get_list_of_dict_data_header(database)
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def display_data_header(data, header):
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def display_profile(patient_database, patient_id):
    '''
    Function to display a patient profile given an existing patient_id

    Args:
        patient_database (dict)
        patient_id (str)

    Returns:
        list
    '''
    print(f'''
Patient ID      : {patient_id}
First name      : {patient_database[patient_id][1]}
Last name       : {patient_database[patient_id][2]}
Gender          : {patient_database[patient_id][3]}
Birth date      : {patient_database[patient_id][4]}
''')
    return patient_database[patient_id][1:]

def display_new_data(data, title):
    '''
    Function to display

    Args:
        data (list)
        title (str)

    Returns:
        None
    '''
    patient_id, first_name, last_name, gender, birth_date = data[:5]
    room_type, admission_date, discharge_date, status = data[5:]

    print(f'''
{title}
Patient ID      : {patient_id}
First name      : {first_name}
Last name       : {last_name}
Gender          : {gender}
Birth date      : {birth_date}
Room type       : {' '.join(room_type.split(sep='_'))}
Admission date  : {admission_date}
Discharge date  : {discharge_date}
Status          : {status}
        ''')

def isAlphaName(name):
    '''
    Function to check if name (with white space characters allowed) is only alphabets

    Args:
        name (str): patient name

    Returns:
        bool
    '''
    return ''.join(name.split()).isalpha()
    
def isDuplicateProfile(database, profile):
    '''
    Function to check if profile for add new patient already exists

    Args:
        database (dict): patient data
        profile (list): list of first name, last name, gender, and birth date

    Returns:
        str
    '''
    key_match = ""
    for key, value in database.items():
        if key == 'column':
            continue
        else:
            if value[1:] == profile:
                key_match = key
    return key_match

def isAvailableRoom(bed_database, room_type):
    # get bed data with most recent timestamp
    data, header = get_list_of_dict_data_header(bed_database)
    most_recent_data = sorted(data, key=lambda x: x[1])[-1]

    # return True if bed_count of room_type > 0
    index = header.index(room_type)
    bed_count =  most_recent_data[index]
    if bed_count > 0: return True
    else: return False

### INPUT FUNCTIONS ###

def get_patient_id():
    isBreak = False
    while True:
        patient_id = pyip.inputStr(prompt="\nEnter Patient ID (e.g. P-1) or 0 to cancel: ")
        if patient_id == "0":
            isBreak = True
        elif not re.fullmatch(PATIENT_ID_FORMAT, patient_id):
            print("Invalid input.")
            continue
        break
    return patient_id, isBreak

def get_name(type):
    name = ""
    isBreak = False
    return name, isBreak

def get_gender():
    gender = ""
    isBreak = False
    return gender, isBreak

def get_date(type):
    date = ""
    isBreak = False
    return date, isBreak

def get_room_type():
    room_type = ""
    isBreak = False
    return room_type, isBreak

def get_status():
    status = ""
    isBreak = False
    return status, isBreak

### FEATURE FUNCTIONS ###

def display_patient(database):
    data, header = get_dict_of_list_data_header(database)

    while True:
        prompt = "\nDisplay by:\n"
        choices = ["All data",
                   "Patient ID",
                   "First name",
                   "Last name",
                   "Gender",
                   "Birth date",
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == choices[-1]:
            break

        elif response == choices[0]:
            display_data_header(data=data, header=header)

        else:
            while True:
                search_key = ""
                if response == choices[1]:
                    search_val = pyip.inputStr(prompt="\nEnter Patient ID (e.g. P-1) or 0 to cancel: ")
                    if search_val == "0":
                        break
                    elif not re.fullmatch(PATIENT_ID_FORMAT, search_val):
                        print("Invalid input.")
                        continue
                    search_key = "Patient_ID"

                elif response == choices[2]:
                    search_val = pyip.inputStr(prompt="\nEnter first name or 0 to cancel: ")
                    if search_val == "0":
                        break
                    elif not isAlphaName(search_val):
                        print("Invalid input.")
                        continue
                    # make sure name is separated by only one space
                    elif ' ' in search_val:
                        search_val = ' '.join(search_val.split().capitalize())
                    search_key = "First_Name"
                
                elif response == choices[3]:
                    search_val = pyip.inputStr(prompt="\nEnter last name or 0 to cancel: ")
                    if search_val == "0":
                        break
                    elif not ''.join(search_val.split()).isalpha():
                        print("Invalid input.")
                        continue
                    # make sure name is separated by only one space
                    elif ' ' in search_val:
                        search_val = ' '.join(search_val.split().capitalize())
                    search_key = "Last_Name"

                elif response == choices[4]:
                    choices = ["Male", "Female", "Return to previous menu"]
                    search_val = pyip.inputMenu(prompt="\nSelect gender:\n", choices=choices, numbered=True)
                    if search_val == choices[-1]:
                        break
                    search_key = "Gender"

                else:
                    search_val = pyip.inputDate(prompt="\nEnter birth date (YYYY-MM-DD) or 0 to cancel: ",
                                                formats=[DATE_FORMAT], allowRegexes=[r"^0$"])
                    if search_val == "0":
                        break
                    search_val = date_to_str(search_val)
                    search_key = "Birth_Date"

                filtered_data = custom_filter(data=data, header=header, key=search_key, val=search_val)
                if filtered_data:
                    display_data_header(data=filtered_data, header=header)
                else:
                    print(f"{response} {search_val} does not exist.")
                    continue
                
                break

def display_room(database):
    data, header = get_list_of_dict_data_header(database)

    while True:
        prompt = "\nDisplay by:\n"
        choices = ["All data",
                   "Patient ID",
                   "Room type",
                   "Admission date",
                   "Discharge date",
                   "Status",
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == choices[-1]:
            break

        elif response == choices[0]:
            display_data_header(data=data, header=header)
        
        else:
            while True:
                search_key = ""
                if response == choices[1]:
                    search_val = pyip.inputStr(prompt="\nEnter Patient ID (e.g. P-1) or 0 to cancel: ")
                    if search_val == "0":
                        break
                    elif not re.fullmatch(PATIENT_ID_FORMAT, search_val):
                        print("Invalid input.")
                        continue
                    search_key = "Patient_ID"

                elif response == choices[2]:
                    choices = ["VVIP", "VIP", "Kelas 1", "Kelas 2", "Kelas 3", "Return to previous menu"]
                    search_val = pyip.inputMenu(prompt="\nSelect room type:\n", choices=choices, numbered=True)
                    if search_val == choices[-1]:
                        break
                    elif ' ' in search_val:
                        search_val = '_'.join(search_val.split())
                    search_key = "Room_Type"

                elif response == choices[3]:
                    search_val = pyip.inputDate(prompt="\nEnter admission date (YYYY-MM-DD) or 0 to cancel: ",
                                                formats=[DATE_FORMAT], allowRegexes=[r"^0$"])
                    if search_val == "0":
                        break
                    search_val = date_to_str(search_val)
                    search_key = "Admission_Date"

                elif response == choices[4]:
                    search_val = pyip.inputDate(prompt="\nEnter discharge date (YYYY-MM-DD) or 0 to cancel: ",
                                                formats=[DATE_FORMAT], allowRegexes=[r"^0$"])
                    if search_val == "0":
                        break
                    search_val = date_to_str(search_val)
                    search_key = "Discharge_Date"

                else:
                    choices = ["COMPLETED", "ONGOING", "Return to previous menu"]
                    search_val = pyip.inputMenu(prompt="\nSelect status:\n", choices=choices, numbered=True)
                    if search_val == choices[-1]:
                        break
                    search_key = "Status"

                filtered_data = custom_filter(data=data, header=header, key=search_key, val=search_val)
                if filtered_data:
                    display_data_header(data=filtered_data, header=header)
                else:
                    print(f"{response} {search_val} does not exist.")
                    continue

                break

### INCOMPLETE: choices & implementation ###
def display_bed(database):
    data, header = get_list_of_dict_data_header(database)
    while True:
        prompt = "\nDisplay by:\n"
        choices = ["All data",
                   "Most recent", ### ADD SEARCH RANGE DATE ###
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == choices[0]:
            display_data_header(data=data, header=header)
        else:
            break

### INCOMPLETE: save changes to .csv ###
def add_new_patient(patient_database, room_database, bed_database, room_type):
    while True:
        first_name = pyip.inputStr(prompt="\nEnter first name or 0 to cancel: ")
        if first_name == "0":
            break
        elif not isAlphaName(first_name):
            print("Invalid input.")
            continue
        # make sure name is separated by only one space
        elif ' ' in first_name:
            first_name = ' '.join(first_name.split().capitalize())

        last_name = pyip.inputStr(prompt="\nEnter last name or 0 to cancel: ")
        if last_name == "0":
            break
        elif not isAlphaName(last_name):
            print("Invalid input.")
            continue
        # make sure name is separated by only one space
        elif ' ' in last_name:
            last_name = ' '.join(last_name.split().capitalize())

        choices = ["Male", "Female", "Return to previous menu"]
        gender = pyip.inputMenu(prompt="\nSelect gender:\n", choices=choices, numbered=True)
        if gender == choices[-1]:
            break

        birth_date = pyip.inputDate(prompt="\nEnter birth date (YYYY-MM-DD) or 0 to cancel: ",
                                    formats=[DATE_FORMAT], allowRegexes=[r"^0$"])
        if birth_date == "0":
            break
        birth_date = date_to_str(birth_date)
        
        profile = [first_name, last_name, gender, birth_date]
        key_match = isDuplicateProfile(patient_database, profile)
        if key_match:
            print(f"\nPatient profile already exists under Patient ID {key_match}.")
            display_profile(patient_database=patient_database, patient_id=key_match)
            confirmation = pyip.inputYesNo(prompt="Is it the same patient? (yes/no): ")
            if confirmation == "yes":
                print("Please add new visit instead.")
                break
            
        patient_id = f"P-{int(list(patient_database.keys())[-1][2:]) + 1}"
        admission_date = get_current_date_str()
        discharge_date = "N/A"
        status = "ONGOING"

        tmp_data = [patient_id, first_name, last_name, gender, birth_date,
                    room_type, admission_date, discharge_date, status]
        display_new_data(tmp_data, title="=== New Patient ===")

        confirmation = pyip.inputYesNo(prompt="Confirm changes? (yes/no): ")
        if confirmation == "yes":
            patient_database.update({patient_id: [patient_id, first_name, last_name, gender, birth_date]})

            headings = room_database[0]
            new_data = {headings[0]: len(room_database)-1,
                        headings[1]: patient_id,
                        headings[2]: room_type,
                        headings[3]: admission_date,
                        headings[4]: discharge_date,
                        headings[5]: status}
            room_database.append(new_data)
            
            headings = bed_database[0]
            new_data = bed_database[-1].copy()
            new_data[headings[0]] = len(bed_database)-1
            new_data[headings[1]] = get_current_datetime_str()
            new_data[room_type] -= 1  
            bed_database.append(new_data)
            print("Data saved.")
        else:
            print("Data not saved.")

        ### CONFIRM & SAVE TO .csv ###
        break

### INCOMPLETE: save changes to .csv ###    
def add_new_visit(patient_database, room_database, bed_database, room_type):
    while True:
        patient_id = pyip.inputStr(prompt="\nEnter Patient ID (e.g P-1) or 0 to cancel: ")
        if patient_id == "0":
            break
        elif not re.fullmatch(PATIENT_ID_FORMAT, patient_id):
            print("Invalid input.")
            continue
        elif patient_id not in patient_database:
            print(f"Patient ID {patient_id} does not exist.")
            continue
        
        first_name, last_name, gender, birth_date = display_profile(patient_database, patient_id)
        confirmation = pyip.inputYesNo(prompt="Looking for different patient? (yes/no): ")
        if confirmation == "yes":
            continue

        headings = room_database[0]
        admission_date = get_current_date_str()
        discharge_date = "N/A"
        status = "ONGOING"

        new_data = {headings[0]: len(room_database)-1,
                    headings[1]: patient_id,
                    headings[2]: room_type,
                    headings[3]: admission_date,
                    headings[4]: discharge_date,
                    headings[5]: status}
        
        tmp_data = [patient_id, first_name, last_name, gender, birth_date,
                    room_type, admission_date, discharge_date, status]
        display_new_data(tmp_data, title="=== New Visit ===")
        confirmation = pyip.inputYesNo(prompt="Confirm changes? (yes/no): ")
        if confirmation == "yes":
            room_database.append(new_data)
            
            headings = bed_database[0]
            new_data = bed_database[-1].copy()
            new_data[headings[0]] = len(bed_database)-1
            new_data[headings[1]] = get_current_datetime_str()
            new_data[room_type] -= 1  
            bed_database.append(new_data)
        
        ### CONFIRM & SAVE TO .csv ### 
        break    
    
def modify_patient(patient_database):
    while True:
        prompt = f"\nEnter Patient_ID to modify data or 0 to cancel: "
        patient_id = pyip.inputStr(prompt=prompt)
        if patient_id.upper() == "CANCEL":
            break
        else:
            while True:
                prompt = "\nModify:\n"
                choices = ["Full_Name",
                           "Gender",
                           "Birth_Date",
                           "Return to previous menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                if response == "Full_Name":
                    name = pyip.inputStr(prompt="Enter full name: ")
                    patient_database[patient_id][1] = name

                elif response == "Gender":
                    gender = pyip.inputStr(prompt="Enter gender: ")
                    patient_database[patient_id][2] = gender

                elif response == "Birth_Date":
                    birth_date = pyip.inputDate(prompt="Enter birth date (YYYY-MM-DD): ", formats=[DATE_FORMAT])
                    patient_database[patient_id][3] = birth_date

                else:
                    break

def modify_room(room_database, bed_database):
    while True:
        prompt = "\nPlease select one of the following:\n"
        choices = ["Update room status",
                   "Change room type",
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == choices[0]:
            prompt = f"Enter index to mark as completed (-1 to cancel): "
            index = pyip.inputInt(prompt=prompt, min=-1, max=len(room_database)-2)
            if index == -1:
                break
            else:
                room_database[index]["Discharge_Date"] = get_current_date_str()
                room_database[index]["Status"] = "COMPLETED"
            
        elif response == choices[1]:
            prompt = f"Enter index to change room type: "
            index = pyip.inputInt(prompt=prompt, min=0, max=len(room_database)-2)
            if index == -1:
                break
            else:
                while True:
                    prompt = "\nEnter new room type:\n"
                    choices = ["VVIP", "VIP", "Kelas_1", "Kelas_2", "Kelas_3", "Return to previous menu"]
                    room_type = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                    if room_type == choices[-1]:
                        break
                    else:
                        room_database[index]["Room_Type"] = room_type
                        break
        
        else:
            break

def delete_patient(patient_database, room_database, bed_database):
    while True:
        display_dict_of_list(database=patient_database)
        display_list_of_dict(database=room_database)
        display_list_of_dict(database=bed_database)

        primary_key = "Patient_ID"
        patient_id = pyip.inputStr(prompt=f"Enter {primary_key} data to delete (-1 to cancel): ")
        
        if patient_id == -1:
            break
        else:
            if patient_id in patient_database.keys():
                confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
                if confirmation == "yes":
                    patient_database.update({patient_id: [patient_id, "NULL", "NULL", "NULL", "NULL"]})
                else:
                    break
            else:
                print(f"{primary_key} {patient_id} does not exist.")
                continue
            
            for row in room_database:
                if row[primary_key] == patient_id and row["Status"] == "ONGOING":
                    row["Discharge_Date"] = get_current_date_str()
                    row["Status"] = "NULL"

                    room_type = row["Room_Type"]
                    new_data = bed_database[-1].copy()
                    new_data["Index"] += 1
                    new_data["Timestamp"] = get_current_datetime_str()
                    new_data[room_type] += 1
                    bed_database.append(new_data)
        
            display_dict_of_list(database=patient_database)
            display_list_of_dict(database=room_database)
            display_list_of_dict(database=bed_database)
            break

def delete_room(room_database, bed_database):
    while True:
        display_list_of_dict(database=room_database)
        display_list_of_dict(database=bed_database)

        primary_key = "Index"
        prompt = f"Enter {primary_key} data to delete (-1 to cancel): "
        index = pyip.inputInt(prompt=prompt, min=-1, max=len(room_database)-2)

        if index == -1:
            break
        else:
            index += 1
            status = room_database[index]["Status"]
            room_type = room_database[index]["Room_Type"]

            confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
            if confirmation == "yes":
                del room_database[index]
            else:
                continue

            # only update bed database if status is ONGOING
            if status == "ONGOING":
                new_data = bed_database[-1].copy()
                new_data["Index"] += 1
                new_data["Timestamp"] = get_current_datetime_str()
                new_data[room_type] += 1
                bed_database.append(new_data)       
            
            display_list_of_dict(database=room_database)
            display_list_of_dict(database=bed_database)
            break

def delete_bed(bed_database):
    while True:
        display_list_of_dict(database=bed_database)
        primary_key = "Index"
        prompt = f"Enter {primary_key} data to delete (-1 to cancel): "
        index = pyip.inputInt(prompt=prompt, min=-1, max=len(bed_database)-2)  
        
        if index == -1:
            break
        else:
            if index == bed_database[-1][primary_key]:
                print("Cannot delete most recent timestamp.")
            else:
                index += 1
                confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
                if confirmation == "yes":
                    del bed_database[index]
                else:
                    break
                
                display_list_of_dict(database=bed_database)
                break

def save_file(database, FILE_PATH):
    response = pyip.inputYesNo(prompt="Save changes (yes/no): ")
    if response == "yes":
        file = open(FILE_PATH, "w", newline='')
        writer = csv.writer(file, delimiter=";")
        writer.writerows(database.values())
        file.close()