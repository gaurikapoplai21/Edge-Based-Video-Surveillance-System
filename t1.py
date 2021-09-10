import json
import sys

list_from_other_process = json.loads(sys.argv[1])
print(list_from_other_process)
