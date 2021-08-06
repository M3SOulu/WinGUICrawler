import os
import json
#directory where the screenshots (.png and .xml) are saved
directory = '%s/' % os.getcwd()+"paint/"
all_screens = []

for file in os.listdir(directory):
    if file[-4:] == ".txt":
        with open(directory+file) as json_file:
            data = json.load(json_file)

i = 0
for song in data.items():
    # now song is a dictionary
    print(song)
    i+=1
    if i>5:
        exit()
