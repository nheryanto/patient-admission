import csv
from datetime import datetime, timezone, timedelta
from dateutil import parser
import pyinputplus as pyip
import tabulate
import re

DATE_FORMAT = "%Y-%m-%d"
PATIENT_ID_FORMAT = r"^P-[0-9]+$"

### GENERAL FUNCTIONS ###

def isEmptyDatabase(database):
    if len(database) < 2: return True
    else: return False

def get_current_datetime_str():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

def get_current_date_str():
    return datetime.today().strftime(DATE_FORMAT)

def date_to_str(date):
    return date.strftime(DATE_FORMAT)

def filter_data_header(data, header, key, val):
    # get index of key in header
    index = header.index(key)
    
    # filter data where row[index] = val for each row in data
    filtered_data = list(filter(lambda row: row[index] == val, data))
    return filtered_data

def filter_range_date(data, header, key, start_date, end_date):
    index = header.index(key)
    filtered_data = list(filter(lambda row: row[index] >= start_date and row[index] <= end_date, data))
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
    # get ordered index
    data = [[i]+ list(row.values())[1:] for i, row in enumerate(database[1:])]
    header = database[0]
    return data, header

def display_list_of_dict(database):
    data, header = get_list_of_dict_data_header(database)
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def display_data_header(data, header):
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def display_ordered_data_header(data, header):
    ordered_data = [[i] + row[1:] for i, row in enumerate(data)]
    print()
    print(tabulate.tabulate(ordered_data, header, tablefmt="outline"))

def display_profile(patient_database, patient_id, title="=== Patient Profile ==="):
    '''
    Function to display a patient profile given an existing patient_id

    Args:
        patient_database (dict)
        patient_id (str)

    Returns:
        list
    '''
    print()
    print(title)
    headings = patient_database['column']
    for i, value in enumerate(patient_database[patient_id]):
        header = ' '.join(headings[i].split(sep='_'))
        print(f"{header:20} : {value}")

    return patient_database[patient_id]

def display_selected_data(data, header, title):
    '''
    Function to display

    Args:
        data (list)
        header (list)
        title (str)

    Returns:
        None
    '''
    if len(data) == len(header):
        print()
        print(title)
        for key, value in zip(header, data):
            try:
                key = ' '.join(key.split(sep='_'))
                value = ' '.join(value.split(sep='_'))
                print(f"{key:20} : {value}")
            except:
                print(f"{key:20} : {value}")

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

def isNullProfile(database, patient_id):
    '''
    Function to check if patient profile has been deleted given a patient ID

    Args:
        database (dict): patient data
        patient_id (str)

    Returns:
        bool
    '''
    if database[patient_id][1:] == ["NULL", "NULL", "NULL", "NULL"]:
        return True
    else:
        return False

def isOngoingPatient(database, patient_id):
    data, header = get_list_of_dict_data_header(database)
    filtered_id = filter_data_header(data, header, key="Patient_ID", val=patient_id)
    filtered_status = []
    if filtered_id:
        filtered_status = filter_data_header(filtered_id, header, key="Status", val="ONGOING")
    if filtered_status: return True
    else: return False

def get_most_recent_bed_data(database):
    # get bed data with most recent timestamp
    data, header = get_list_of_dict_data_header(database)
    return sorted(data, key=lambda x: x[1])[-1], header

def isAvailableRoom(data, header, room_type):
    # return True if bed_count of room_type > 0
    index = header.index(room_type)
    bed_count =  data[index]
    if bed_count > 0: return True
    else: return False

def update_patient_database(database, data):
    patient_id, first_name, last_name, gender, birth_date = data
    database.update({
        patient_id: [
            patient_id,
            first_name,
            last_name,
            gender,
            birth_date
        ]
    })
    return database

def update_room_database(database, data):
    headings = database[0]
    patient_id, room_type, admission_date, discharge_date, status = data
    new_data = {headings[0]: get_max_index(database)+1,
                headings[1]: patient_id,
                headings[2]: room_type,
                headings[3]: admission_date,
                headings[4]: discharge_date,
                headings[5]: status}
    database.append(new_data)
    return database

def update_bed_database(database, old_room_type, new_room_type):
    headings = database[0]
    new_data = database[-1].copy()
    new_data[headings[0]] = get_max_index(database)+1
    new_data[headings[1]] = get_current_datetime_str()
    if old_room_type:
        new_data[old_room_type] += 1
    if new_room_type:
        new_data[new_room_type] -= 1
    database.append(new_data)
    return database

def get_max_index(database):
    '''
    Function to find largest index of database which uses index as primary key

    Args:
        database (list)

    Returns
        int
    '''
    return max([row["Index"] for row in database[1:]])

def get_max_patient_id(database):
    '''
    Function to find largest patient ID number in database which uses patient ID as primary key

    Args:
        database (dict)

    Returns
        int
    '''
    # patient ID format e.g. P-1
    # get only number part in patient_ids
    patient_ids = [int(val[2:]) for val in list(database.keys())[1:]]
    return max(patient_ids)

def getValidName(name):
    '''
    Function to make sure name is capitalized and separated by single spaces
    
    Args:
        name (str)

    Returns:
        str
    '''
    if ' ' in name:
        tmp = [item.capitalize() for item in name.split()]
        name = ' '.join(tmp)
    else:
        name =  name.capitalize()
    return name

### INPUT FUNCTIONS ###

def input_patient_id():
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

def input_name(type):
    isBreak = False
    prompt = "\n" + f"Enter {type} name or 0 to cancel: "
    while True:
        name = pyip.inputStr(prompt=prompt)
        if name == "0":
            isBreak = True
        elif not isAlphaName(name) or "NULL" in name:
            print("Invalid input.")
            continue
        else:
            name = getValidName(name)
        break
    
    return name, isBreak

def input_gender():
    isBreak = False
    choices = ["Male", "Female", "Return to previous menu"]
    while True:
        gender = pyip.inputMenu(prompt="\nSelect gender:\n", choices=choices, numbered=True)
        if gender == choices[-1]:
            isBreak = True
        break
    return gender, isBreak

def input_date(type):
    isBreak = False
    prompt = "\n" + f"Enter {type} date (YYYY-MM-DD) or 0 to cancel: "
    date = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT], allowRegexes=[r"^0$"])
    if date == "0":
        isBreak = True
    else:
        date = date_to_str(date)
    return date, isBreak

def input_room_type():
    isBreak = False
    choices = ["VVIP", "VIP", "Kelas 1", "Kelas 2", "Kelas 3", "Return to previous menu"]
    room_type = pyip.inputMenu(prompt="\nSelect room type:\n", choices=choices, numbered=True)
    if room_type == choices[-1]:
        isBreak = True
    elif ' ' in room_type:
        room_type = '_'.join(room_type.split())
    return room_type, isBreak

def input_status():
    isBreak = False
    choices = ["Completed", "Ongoing", "Return to previous menu"]
    status = pyip.inputMenu(prompt="\nSelect status:\n", choices=choices, numbered=True)
    if status == choices[-1]:
        isBreak = True
    else:
        status = status.upper()
    return status, isBreak

def input_index_to_modify(len_database, type):
    isBreak = False
    prompt = "\n" + f"Enter index to {type} or -1 to cancel: "
    index = pyip.inputInt(prompt=prompt, min=-1, max=len_database-2)
    if index == -1:
        isBreak = True
    return index, isBreak

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
            isBreak = False
            while True:
                if response == choices[1]:
                    search_val, isBreak = input_patient_id()
                    search_key = "Patient_ID"

                elif response == choices[2]:
                    search_val, isBreak = input_name(type="first")
                    search_key = "First_Name"
                
                elif response == choices[3]:
                    search_val, isBreak = input_name(type="last")
                    search_key = "Last_Name"

                elif response == choices[4]:
                    search_val, isBreak = input_gender()
                    search_key = "Gender"

                else:
                    search_val, isBreak = input_date(type="birth")
                    search_key = "Birth_Date"

                if isBreak:
                    break

                filtered_data = filter_data_header(data=data, header=header, key=search_key, val=search_val)
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
            isBreak = False
            while True:
                if response == choices[1]:
                    search_val, isBreak = input_patient_id()
                    search_key = "Patient_ID"

                elif response == choices[2]:
                    search_val, isBreak = input_room_type()
                    search_key = "Room_Type"

                elif response == choices[3]:
                    search_val, isBreak = input_date(type="admission")
                    search_key = "Admission_Date"

                elif response == choices[4]:
                    search_val, isBreak = input_date(type="discharge")
                    search_key = "Discharge_Date"

                else:
                    search_val, isBreak = input_status()
                    search_key = "Status"
                
                if isBreak:
                    break

                filtered_data = filter_data_header(data=data, header=header, key=search_key, val=search_val)
                if filtered_data:
                    display_ordered_data_header(data=filtered_data, header=header)
                else:
                    print(f"{response} {search_val} does not exist in Room Admission data.")
                    continue
                break

def display_bed(database):
    data, header = get_list_of_dict_data_header(database)
    while True:
        prompt = "\nDisplay by:\n"
        choices = ["All data",
                   "Most recent",
                   "Range date",
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == choices[0]:
            display_data_header(data=data, header=header)
        elif response == choices[1]:
            most_recent_data, header = get_most_recent_bed_data(database)
            display_ordered_data_header(data=[most_recent_data], header=header)
        elif response == choices[2]:
            while True:
                start_date, isBreak = input_date(type="start")
                if isBreak:
                    break

                end_date, isBreak = input_date(type="end")
                if isBreak:
                    break

                start_date = parser.isoparse(start_date).astimezone().isoformat()
                end_date = parser.isoparse(end_date) + timedelta(days=1) - timedelta(seconds=1)
                end_date = end_date.astimezone().isoformat()

                if start_date > end_date:
                    print("\nStart date must be before end date.\n")
                    continue
                
                filtered_data = filter_range_date(data=data, header=header, key="Timestamp",
                                                  start_date=start_date, end_date=end_date)
                if filtered_data:
                    display_ordered_data_header(filtered_data, header)
                else:
                    print("\nData does not exist.\n")
                    continue
                break
        else:
            break

def add_new_patient(patient_database, room_database, bed_database, room_type):
    isBreak = False
    while True:
        first_name, isBreak = input_name(type="first")
        if isBreak:
            break

        last_name, isBreak = input_name(type="last")
        if isBreak:
            break

        gender, isBreak = input_gender()
        if isBreak:
            break

        birth_date, isBreak = input_date(type="birth")
        if isBreak:
            break
        
        profile = [first_name, last_name, gender, birth_date]
        key_match = isDuplicateProfile(patient_database, profile)
        if key_match:
            print(f"\nPatient profile already exists under Patient ID {key_match}.")
            display_profile(patient_database=patient_database, patient_id=key_match)

            confirmation = pyip.inputYesNo(prompt="Is it the same patient? (yes/no): ")
            if confirmation == "yes":
                print("Please add new visit instead.")
                break
            
        patient_id = f"P-{get_max_patient_id(patient_database) + 1}"
        patient_data = [patient_id] + profile

        admission_date = get_current_date_str()
        discharge_date = "N/A"
        status = "ONGOING"
        room_data = [patient_id, room_type, admission_date, discharge_date, status]

        tmp_data = patient_data + room_data[1:]
        tmp_header = patient_database['column'] + room_database[0][2:]
        display_selected_data(tmp_data, tmp_header, title="=== New Patient ===")

        confirmation = pyip.inputYesNo(prompt="\nConfirm changes? (yes/no): ")
        if confirmation == "yes":            
            patient_database = update_patient_database(patient_database, patient_data)            
            room_database = update_room_database(room_database, room_data)            
            bed_database = update_bed_database(database=bed_database,
                                               new_room_type= room_type,
                                               old_room_type=None)
            
            print("Data saved.")
        else:
            print("Data not saved.")

        break

def add_new_visit(patient_database, room_database, bed_database, room_type):
    isBreak = False
    while True:
        patient_id, isBreak = input_patient_id()
        if isBreak:
            break
        
        if patient_id not in patient_database or isNullProfile(patient_database, patient_id):
            print(f"Patient ID {patient_id} does not exist.")
            continue

        if isOngoingPatient(room_database, patient_id):
            print(f"Cannot add new visit for ONGOING patient.")
            continue
        
        patient_data = display_profile(patient_database, patient_id)
        confirmation = pyip.inputYesNo(prompt="Looking for different patient? (yes/no): ")
        if confirmation == "yes":
            continue

        admission_date = get_current_date_str()
        discharge_date = "N/A"
        status = "ONGOING"
        room_data = [patient_id, room_type, admission_date, discharge_date, status]

        tmp_data = patient_data + room_data[1:]
        tmp_header = patient_database['column'] + room_database[0][2:]
        display_selected_data(tmp_data, tmp_header, title="=== New Visit ===")
        
        confirmation = pyip.inputYesNo(prompt="\nConfirm changes? (yes/no): ")
        if confirmation == "yes":       
            room_database = update_room_database(room_database, room_data)            
            bed_database = update_bed_database(database=bed_database,
                                               new_room_type=room_type,
                                               old_room_type=None)
            print("Data saved.")
        else:
            print("Data not saved.")
        
        break    
    
def modify_patient(patient_database):
    isBreak = False
    while True:
        patient_id, isBreak = input_patient_id()
        if isBreak:
            break
        
        if patient_id not in patient_database or isNullProfile(patient_database, patient_id):
            print(f"Patient ID {patient_id} does not exist.")
            continue

        break
    
    if not isBreak:
        while True:
            patient_data = display_profile(patient_database, patient_id)
            prompt = "\nModify:\n"
            choices = ["First name",
                        "Last name",
                        "Gender",
                        "Birth date",
                        "Return to previous menu"]
            response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

            if response == choices[-1]:
                break

            else:
                breakFlag = False
                while True:
                    if response == choices[0]:
                        key = "First_Name"
                        new_value, breakFlag = input_name(type="first")

                    elif response == choices[1]:
                        key = "Last_Name"
                        new_value, breakFlag = input_name(type="last")

                    elif response == choices[2]:
                        key = "Gender"
                        new_value, breakFlag = input_gender()

                    else:
                        key = "Birth_Date"
                        new_value, breakFlag = input_date(type="birth")

                    if breakFlag:
                        break
                    
                    header = patient_database['column']
                    key_index = header.index(key)
                    tmp_data = patient_data.copy()
                    tmp_data[key_index] = new_value
                    display_selected_data(tmp_data, header, title="=== Modified Patient Profile ===")

                    confirmation = pyip.inputYesNo(prompt="\nConfirm changes? (yes/no): ")
                    if confirmation == "yes":
                        patient_database[patient_id][key_index] = new_value
                        print("Data saved.")
                    else:
                        print("Data not saved.")

                    break

def modify_room(room_database, bed_database):
    isBreak = False
    while True:
        prompt = "\nPlease select one of the following:\n"
        choices = ["Update room status",
                   "Change room type",
                   "Return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
        if response == choices[-1]:
            break
        else:
            display_list_of_dict(room_database)
            while True:
                if response == choices[0]:
                    index, isBreak = input_index_to_modify(len_database=len(room_database), type="mark as completed")
                    
                    if isBreak:
                        break
                    
                    current_status = room_database[index]["Status"]
                    index += 1
                    if current_status == "COMPLETED" or current_status == "NULL":
                        print("Cannot modify COMPLETED or NULL entries.")
                        continue
                    
                    current_date = get_current_date_str()
                    new_status = "COMPLETED"

                    tmp_data = room_database[index].copy()
                    tmp_data["Discharge_Date"] = current_date
                    tmp_data["Status"] = new_status           

                    tmp_data = list(tmp_data.values())[1:]
                    header = room_database[0][1:]
                    display_selected_data(tmp_data, header, title="=== Modified Room Admission Data ===")

                    confirmation = pyip.inputYesNo(prompt="\nConfirm changes? (yes/no): ")
                    if confirmation == "yes":
                        room_type = room_database[index]["Room_Type"]
                        room_database[index]["Discharge_Date"] = current_date
                        room_database[index]["Status"] = new_status
                        bed_database = update_bed_database(database=bed_database, old_room_type=room_type, new_room_type=None)
                        print("Data saved.")
                        display_list_of_dict(room_database)

                    else:
                        print("Data not saved.")

                    break
                
                else:
                    index, isBreak = input_index_to_modify(len_database=len(room_database), type="change room type")
                    
                    if isBreak:
                        break

                    current_status = room_database[index]["Status"]
                    index += 1
                    if current_status == "COMPLETED" or current_status == "NULL":
                        print("Cannot modify COMPLETED or NULL entries.")
                        continue
                    
                    breakFlag = False
                    while True:
                        new_room_type, breakFlag = input_room_type()

                        if breakFlag:
                            break
                        
                        tmp_data = room_database[index].copy()
                        tmp_data["Room_Type"] = new_room_type           

                        tmp_data = list(tmp_data.values())[1:]
                        header = room_database[0][1:]
                        display_selected_data(tmp_data, header, title="=== Modified Room Admission Data ===")

                        confirmation = pyip.inputYesNo(prompt="\nConfirm changes? (yes/no): ")
                        if confirmation == "yes":
                            old_room_type = room_database[index]["Room_Type"]
                            room_database[index]["Room_Type"] = new_room_type
                            update_bed_database(database=bed_database,
                                                old_room_type=old_room_type,
                                                new_room_type=new_room_type)
                            print("Data saved.")
                            display_list_of_dict(room_database)

                        else:
                            print("Data not saved.")
                        
                        break

def delete_patient(patient_database, room_database, bed_database):
    isBreak = False
    while True:
        display_dict_of_list(database=patient_database)
        patient_id, isBreak = input_patient_id()
        
        if isBreak:
            break
        
        if patient_id not in patient_database or isNullProfile(patient_database, patient_id):
            print(f"Patient ID {patient_id} does not exist.")
            continue
        
        display_profile(patient_database, patient_id)
        confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
        if confirmation == "yes":
            new_data = [patient_id, "NULL", "NULL", "NULL", "NULL"]
            patient_database = update_patient_database(patient_database, new_data)

            print("Data successfully deleted.")
            display_dict_of_list(database=patient_database)

            for row in room_database[1:]:
                if row["Patient_ID"] == patient_id and row["Status"] == "ONGOING":
                    row["Discharge_Date"] = get_current_date_str()
                    row["Status"] = "NULL"
                    room_type = row["Room_Type"]
                    ### LOOPHOLE: MULTIPLE ONGOING STATUS PER PATIENT WILL GENERATE NEW TIMESTAMP ON EACH DELETION ###
                    ### SAVED BY CONSTRAINT: ONE PATIENT CAN ONLY HAVE ONE ONGOING STATUS ###
                    ### UNLESS BULK DELETION (TO-DO?) ###
                    bed_database = update_bed_database(database=bed_database,
                                                       old_room_type=room_type,
                                                       new_room_type=None)

                    display_list_of_dict(database=room_database)
                    display_list_of_dict(database=bed_database)
        else:
            print("Deletion canceled.")
        break

def delete_room(room_database, bed_database):
    while True:
        display_list_of_dict(database=room_database)
        index, isBreak = input_index_to_modify(len_database=len(room_database), type="delete")
        if isBreak:
            break

        index += 1
        tmp_data = room_database[index].copy()
        tmp_data = list(tmp_data.values())[1:]
        header = room_database[0][1:]
        display_selected_data(tmp_data, header, title="=== Room Admission Data ===")

        confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
        if confirmation == "yes":
            status = room_database[index]["Status"]
            room_type = room_database[index]["Room_Type"]
            del room_database[index]

            print("Data successfully deleted.")
            display_list_of_dict(database=room_database)

            if status == "ONGOING":
                bed_database = update_bed_database(database=bed_database,
                                                   old_room_type=room_type,
                                                   new_room_type=None)
                display_list_of_dict(database=bed_database)
            
        else:
            print("Deletion canceled.")

        break

def delete_bed(bed_database):
    while True:
        display_list_of_dict(database=bed_database)
        index, isBreak = input_index_to_modify(len_database=len(bed_database), type="delete")
        if isBreak:
            break
        
        index += 1

        if index == len(bed_database)-1:
            print("Cannot delete most recent timestamp.")
            continue

        tmp_data = bed_database[index].copy()
        tmp_data = list(tmp_data.values())[1:]
        header = bed_database[0][1:]
        display_selected_data(tmp_data, header, title="=== Bed Availability Data ===")
        confirmation = pyip.inputYesNo(prompt="\nConfirm deletion? (yes/no): ")
        if confirmation == "yes":
            del bed_database[index]
            print("Data successfully deleted.")
        else:
            print("Deletion canceled.")

        break