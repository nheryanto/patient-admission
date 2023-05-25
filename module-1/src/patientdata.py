import csv
from datetime import datetime, timezone
import pyinputplus as pyip
import tabulate

DATE_FORMAT = "%Y-%m-%d"

def display(database=None, data=None, header=None):
    if database:
        data, header = get_data_header(database)
    print()
    print(tabulate.tabulate(data, header, tablefmt="outline"))

def get_current_datetime_str():
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()

def display_patient(database):
    data, header = get_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                   "patient_id",
                   "name",
                   "gender",
                   "birth_date",
                   "main menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display(data=data, header=header)
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
            display(data=filtered_data, header=header)

def display_room(database):
    data, header = get_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                    "patient_id",
                    "room_type",
                    "admission_date",
                    "discharge_date",
                    "status",
                    "main_menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display(data=data, header=header)
        else:
            prompt = f"enter {response}: "
            if response == "room_type":
                search_val = pyip.inputStr(prompt=prompt)
            elif response == "admission_date":
                search_val = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT])
            elif response == "discharge_date":
                search_val = pyip.inputDate(prompt=prompt, formats=[DATE_FORMAT])
            elif response == "status":
                search_val = pyip.inputMenu(prompt=prompt, choices=["COMPLETED", "ONGOING"], numbered=True)
            else:
                break
            filtered_data = custom_filter(data=data, header=header, key=response, val=search_val)
            display(data=filtered_data, header=header)

def display_bed(database):
    data, header = get_data_header(database)
    while True:
        prompt = "\ndisplay by:\n"
        choices = ["all_data",
                    "most_recent",
                    "main_menu"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        if response == "all_data":
            display(data=data, header=header)
        else:
            break

def custom_filter(data, header, key, val):
    # get index of key in header
    index = header.index(key)
    # filter data where row[index] = val for each row in data
    filtered_data = list(filter(lambda row: row[index] == val, data))
    return filtered_data

def get_data_header(database):
    # convert values of db into list without the header row
    data = list(database.values())[1:]
    # get header row from db
    header = database['column']
    return data, header

def add_new_patient(patient_database, room_database, bed_database):
    #patient_id
    name = pyip.inputStr()


def add_new_visit(patient_database, room_database, bed_database):
    key = "patient_id"
    prompt = f"enter {key}: "
    patient_id = pyip.inputStr(prompt=prompt)

    data, header = get_data_header(patient_database)
    index = header.index(key)

def isRoomAvailable(bed_database, room_type):
    # get bed data with most recent timestamp
    data, header = get_data_header(bed_database)
    most_recent_data = sorted(data, key=lambda x: x[1])[-1]

    # return True if bed_count of room_type > 0
    index = header.index(room_type)
    bed_count =  most_recent_data[index]
    if bed_count > 0:
        return True

def modify():
    print()

def delete_patient(patient_database, room_database, bed_database):
    display(database=patient_database)
    display(database=room_database)
    display(database=bed_database)

    primary_key = "patient_id"
    prompt = f"enter {primary_key} data to delete: "
    patient_id = pyip.inputStr(prompt=prompt)

    # delete data in patient_database
    for key, val in patient_database.copy().items():
        if key == "column":
            continue
        else:
            if patient_id in val:
                del patient_database[key]
    
    # get index (primary key) in room_database using patient_id
    check = [val[0] for val in room_database.values() if patient_id in val]
    if check:
        for i in range(len(check)):
            # get current index
            index = check[i]
            for key, val in room_database.copy().items():
                if key == "column":
                    continue
                if index == val[0]:
                    # decrement index by 1 on each deletion
                    check[i:] = [item-1 for item in check[i:]]
                    # get foreign keys for bed database
                    status = val[-1]
                    room_type = val[2]
                    # delete data in room_database
                    del room_database[key]
                # update index of remaining data
                elif index < val[0]:
                    # initialize new value with new index of previous index - 1
                    new_val = [val[0]-1]
                    # copy remaining values
                    new_val.extend(val[1:])
                    # update room database
                    room_database.update({
                        f"{key}": new_val
                    }) # old key does not change ?
                    # this raises unboundlocalerror
                    # index referenced before assignment
                    # why? because in room data, patient_id duplicates is allowed
                    # solution idea: get indexes where patient_id exists
                    # delete per index, while update index accordingly at each deletion

        # only update bed database if status is ONGOING
        if status == "ONGOING":
            data, header = get_data_header(bed_database)
            last_data = sorted(data, key=lambda x: x[1])[-1]

            # create new entry with new timestamp
            new_data = [len(bed_database)-1, get_current_datetime_str()]
            new_data.extend(last_data[2:]) # no need to use .copy()
            new_data[header.index(room_type)] += 1

            # update bed database
            bed_database.update({
                str(new_data[0]): new_data
            })
    
    display(database=patient_database)
    display(database=room_database)
    display(database=bed_database)

def delete_room(room_database, bed_database):
    display(database=room_database)
    display(database=bed_database)

    primary_key = "index"
    prompt = f"enter {primary_key} data to delete: "
    index = pyip.inputInt(prompt=prompt, min=0, max=len(room_database)-1)

    for key, val in room_database.copy().items():
        if key == "column":
            continue
        if index == val[0]:
            status = val[-1]
            room_type = val[2]
            del room_database[key]
        elif index < val[0]:
            new_val = [val[0]-1]
            new_val.extend(val[1:])
            room_database.update({
                f"{key}": new_val
            })
    
    if status == "ONGOING":
        data, header = get_data_header(bed_database)
        last_data = sorted(data, key=lambda x: x[1])[-1]

        new_data = [len(bed_database)-1, get_current_datetime_str()]
        new_data.extend(last_data[2:]) # no need to use .copy()
        new_data[header.index(room_type)] += 1

        bed_database.update({
            str(new_data[0]): new_data
        })
    
    display(database=room_database)
    display(database=bed_database)

def delete_bed(bed_database):
    display(database=bed_database)
    primary_key = "index"
    prompt = f"enter {primary_key} data to delete: "
    index = pyip.inputInt(prompt=prompt, min=0, max=len(bed_database)-1)  
    
    data, _ = get_data_header(bed_database)
    most_recent_index = sorted(data, key=lambda x: x[1])[-1][0]

    if index == most_recent_index:
        print("Cannot delete most recent timestamp.")
    else:
        for key, val in bed_database.copy().items():
            if key == "column":
                continue

            if index == val[0]:
                del bed_database[key]
            elif index < val[0]:
                new_val = [val[0]-1]
                new_val.extend(val[1:])
                bed_database.update({
                    f"{key}": new_val
                })
    display(database=bed_database)

def save_file(database, FILE_PATH):
    display(database=database)
    response = pyip.inputYesNo(prompt="Save changes (yes/no): ")
    if response == "yes":
        file = open(FILE_PATH, "w", newline='')
        writer = csv.writer(file, delimiter=";")
        writer.writerows(database.values())
        file.close()