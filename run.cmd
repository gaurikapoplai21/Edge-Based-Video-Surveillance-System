start cmd.exe @cmd /k "python t3.py 5004"
timeout 3
start cmd.exe @cmd /k "python t2.py 5001 5004"
timeout 3
start cmd.exe @cmd /k "python t2.py 5002 5004"
timeout 3
start cmd.exe @cmd /k "python t2.py 5003 5004"
timeout 3
start cmd.exe @cmd /k "python t1.py"
start cmd.exe @cmd /k "cd algorithms\MobileNet&python main.py"
