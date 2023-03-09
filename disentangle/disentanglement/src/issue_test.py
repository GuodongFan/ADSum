import argparse
import spacy

parser = argparse.ArgumentParser(description='IRC Conversation Disentangler.')
# Data arguments
parser.add_argument('--files', nargs="+", help="Training files, e.g. train/*.annotation.txt")
args = parser.parse_args()


for filename in args.files:
    name = filename
    for ending in [".annotation.txt", ".ascii.txt", ".raw.txt", ".tok.txt"]:
        if filename.endswith(ending):
            name = filename[:-len(ending)]

    with open(name+'.raw.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            print(line)
