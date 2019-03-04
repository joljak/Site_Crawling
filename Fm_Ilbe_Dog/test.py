import os
from pathlib import Path

p = Path(__file__).parents[0]

print(p)

FILE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

print(FILE_DIRECTORY)

bach = os.path.abspath(os.path.join(__file__, "../.."))

print(bach)