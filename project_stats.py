# Calculates some cool project statistics such as how much each type of language is being used and prints it as an output
from os import listdir
from os.path import isfile, join

# Define different file types to llok for and also initialze the dicts to store the result for each file type
file_types = ['py', 'html', 'css', 'js']
comment_types =  {'py':'#', 'html':'<!--', 'css':'/*', 'js':'//'}
file_c = {'py':0, 'html':0, 'css':0, 'js':0}
line_c = {'py':0, 'html':0, 'css':0, 'js':0}
char_c = {'py':0, 'html':0, 'css':0, 'js':0}
percentage = {'py':0, 'html':0, 'css':0, 'js':0}
comments = {'py':0, 'html':0, 'css':0, 'js':0}

def read_folder(path):
    # Get a list of files and another list of folders present in the curretn path
    if path:
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        onlydirectories = [f for f in listdir(path) if not isfile(join(path, f))]
    else:
        onlyfiles = [f for f in listdir() if isfile(join(path, f))]
        onlydirectories = [f for f in listdir() if not isfile(join(path, f))]
    # For each file in our filetypes count the number of lines(non-empty), comments, chars and also add 1 to the files dict
    for file in onlyfiles:
        try:
            if file.split('.')[1] in file_types:
                ext = file.split('.')[1]
                with open(join(path,file)) as infile:
                    lines=0
                    characters=0
                    comment = 0
                    for line in infile:
                        if line != "\n":
                            lines += 1
                            characters += len(line)
                            if comment_types[ext] in str(line):
                                comment += 1
                line_c[ext] += lines
                char_c[ext] += characters
                file_c[ext] += 1
                comments[ext] += comment
        except: ''
    # For each folder present recurcively run this function again to perform the same operation on files present inside them
    for folder in onlydirectories:
        read_folder(join(path, folder))

read_folder('') #Run the function with the base path
# Calculate the percentage based on chars present within each language 
for k in percentage:
    percentage[k] = float("{:.2f}".format((char_c[k] / sum(char_c.values())) * 100))

print('\n\nType\tLines\t\tChars\t\tFiles\t\tPercent\t\tComments')
print('-'*100)
for ftype in file_types:
    print('{}\t{}\t\t{}\t\t{}\t\t{}\t\t{}'.format(ftype, line_c[ftype], char_c[ftype], file_c[ftype], percentage[ftype], comments[ftype]))
print('-'*100)
print('Total\t{}\t\t{}\t\t{}\t\t{:.0f}\t\t{}'.format(sum(line_c.values()), sum(char_c.values()), sum(file_c.values()), round(sum(percentage.values()),0), sum(comments.values())))
