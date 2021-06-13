import platform
import subprocess


def check_ping(host):
    if platform.system().lower() == "linux":
        ping = subprocess.check_output(["ping", "-c", quantity, host])
        latency = ping.split()[-2]
        resp = str(latency, 'utf-8')
        print(resp)
        resp2= resp.split("/")[2]
        return resp2
    if platform.system().lower() == "windows":
        ping = subprocess.check_output(["ping", "-n", quantity, host])
        latency = ping.split()[-1]
        resp = str(time, 'utf-8')
        resp2= resp.split("=")[0]
        resp3=resp2[:2]
        return resp3
        
host="10.0.0.1"
quantity="5"
print(check_ping(host))