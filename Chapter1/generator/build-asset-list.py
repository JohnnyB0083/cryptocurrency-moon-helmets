import os

path = "assets/"
filename = "helmet_layers.csv"
fields = ["Filename"]

with open(filename, 'w') as image_file:
    files = os.listdir(path)
    for file in files:
        if file.endswith(".png"):
            image_file.write(str(file))
            image_file.write('\n')