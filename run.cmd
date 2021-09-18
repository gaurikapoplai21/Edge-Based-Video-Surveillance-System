start cmd.exe @cmd /k "python t3.py 5005"
timeout 3
start cmd.exe @cmd /k "python t2.py 5002 5005"
timeout 3
start cmd.exe @cmd /k "python t2.py 5003 5005"
timeout 3
start cmd.exe @cmd /k "python t2.py 5004 5005"
timeout 5
start cmd.exe @cmd /k "python t1.py 5001"
start cmd.exe @cmd /k "cd algorithms\MobileNet&python main_test.py"
