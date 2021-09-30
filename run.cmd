start /MIN cmd.exe @cmd /k "python t3.py 5005&exit"
timeout 3
start /MIN cmd.exe @cmd /k "python t2.py 5002 5005&exit"
timeout 3
start /MIN cmd.exe @cmd /k "python t2.py 5003 5005&exit"
timeout 3
start /MIN cmd.exe @cmd /k "python t2.py 5004 5005&exit"
timeout 5
start /MIN cmd.exe @cmd /k "python t1.py 5001&exit"
start /MIN cmd.exe @cmd /k "cd algorithms\MobileNet&python main.py&exit"
exit