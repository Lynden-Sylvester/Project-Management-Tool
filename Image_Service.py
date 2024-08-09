import time
import os


def read_file():

  return int(content)


while True:
  time.sleep(5)
  with open("image-service.txt", "r") as file:
    content = file.read().strip()

  if content.isdecimal():

    index = int(content)

    filenames = os.listdir("static/images")

    correct_index = index % len(filenames)

    print(os.path.join("static/images", filenames[correct_index]))
    with open("image-service.txt", "w") as file:
      file.write(str(os.path.join("static/images", filenames[correct_index])))
