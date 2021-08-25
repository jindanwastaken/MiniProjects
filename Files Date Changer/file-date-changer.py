# core modules
from genericpath import isdir
import os
import time
import datetime

# global variables
ALL_FILES = []
ERROR_FILES = []
TOTAL_FILES = 0
INIT_FOLDER = 'pending_blobs'

# print errors
def print_errors():
    for file in ERROR_FILES:
        print(file)

# returns a number corresponding to that month
def get_month_number(month):
    if(month == 'Jan'):
        return 1
    elif(month == 'Feb'):
        return 2
    elif(month == 'Mar'):
        return 3
    elif(month == 'Apr'):
        return 4
    elif(month == 'May'):
        return 5
    elif(month == 'Jun'):
        return 6
    elif(month == 'Jul'):
        return 7
    elif(month == 'Aug'):
        return 8
    elif(month == 'Sep'):
        return 9
    elif(month == 'Oct'):
        return 10
    elif(month == 'Nov'):
        return 11
    elif(month == 'Dec'):
        return 12
    else:
        return month

# change modification time of the file passed in path
def change_mod_time(path):

    file_name_array = os.path.basename(path).split('.')[0].split(' ')
    
    year = 0
    month = 0
    day = 0
    hour = 0
    minute = 0
    second = 0

    if(file_name_array[0].isdigit()):
        day = int(file_name_array[0])
        month = get_month_number(file_name_array[1])

    else:
        day = int(file_name_array[1].split(',')[0])
        month = get_month_number(file_name_array[0])
    
    year = int(file_name_array[2])

    time_array = file_name_array[3].split('-')

    hour = int(time_array[0])
    minute = int(time_array[1])
    second = int(time_array[2])
    
    extracted_date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
    time_tuple = time.mktime(extracted_date.timetuple())

    os.utime(path, (time_tuple, time_tuple))

# process each file in ALL_FILES array
def process_files():
    global TOTAL_FILES
    global ALL_FILES
    global ERROR_FILES

    processed_count = 0
    error_count = 0

    for file_path in ALL_FILES:
        try:
            change_mod_time(file_path)
            processed_count += 1
            print(f'{processed_count}/{TOTAL_FILES} : {file_path}')
        except:
            print(f'error with {file_path}')
            error_count += 1
            ERROR_FILES.append(file_path)

    return processed_count, error_count

# process an individual folder
def process_folder(path):
    print(f'processing path : {path}')
    
    global ALL_FILES
    global TOTAL_FILES

    dir_list = os.listdir(path)

    for entry in dir_list:
        if(os.path.isdir(os.path.join(path, entry))):
            process_folder(os.path.join(path, entry))
        else:
            print(f'adding file : {os.path.join(path, entry)}')
            ALL_FILES.append(os.path.join(path, entry))
            TOTAL_FILES += 1

# main method
def main():

    global TOTAL_FILES
    global ALL_FILES
    global INIT_FOLDER

    # adding all files to global array
    process_folder(f'./{INIT_FOLDER}')
    print(f'added {TOTAL_FILES} files in total')
    print()

    # changing dates of files
    processed_count, error_count = process_files()
    print(f'processed {processed_count} out of {TOTAL_FILES}')
    print(f'errors : {error_count} / {TOTAL_FILES}')
    print()

    # print errors
    print_errors()


if __name__ == '__main__':
    main()