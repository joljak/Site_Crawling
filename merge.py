import json
import os
import csv
import sys


ROOT_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))
SLANG_FILE = os.path.abspath(os.path.join(ROOT_DIRECTORY, 'slang.json'))
with open(SLANG_FILE, 'r', encoding='utf-8') as slang_file:
    SLANG = json.load(slang_file)['slang']



field_name = ['content', 'label']

for site in  ['clien', 'inven', 'ruliweb'] :
    for slang in SLANG:
        processed_path = os.path.join(ROOT_DIRECTORY, site, 'processed', f'{site}_{slang}_processed.csv')

        labeled_path = os.path.join(ROOT_DIRECTORY, 'labeled.csv')

        with open(processed_path, 'r', encoding='utf-8', newline='\n') as processed_file:
            reader = csv.reader(processed_file)
            next(reader, None)
            for row in list(reader):
                with open(labeled_path, 'a', encoding='utf-8', newline='\n') as labeled_file:
                    writer = csv.DictWriter(
                        labeled_file, fieldnames=field_name
                    )
                    writer.writerow({'content': row[0], 'label':row[1]})


        
        
