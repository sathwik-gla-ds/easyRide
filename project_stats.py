from os import listdir
from os.path import isfile, join

file_types = ['py', 'html', 'css', 'js']
comment_types =  {'py':'#', 'html':'<!--', 'css':'/*', 'js':'//'}
file_c = {'py':0, 'html':0, 'css':0, 'js':0}
line_c = {'py':0, 'html':0, 'css':0, 'js':0}
char_c = {'py':0, 'html':0, 'css':0, 'js':0}
percentage = {'py':0, 'html':0, 'css':0, 'js':0}
comments = {'py':0, 'html':0, 'css':0, 'js':0}

def read_folder(path):
    if path:
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        onlydirectories = [f for f in listdir(path) if not isfile(join(path, f))]
    else:
        onlyfiles = [f for f in listdir() if isfile(join(path, f))]
        onlydirectories = [f for f in listdir() if not isfile(join(path, f))]
    for ext in file_types:
        for file in onlyfiles:
            try:
                if file.split('.')[1] == ext:
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
                                # if ('#' in str(line)) or  ('//' in str(line)) or ('<!--' in str(line)) or ('/*' in str(line)):
                                #     comment += 1
                    line_c[ext] += lines
                    char_c[ext] += characters
                    file_c[ext] += 1
                    comments[ext] += comment
            except: ''
    for folder in onlydirectories:
        read_folder(join(path, folder))

read_folder('')
print(line_c)
print(char_c)
print(file_c)
for k in percentage:
    percentage[k] =(char_c[k] / sum(char_c.values())) * 100
print(percentage)
print(comments)
