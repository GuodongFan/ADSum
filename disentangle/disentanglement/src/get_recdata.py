import sys
import argparse

count = 0
data_list = []

parser = argparse.ArgumentParser(description='IRC Conversation Disentangler.')
parser.add_argument('--input-file', nargs="+", help="Training files, e.g. train/*.annotation.txt")

args = parser.parse_args()

INPUT_FILES = args.input_file
num_dialogs = 0
for input_file in INPUT_FILES:
    with open(input_file, 'r') as file:
        lines = file.readlines()
        data = []
        for line in lines:

            if line == '=======================\n':
                count = 0
                num_dialogs = num_dialogs + 1
                data_list.append(data)
            elif count == 0:
                data = []
                values = line.split('\t')
                user = values[1]
                count += 1
                data.append(line)
                data.append(user)
            else:
                values = line.split('\t')
                user = values[1]
                count += 1
                data.append(user)

    min = 10
    max = 0
    statistics = {}
    for data in data_list:
        #print('QA:', data[0])
        names = set()
        for i in range(1, len(data)):
            #print(data[i])
            names.add(data[i])
        if len(names) > max:
            max = len(names)
        if len(names) < min:
            min = len(names)
        key = str(len(names))
        if key in statistics.keys():
            statistics[key] = statistics[key] + 1
        else:
            statistics[key] = 1
    print('max' , max)
    print('min', min)
    for key, val in statistics.items():
        print(key)
        print(val)
        print('*******')
    print('num dialogs:', num_dialogs)

