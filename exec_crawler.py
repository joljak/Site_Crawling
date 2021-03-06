import json
import os
import subprocess
import sys
import time

if __name__ == '__main__':
    FILE_DIRECTORY = os.path.abspath(os.path.join(__file__, '..'))
    with open(os.path.join(FILE_DIRECTORY, 'slang.json'), encoding='utf-8') as slang_file:
        SLANG = json.load(slang_file)['unordered']

    if len(sys.argv) < 2:
        exit('''
        Argument Error
        Choice Site [Clien, Inven, Ruliweb]
        Choice Type [link, content]
        usage) exec_crawler.py [Site] [Type]
        ''')

    SITE = sys.argv[1] if sys.argv[1] in ['Clien', 'Inven', 'Ruliweb'] else exit("Please. Retry input site name")
    TYPE = sys.argv[2] if sys.argv[2] in ['link', 'content'] else exit("Please. Retry input type")
    idx = SLANG.index(sys.argv[3]) if len(sys.argv) >= 4 and sys.argv[3] in SLANG else 0
    end = SLANG.index(sys.argv[4]) if len(sys.argv) >= 5 and sys.argv[4] in SLANG else None
   
    for keyword in SLANG[idx:end]:
        subprocess.call(f'python {FILE_DIRECTORY}/{SITE}/{SITE.lower()}.py {TYPE} {keyword}', shell=True)
        time.sleep(2)
