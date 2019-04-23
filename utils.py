import os

def read_rocket_frames(directory):
  frames = []

  for file in os.listdir(f"{directory}"):
      with open(f"{directory}/{file}", "r") as my_file:
          frame = my_file.read()
          frames.append(frame)

  return frames