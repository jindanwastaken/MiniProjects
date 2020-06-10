import os
import platform
import time
import argparse
import sys
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('-d', '-del', action="store_true", help="If specified will delete all residual folders")

requiredArgs = parser.add_mutually_exclusive_group(required=True)
requiredArgs.add_argument('-m', '-move', action="store_true", help="If specified, the files will be moved to the other location. Cannot be used with -c")
requiredArgs.add_argument('-c', '-copy', action="store_true", help="If specified, the files will be copied to the other location. Cannot be used with -m")

args = parser.parse_args()

# List storing the month names following 1 based indexing
months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

# Hold the output directory in a variable
root_dir = os.path.join(os.getcwd(), "Output")

# Check to see if output directory exists. If not create it.
if not (os.path.exists(root_dir)):
    os.mkdir(root_dir)

# Holding the count of number of files moved
count = 0

# List holding the files to be excluded
excluded_files = ["File_Organiser.py", "README.md", "Output"]

# Flag which checks if we are in the root directory
isRoot = True

# List of files to be deleted after the operation is done
to_be_deleted = []

# Function which returns the File Creation Year and Month in a List
# Different checks are given for Windows, Mac and Linux 
# If creation date fails (happens in Linux), it falls back to returning last modified date and time

def creation_date(path_to_file):

    creation_local_time = 0

    # Checking for Windows

    if platform.system() == 'Windows':
        creation_local_time = time.localtime(os.path.getctime(path_to_file))
    else:
        stat = os.stat(path_to_file)
        
        # Usually Mac and UNIX based systems but sometimes Linux
        try:
            creation_local_time = time.localtime(stat.st_birthtime)
        
        # Stored last modified data and time
        except AttributeError:
            creation_local_time = time.localtime(stat.st_mtime)
    
    # Making a list with creation year and creation month respectively
    creation_year_month = []
    creation_year_month.append(creation_local_time.tm_year)
    creation_year_month.append(creation_local_time.tm_mon)

    return creation_year_month

def extract():

    global isRoot
    global to_be_deleted
    global count

    print("Entered " + str(os.getcwd()))
    current_path = os.getcwd()

    # Holding subfolders and files in current directory
    file_names = os.listdir('.')

    # This section will be processed only if we are in the root directory
    if(isRoot):
        # If folders are excluded, the will be removed from the file_names
        for each_excluded_file in excluded_files:
            if(each_excluded_file in file_names):
                file_names.remove(each_excluded_file)

        to_be_deleted = file_names.copy()
        isRoot = False

    # Checking if each file is a directory. If it is, it will change current directory to the sub-directory and call extract again
    # After that, it removes the folder from file_names[] and moves on to the next one
    for each_file in file_names:

        # If it is hidden, continue
        if(each_file.startswith('.')):
            continue

        # Recursively calling the extract function after changing working directory to sub folder
        if (os.path.isdir(os.path.join(os.getcwd(), each_file))):
            os.chdir(os.path.join(os.getcwd(), each_file))
            extract()
            os.chdir(current_path)

    # Moving each file to respective folder
    for each_file in file_names:

        # If it is a folder, ignore
        if (os.path.isdir(os.path.join(os.getcwd(), each_file))):
            continue

        # If it is hidden, ignore
        if(each_file.startswith('.')):
            continue

        # Getting the Month and Year of each file
        creation_year_month = creation_date(each_file)
        creation_year = str(creation_year_month[0])
        creation_month = months[creation_year_month[1]]

        # Marking the current file path and the output file path
        # This is done because os.replace() method needs two arguments with the file name
        current_file = os.path.join(current_path, each_file)
        output_path = os.path.join(root_dir, creation_year, creation_month)
        output_file = os.path.join(output_path, each_file)

        if not (os.path.exists(output_path)):
            os.makedirs(output_path)

        if(args.m == True):
            os.rename(current_file, output_file)
            print("Moved {}".format(each_file))
        elif(args.c == True):
            dest = shutil.copyfile(current_file, output_file)
            print("Copied {}".format(each_file))

        count = count+1
        print("Processed {} files".format(count))
        

# Adding files/folders specified in the input file. These files/folders won't be processed
def add_excluded_files():

    if(os.path.exists("input.txt")):
        input_file = "input.txt"
        with open(input_file, "r") as in_buf:
            for line in in_buf:
                if not line.strip() == '':
                    excluded_files.append(line.strip())
            
            excluded_files.append(input_file)
        
def main():
    
    add_excluded_files()

    # Checking for Files and Folders in current working directory
    if not os.listdir('.'):
        print("No files found")
    
    # If files exist, begin the process
    else:
        extract()  

    if(args.d == True and args.m == True):
        for each_folder in to_be_deleted:
            if not (each_folder.startswith('.')):
                try:
                    shutil.rmtree(each_folder)
                except:
                    print("Error deleting folder {}. Please check for file misses".format(each_folder))

if __name__ == "__main__":
   main()