import sys
import os
import csv
import datetime
from dateutil import parser
import pyinputplus as pyip

from patientdata import display_patient, display_room, display_bed
from patientdata import add_new_patient, add_new_visit
from patientdata import modify_patient, modify_room
from patientdata import delete_patient, delete_room, delete_bed
from patientdata import isEmptyDatabase, isAvailableRoom

def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls') # Windows
    else:
        _ = os.system('clear') # macOS and Linux

def load_patient(FILE_PATH):
    file = open(FILE_PATH, "r")
    reader = csv.reader(file, delimiter=";")
    headings = next(reader)
    database = {"column": headings}
    for row in reader:
        patient_id, name, gender, birth_date = row
        database.update(
            {
                patient_id: [
                    patient_id, 
                    name,
                    gender,
                    birth_date
                ]
            }
        )
    file.close()
    return database

def load_room(FILE_PATH):
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

def main():
    global patient_db
    global room_db
    global bed_db

    while True:
        prompt = "\nplease select one of the following:\n"
        choices = ["display data",
                   "add new admission",
                   "modify data",
                   "delete data",
                   "exit"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
        if response == "display data":
            while True:
                prompt = "\nplease select one of the following:\n"
                choices = ["display patient data",
                           "display room data",
                           "display bed data",
                           "return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
                
                if response == "display patient data":
                    display_patient(database=patient_db)                    
                elif response == "display room data":
                    display_room(database=room_db)
                elif response == "display bed data":
                    display_bed(database=bed_db)
                else:
                    break
        
        elif response == "add new admission":
            while True:
                prompt = "\nenter desired room type:\n"
                choices = ["vvip", "vip", "kelas_1", "kelas_2", "kelas_3", "return to main menu"]
                room_type = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                if room_type == choices[-1]:
                    break
                else:
                    if isAvailableRoom(bed_db, room_type):
                        while True:
                            prompt = "\nplease select one of the following:\n"
                            choices = ["add new patient",
                                       "add new visit",
                                       "return to previous menu"]
                            response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
            
                            if response == "add new patient":
                                add_new_patient(patient_database=patient_db, room_database=room_db,
                                                bed_database=bed_db, room_type=room_type)
                            elif response == "add new visit":
                                add_new_visit(patient_database=patient_db, room_database=room_db,
                                            bed_database=bed_db)
                            else:
                                break
                    else:
                        ### show most recent bed counts ###
                        prompt = "\nroom is not available. reenter desired room type? (yes/no): "
                        response = pyip.inputYesNo(prompt=prompt)
                        if response == "yes": continue
                        else: break

        elif response == "modify data":
            while True:
                prompt = "\nplease select one of the following:\n"
                choices = ["modify patient data",
                           "modify room data",
                           "return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                ### check empty database ###
                if response == "modify patient data":
                    modify_patient(patient_database=patient_db)
                elif response == "modify room data":
                    modify_room(room_database=room_db,
                                bed_database=bed_db)
                else:
                    break

        elif response == "delete data":
            while True:
                prompt = "\nplease select one of the following:\n"
                choices = ["delete patient data",
                           "delete room data",
                           "delete bed data",
                           "return to main menu"]
                response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

                ### check empty database ###
                ### case study: if all patient & room data deleted ###
                if response == "delete patient data":
                    delete_patient(patient_database=patient_db, room_database=room_db,
                                bed_database=bed_db)
                elif response == "delete room data":
                    delete_room(room_database=room_db,
                                bed_database=bed_db)
                elif response == "delete bed data":
                    delete_bed(bed_database=bed_db)
                else:
                    break
        
        else:
            break
    
if __name__ == "__main__":
    clear_screen()

    CURRENT_DIR = os.getcwd()
    PATIENT_DB_PATH = os.path.join(CURRENT_DIR, "patient_data.csv")
    ROOM_DB_PATH = os.path.join(CURRENT_DIR, "room_data.csv")
    BED_DB_PATH = os.path.join(CURRENT_DIR, "bed_data.csv")

    patient_db = load_patient(PATIENT_DB_PATH)
    room_db = load_room(ROOM_DB_PATH)
    bed_db = load_bed(BED_DB_PATH)

    main()
    
    sys.exit()