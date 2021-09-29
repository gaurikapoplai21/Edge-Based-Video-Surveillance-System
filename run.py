# "python t3.py 5005"
# timeout 3
# start cmd.exe @cmd /k "python t2.py 5002 5005"
# timeout 3
# start cmd.exe @cmd /k "python t2.py 5003 5005"
# timeout 3
# start cmd.exe @cmd /k "python t2.py 5004 5005"
# timeout 5
# start cmd.exe @cmd /k "python t1.py 5001"
# start cmd.exe @cmd /k "cd algorithms\MobileNet&python main.py"

import subprocess
import time

if __name__ == "__main__":
    cmds = [
        {"args": ["python", "t3.py", "5005"], "close_fds": True},
        {"args": ["python", "t2.py", "5002", "5005"], "close_fds": True},
        {"args": ["python", "t2.py", "5003", "5005"], "close_fds": True},
        {"args": ["python", "t2.py", "5004", "5005"], "close_fds": True},
        {"args": ["python", "t1.py", "5001"], "close_fds": True},
        {"args": ["python", "algorithms\MobileNet\main.py"], "close_fds": True},
    ]

    processes = []
    for command in cmds:
        processes.append(subprocess.Popen(**command))
        time.sleep(5)

    # time.sleep(30)
    # for p in processes:
    #     p.terminate()
