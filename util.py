import os

filename = 'bestandawsefsefse.txt'
naam_zonder_extensie = os.path.splitext(filename)[0]
print(naam_zonder_extensie)  # Output: 'bestand'