# File-Organiser 

<p align="center">
<a href="https://www.python.org/"><img alt="Python Version"src = "https://img.shields.io/pypi/pyversions/ansicolortags.svg" ></a> <a href = "https://www.linux.org/">
<img alt="PowerShell Gallery" src="https://img.shields.io/powershellgallery/p/Az?color=blue&logo=linux&logoColor=white"> </a>
</p>

A python script which will recursively visit every sub-folder in the current directory and organise each file according to the Year and Month of it's creation.

## How to use
Download the file `File_Organiser.md` and `input.txt` and place it in the directory where the organising needs to be done.

Run the script and voila! Your job is done.

### Usage 
```
python File_Organiser.py  [-m / -c] [-d]
```
### Flags
- `-m` flag is to be used when a __move__ operation is to be made, i.e the original file will be copied to the new location and deleted.
- `-c` flag is to be used when a __copy__ operation is to be made, i.e the original file will be copied to the new location and it __will not__ be deleted. (Use with caution since space requirements will double)
- `-d` flag is to be used when the residual folders are to be deleted after the move operation.

__Note__: `-m` flag and `-c` flag cannot be used together. They are __mutually exclusive__. Usage of `-d` flag with `-c` flag will __not__ delete anything, i.e `-d` flag is useless in this context.

### Excluding Files / Folders

There is an option to exclude certain files and folders. Add the files and folder names in `input.txt` with each file/folder seperated by a new line like so -

```
Folder1
Folder2
Folder3
```
__Note:__ `input.txt` is to be placed within the __same__ directory as `File_Organiser.py`.
