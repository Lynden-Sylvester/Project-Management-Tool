import random
import time


def read_file():
  with open("prng-service.txt", "r") as file:
    content = file.read()
  return content


def generate_random_number():

  generated_random_number = random.randint(1, 10)
  with open("prng-service.txt", "w") as file:
    file.write(str(generated_random_number))


while True:
  time.sleep(1)
  read_file()

  content = read_file()

  if "run" in content.lower():
    generate_random_number()
