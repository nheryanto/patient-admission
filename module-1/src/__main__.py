import sys
import os
import csv
import datetime
from dateutil import parser
import pyinputplus as pyip

from patientdata import display_patient, display_room, display_bed
from patientdata import isRoomAvailable, add_new_patient, add_new_visit
from patientdata import delete_patient, delete_room, delete_bed

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
    database = {"column": headings}
    for row in reader:
        index, patient_id, room_type, adm_date, dis_date, status = row
        database.update(
            {
                index: [
                    int(index), 
                    patient_id,
                    room_type,
                    adm_date,
                    dis_date,
                    status
                ]
            }
        )
    file.close()
    return database

def load_bed(FILE_PATH):
    file = open(FILE_PATH, "r")
    reader = csv.reader(file, delimiter=";")
    headings = next(reader)
    database = {"column": headings}
    for row in reader:
        index, timestamp, vvip, vip, kelas_1, kelas_2, kelas_3 = row
        #timestamp = parser.isoparse(timestamp)
        database.update(
            {
                index: [
                    int(index), 
                    timestamp,
                    int(vvip),
                    int(vip),
                    int(kelas_1),
                    int(kelas_2),
                    int(kelas_3)
                ]
            }
        )
    file.close()
    return database

def main():
    global patient_db
    global room_db
    global bed_db

    while True:
        prompt = "\nplease select one of the following:\n"
        choices = ["display patient data",
                   "display room data",
                   "display bed data",
                   "add new visit",
                   "delete patient data",
                   "delete room data",
                   "delete bed data",
                   "exit"]
        response = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)
        
        if response == "display patient data":
            display_patient(database=patient_db)

        elif response == "display room data":
            display_room(database=room_db)
        
        elif response == "display bed data":
            display_bed(database=bed_db)
        
        elif response == "add new visit":
            prompt = "\nenter desired room type:\n"
            choices = ["vvip", "vip", "kelas_1", "kelas_2", "kelas_3"]
            room_type = pyip.inputMenu(prompt=prompt, choices=choices, numbered=True)

            if isRoomAvailable(room_type):
                new_patient = pyip.inputYesNo(prompt="\nare you a new patient? (yes/no): ")
                if new_patient == "yes":
                    add_new_patient(patient_database=patient_db, room_database=room_db,
                                    bed_database=bed_db)
                else:
                    add_new_visit(patient_database=patient_db, room_database=room_db,
                                  bed_database=bed_db)
        
        elif response == "delete patient data":
            delete_patient(patient_database=patient_db, room_database=room_db,
                           bed_database=bed_db)
        
        elif response == "delete room data":
            delete_room(room_database=room_db,
                        bed_database=bed_db)
        
        elif response == "delete bed data":
            delete_bed(bed_database=bed_db)
        
        else:
            break
    
if __name__ == "__main__":
    clear_screen()

    DATE_FORMAT = "%Y-%m-%d"

    CURRENT_DIR = os.getcwd()
    PATIENT_DB_PATH = os.path.join(CURRENT_DIR, "patient_data.csv")
    ROOM_DB_PATH = os.path.join(CURRENT_DIR, "room_data.csv")
    BED_DB_PATH = os.path.join(CURRENT_DIR, "bed_data.csv")

    patient_db = load_patient(PATIENT_DB_PATH)
    room_db = load_room(ROOM_DB_PATH)
    bed_db = load_bed(BED_DB_PATH)

    main()
    
    sys.exit()