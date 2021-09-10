import json
import subprocess

l = [1, 2, 1, 5.6]
l = json.dumps(l)

subprocess.call('python t1.py "%s"' % l, shell=True)
