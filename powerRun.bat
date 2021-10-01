start Powershell.exe -windowstyle hidden -c "python t3.py 5005"
timeout 3
start Powershell.exe -windowstyle hidden -c "python t2.py 5002 5005"
timeout 3
start Powershell.exe -windowstyle hidden -c "python t2.py 5003 5005"
timeout 3
start Powershell.exe -windowstyle hidden -c "python t2.py 5004 5005"
timeout 5
start Powershell.exe -windowstyle hidden -c "python t1.py 5001"
start Powershell.exe -windowstyle hidden -c "python algorithms\MobileNet\main.py"