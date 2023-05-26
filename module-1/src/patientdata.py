import csv
from datetime import datetime, timezone
import pyinputplus as pyip
import tabulate

DATE_FORMAT = "%Y-%m-%d"

### general functions ###

def isEmptyDatabase(database):
    print(len(database))
    if len(database) < 2: return True
    else: return False

def get_current_datetime_str():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

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
    data = [list(row.values()) for row in database[1:]]
    header = database[0]
    return data, header

def display_list_of_dict(database):
    data, header = get_list_of_dict_data_header(database)
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def display_data_header(data, header):
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

### FEATURE FUNCTIONS ###

def display_patient(database):
    data, header = get_dict_of_list_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                   "patient_id",
                   "name",
                   "gender",
                   "birth_date",
                   "return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display_data_header(data=data, header=header)
        else:
            prompt = f"enter {response}: "
            if response == "patient_id":
                search_val = pyip.inputStr(prompt=prompt)
            elif response == "name":
                search_val = pyip.inputStr(prompt=prompt)
            elif response == "gender":
                search_val = pyip.inputMenu(prompt=prompt, choices=["Male", "Female"], numbered=True)
            elif response == "birth_date":
                search_val = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT])
            else:
                break
            filtered_data = custom_filter(data=data, header=header, key=response, val=search_val)
            if filtered_data:
                display_data_header(data=filtered_data, header=header)
            else:
                print("Data does not exist.")

def display_room(database):
    data, header = get_list_of_dict_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                   "patient_id",
                   "room_type",
                   "admission_date",
                   "discharge_date",
                   "status",
                   "return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display_data_header(data=data, header=header)
        else:
            prompt = f"enter {response}: "
            if response == "patient_id":
                search_val = pyip.inputStr(prompt=prompt)
            elif response == "room_type":
                search_val = pyip.inputStr(prompt=prompt)
            elif response == "admission_date":
                search_val = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT])
            elif response == "discharge_date":
                search_val = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT])
            elif response == "status":
                search_val = pyip.inputMenu(prompt=(prompt+"\n"), choices=["COMPLETED", "ONGOING"], numbered=True)
            else:
                break
            filtered_data = custom_filter(data=data, header=header, key=response, val=search_val)
            display_data_header(data=filtered_data, header=header)

def display_bed(database):
    data, header = get_list_of_dict_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                    "most_recent",
                    "return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display_data_header(data=data, header=header)
        else:
            break

def add_new_patient(patient_database, room_database, bed_database, room_type):
    ### INPUT ###
    name = pyip.inputStr()
    gender = pyip.inputStr()
    birth_data = pyip.inputDate()

    patient_id = f"P-{int(list(patient_database.keys())[-1][-1]) + 1}"
    patient_database.update({patient_id: [patient_id, name, gender, birth_data]})

    index_room = len(room_database)-1
    admission_date = datetime.datetime.today().strftime(DATE_FORMAT)
    discharge_date = "N/A"
    status = "ONGOING"
    room_database.update({str(index_room): [index_room,
                                            patient_id,
                                            room_type,
                                            admission_date,
                                            discharge_date,
                                            status]})
    
    index_bed = len(bed_database)-1
    last_data = sorted(list(bed_database.values()), key=lambda x: x[1])[-1]
    bed_database.update({str(index_bed): [index_bed,
                                          get_current_datetime_str(),
                                          last_data[2]-1,
                                          last_data[3],
                                          last_data[4],
                                          last_data[5]]})
    
def add_new_visit(patient_database, room_database, bed_database, room_type):
    key = "patient_id"
    prompt = f"enter {key}: "
    print()
    patient_id = pyip.inputStr(prompt=prompt)
    
    ### CHECK patient_id IN DATABASE ###

    index_room = len(room_database)-1
    admission_date = datetime.datetime.today().strftime(DATE_FORMAT)
    discharge_date = "N/A"
    status = "ONGOING"
    room_database.update({str(index_room): [index_room,
                                            patient_id,
                                            room_type,
                                            admission_date,
                                            discharge_date,
                                            status]})
    
    index_bed = len(bed_database)-1
    last_data = sorted(list(bed_database.values()), key=lambda x: x[1])[-1]
    bed_database.update({str(index_bed): [index_bed,
                                          get_current_datetime_str(),
                                          last_data[2]-1,
                                          last_data[3],
                                          last_data[4],
                                          last_data[5]]})

def isAvailableRoom(bed_database, room_type):
    # get bed data with most recent timestamp
    data, header = get_list_of_dict_data_header(bed_database)
    most_recent_data = sorted(data, key=lambda x: x[1])[-1]

    # return True if bed_count of room_type > 0
    index = header.index(room_type)
    bed_count =  most_recent_data[index]
    if bed_count > 0: return True
    else: return False
    
def modify_patient(patient_database):
    while True:
        prompt = f"enter patient_id to modify data or CANCEL to cancel: "
        patient_id = pyip.inputStr()
        if patient_id.upper() == "CANCEL":
            break
        else:
            while True:
                prompt = "\nmodify:\n"
                choices = ["name",
                        "gender",
                        "birth_date"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

def modify_room(room_database, bed_database):
    while True:
        prompt = "\nplease select one of the following:\n"
        choices = ["update room status",
                   "change room type",
                   "return to previous menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

        if response == "update room status":
            prompt = f"enter index to mark as completed: "
            index = pyip.inputInt(prompt=prompt, min=0, max=len(room_database)-2)
            
        elif choices == "change room type":
            prompt = f"enter index to change room type: "
            index = pyip.inputInt(prompt=prompt, min=0, max=len(room_database)-2)

            while True:
                prompt = "\nenter new room type:\n"
                choices = ["vvip", "vip", "kelas_1", "kelas_2", "kelas_3", "return to main menu"]
                room_type = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
        else:
            break

def delete_patient(patient_database, room_database, bed_database):
    while True:
        display_dict_of_list(database=patient_database)
        display_list_of_dict(database=room_database)
        display_list_of_dict(database=bed_database)

        primary_key = "patient_id"
        patient_id = pyip.inputStr(prompt=f"enter {primary_key} data to delete (CANCEL to cancel): ")

        if patient_id.upper() == "CANCEL":
            break
        else:
            if patient_id in patient_database.keys():
                confirmation = pyip.inputYesNo(prompt="\nconfirm deletion? (yes/no): ")
                if confirmation == "yes":
                    patient_database.update({patient_id: [patient_id, "NULL", "NULL", "NULL"]})
                else:
                    break
            else:
                print(f"{primary_key} {patient_id} does not exist.")
                continue

            # get index (primary key) in room_database using patient_id (foreign key)
            primary_key, foreign_key = "index", "patient_id"
            room_index = [val[primary_key] for val in room_database[1:] if patient_id == val[foreign_key]]

            # delete if index (primary key) exists
            if room_index:
                for i in range(len(room_index)):
                    index = room_index[i] + 1

                    # get status and room type (foreign keys) in room_database
                    status = room_database[index]["status"]
                    room_type = room_database[index]["room_type"]

                    del room_database[index]
                    # room_database[index].update({
                    #     "room_type": "NULL",
                    #     "admission_date": "NULL",
                    #     "discharge_date": "NULL",
                    #     "status": "NULL"
                    # })

                    room_index[i+1:] = [item-1 for item in room_index[i+1:]]
                    #room_index[i%len(room_index)+1:] = [item-1 for item in room_index[i%len(room_index)+1:]]
                    print(room_index)
                    display_list_of_dict(room_database)
                    display_list_of_dict(bed_database)

                    # only update bed database if status is ONGOING
                    if status == "ONGOING":
                        new_data = bed_database[-1].copy()
                        new_data["index"] += 1
                        new_data["timestamp"] = get_current_datetime_str()
                        new_data[room_type] += 1
                        bed_database.append(new_data)       

                for i in range(1,len(room_database)):
                    room_database[i][primary_key] = i - 1
        
            display_dict_of_list(database=patient_database)
            display_list_of_dict(database=room_database)
            display_list_of_dict(database=bed_database)
            break

def delete_room(room_database, bed_database):
    while True:
        display_list_of_dict(database=room_database)
        display_list_of_dict(database=bed_database)

        primary_key = "index"
        prompt = f"enter {primary_key} data to delete (-1 to cancel): "
        index = pyip.inputInt(prompt=prompt, min=-1, max=len(room_database)-2)

        if index == -1:
            break
        else:
            index += 1
            status = room_database[index]["status"]
            room_type = room_database[index]["room_type"]

            confirmation = pyip.inputYesNo(prompt="\nconfirm deletion? (yes/no): ")
            if confirmation == "yes":
                del room_database[index]
                # room_database[index].update({
                #     "room_type": "NULL",
                #     "admission_date": "NULL",
                #     "discharge_date": "NULL",
                #     "status": "NULL"
                # })
            else:
                continue
            
            for i in range(index, len(room_database)):
                room_database[i][primary_key] = i - 1

            # only update bed database if status is ONGOING
            if status == "ONGOING":
                new_data = bed_database[-1].copy()
                new_data["index"] += 1
                new_data["timestamp"] = get_current_datetime_str()
                new_data[room_type] += 1
                bed_database.append(new_data)       
            
            display_list_of_dict(database=room_database)
            display_list_of_dict(database=bed_database)

def delete_bed(bed_database):
    while True:
        display_list_of_dict(database=bed_database)
        primary_key = "index"
        prompt = f"enter {primary_key} data to delete (-1 to cancel): "
        index = pyip.inputInt(prompt=prompt, min=-1, max=len(bed_database)-2)  
        
        if index == -1:
            break
        else:
            if index == bed_database[-1][primary_key]:
                print("Cannot delete most recent timestamp.")
            else:
                index += 1
                confirmation = pyip.inputYesNo(prompt="\nconfirm deletion? (yes/no): ")
                if confirmation == "yes":
                    del bed_database[index]
                else:
                    break
                
                for i in range(index, len(bed_database)):
                    bed_database[i][primary_key] = i - 1
                display_list_of_dict(database=bed_database)

def save_file(database, FILE_PATH):
    response = pyip.inputYesNo(prompt="Save changes (yes/no): ")
    if response == "yes":
        file = open(FILE_PATH, "w", newline='')
        writer = csv.writer(file, delimiter=";")
        writer.writerows(database.values())
        file.close()