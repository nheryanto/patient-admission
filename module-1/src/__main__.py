import sys
import os
import csv
import pyinputplus as pyip

from patientdata import display_patient, display_room, display_bed
from patientdata import add_new_patient, add_new_visit
from patientdata import modify_patient, modify_room
from patientdata import delete_patient, delete_room, delete_bed
from patientdata import isEmptyDatabase, isAvailableRoom

from patientdata import get_most_recent_bed_data, display_selected_data
from patientdata import input_room_type


def clear_screen():
    """
    Function to clear user's screen
    """
    if os.name == 'nt':
        _ = os.system('cls') # Windows
    else:
        _ = os.system('clear') # macOS and Linux

def load_patient(FILE_PATH):
    """
    Function to load patient data
    
    Args:
        FILE_PATH (str): path to CSV file containing patient data
    
    Returns:
        dict: patient data
    """
    file = open(FILE_PATH, "r")
    reader = csv.reader(file, delimiter=";")
    headings = next(reader)
    database = {"column": headings}
    for row in reader:
        patient_id, first_name, last_name, gender, birth_date = row
        database.update(
            {
                str(patient_id): [
                    str(patient_id), 
                    str(first_name),
                    str(last_name),
                    str(gender),
                    str(birth_date)
                ]
            }
        )
    file.close()
    return database

def load_room(FILE_PATH):
    """
    Function to load room admission data
    
    Args:
        FILE_PATH (str): path to CSV file containing room admission data
    
    Returns:
        list: room admission data
    """
    file = open(FILE_PATH, "r")
    reader = csv.reader(file, delimiter=";")
    headings = next(reader)
    database = []
    database.append(headings)

    for row in reader:
        dict_row = {}
        index, patient_id, room_type, admission_date, discharge_date, status = row
        dict_row.update(
            {
                headings[0]: int(index),
                headings[1]: str(patient_id),
                headings[2]: str(room_type),
                headings[3]: str(admission_date),
                headings[4]: str(discharge_date),
                headings[5]: str(status)
            }
        )
        database.append(dict_row)
    file.close()

    return database

def load_bed(FILE_PATH):
    """
    Function to load bed availability data
    
    Args:
        FILE_PATH (str): path to CSV file containing bed availability data
    
    Returns:
        list: bed availability data
    """
    file = open(FILE_PATH, "r")
    reader = csv.reader(file, delimiter=";")
    headings = next(reader)
    database = []
    database.append(headings)

    for row in reader:
        dict_row = {}
        index, timestamp, vvip, vip, kelas_1, kelas_2, kelas_3 = row
        dict_row.update(
            {
                headings[0]: int(index),
                headings[1]: str(timestamp),
                headings[2]: int(vvip),
                headings[3]: int(vip),
                headings[4]: int(kelas_1),
                headings[5]: int(kelas_2),
                headings[6]: int(kelas_3)
            }
        )
        database.append(dict_row)
    file.close()
    return database

def dict_of_list_to_csv(FILE_PATH, database):
    file = open(FILE_PATH, "w", newline='')
    writer = csv.writer(file, delimiter=";")
    writer.writerows(database.values())
    file.close()

def list_of_dict_to_csv(FILE_PATH, database):
    file = open(FILE_PATH, "w", newline='')
    writer = csv.writer(file, delimiter=";")
    database = [database[0]] + [row.values() for row in database[1:]]
    writer.writerows(database)
    file.close()

### INCOMPLETE: TOTAL PATIENT DATABASE ###
def main():
    """
    Main program to run the entire process
    """
    global patient_db
    global room_db
    global bed_db

    while True:
        prompt = "\n=== Main Menu ===\nPlease select one of the following:\n"
        choices = ["Display data",
                   "Add new admission",
                   "Modify data",
                   "Delete data",
                   "Exit"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
        if response == choices[0]:
            while True:
                prompt = "\nPlease select one of the following:\n"
                choices = ["Display patient data",
                        "Display room data",
                        "Display bed data",
                        "Return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
                
                if response == choices[0]:
                    if isEmptyDatabase(patient_db):
                        print("Patient database empty. Please add new patient first.")
                    else:
                        display_patient(database=patient_db)          

                elif response == choices[1]:
                    if isEmptyDatabase(room_db):
                        print("Room database empty. Please add new patient or new visit first.")
                    else:
                        display_room(database=room_db)

                elif response == choices[2]:
                    display_bed(database=bed_db)

                else:
                    break
        
        elif response == choices[1]:
            while True:
                most_recent_data, bed_header = get_most_recent_bed_data(bed_db)
                display_selected_data(most_recent_data[1:], bed_header[1:], title="=== Bed Availability ===")

                room_type, isBreak = input_room_type()

                if isBreak:
                    break
            
                if isAvailableRoom(most_recent_data, bed_header, room_type):
                    while True:
                        prompt = "\nPlease select one of the following:\n"
                        choices = ["Add new patient",
                                   "Add new visit",
                                   "Return to previous menu"]
                        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
                        if response == choices[0]:
                            add_new_patient(patient_database=patient_db, room_database=room_db,
                                            bed_database=bed_db, room_type=room_type)
                            
                        elif response == choices[1]:
                            if isEmptyDatabase(patient_db):
                                print("Patient database empty. Please add new patient first.")
                            else:
                                add_new_visit(patient_database=patient_db, room_database=room_db,
                                              bed_database=bed_db, room_type=room_type)
                        
                        else:
                            break
                
                else:
                    prompt = "\nRoom is not available. Reenter desired room type? (yes/no): "
                    response = pyip.inputYesNo(prompt=prompt)
                    if response == "yes": continue
                    else: break

        elif response == choices[2]:
            while True:
                prompt = "\nPlease select one of the following:\n"
                choices = ["Modify patient data",
                           "Modify room data",
                           "Return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                if response == choices[0]:
                    if isEmptyDatabase(patient_db):
                        print("Patient database empty. Please add new patient first.")
                    else:
                        modify_patient(patient_database=patient_db)

                elif response == choices[1]:
                    if isEmptyDatabase(room_db):
                        print("Room database empty. Please add new patient or new visit first.")
                    else:
                        modify_room(room_database=room_db,
                                    bed_database=bed_db)
                
                else:
                    break

        elif response == choices[3]:
            while True:
                prompt = "\nPlease select one of the following:\n"
                choices = ["Delete patient data",
                           "Delete room data",
                           "Delete bed data",
                           "Return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                if response == choices[0]:
                    if isEmptyDatabase(patient_db):
                        print("Patient database empty. Please add new patient first.")
                    else:
                        delete_patient(patient_database=patient_db, room_database=room_db,
                                    bed_database=bed_db)
                    
                elif response == choices[1]:
                    if isEmptyDatabase(room_db):
                        print("Room database empty. Please add new patient or new visit first.")
                    else:
                        delete_room(room_database=room_db,
                                    bed_database=bed_db)
                    
                elif response == choices[2]:
                    delete_bed(bed_database=bed_db)

                else:
                    break
        
        else:
            break
    
### SIMPLIFY ###
if __name__ == "__main__":
    clear_screen()

    # get current working directory
    CURRENT_DIR = os.getcwd()

    # get path to CSV files of patient, room admission, and bed availability data
    PATIENT_DB_PATH = os.path.join(CURRENT_DIR, "patient_data.csv")
    ROOM_DB_PATH = os.path.join(CURRENT_DIR, "room_data.csv")
    BED_DB_PATH = os.path.join(CURRENT_DIR, "bed_data.csv")

    patient_file_size = os.path.getsize(PATIENT_DB_PATH)
    room_file_size = os.path.getsize(ROOM_DB_PATH)
    bed_file_size = os.path.getsize(BED_DB_PATH)
    
    ### SIMPLIFY ###
    if patient_file_size > 0 and room_file_size > 0 and bed_file_size > 0:
        # load data
        bed_db = load_bed(BED_DB_PATH)
        if not isEmptyDatabase(bed_db):
            patient_db = load_patient(PATIENT_DB_PATH)
            room_db = load_room(ROOM_DB_PATH)
            
            print('\n=== Welcome to JCDS Purwadhika Patient Admission Data System ===')
            # run main program
            main()
            # keep database updated
            dict_of_list_to_csv(PATIENT_DB_PATH, patient_db)
            list_of_dict_to_csv(ROOM_DB_PATH, room_db)
            list_of_dict_to_csv(BED_DB_PATH, bed_db)
        else:
            print("Bed database empty. Please enter bed availability first.")
    else:
        if patient_file_size == 0:
            print("Patient database empty.")
        if room_file_size == 0:
            print("Room database empty.")
        if bed_file_size == 0:
            print("Bed database empty.")
        print("Please enter initial data first.")
    
    # end program
    sys.exit()