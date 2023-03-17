import os

path = "output/images/"

files = os.listdir(path)

for file in files:
    os.remove(path + file)

path = "output/metadata/"

files = os.listdir(path)

for file in files:
    os.remove(path + file)
