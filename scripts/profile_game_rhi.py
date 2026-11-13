"""
Profiler script utilizing simpleperf to inspect live graphics symbols in target Android process.
"""
import subprocess
import sys

def get_target_pid(pkg="com.rockstargames.gtavc.de"):
    out = subprocess.check_output(['adb', 'shell', 'su', '-c', f'pidof {pkg}']).decode('utf-8').strip()
    return out.split()[0] if out else None

def profile_pid(pid, duration=2):
    print(f"[*] Profiling PID {pid} for {duration} seconds with simpleperf...")
    subprocess.call(['adb', 'shell', 'su', '-c', f'simpleperf record -p {pid} --duration {duration} -o /data/local/tmp/perf.data'])
    report = subprocess.check_output(['adb', 'shell', 'su', '-c', 'simpleperf report -i /data/local/tmp/perf.data --sort dso,symbol | head -n 35']).decode('utf-8')
    print("[+] Report output:\n")
    print(report)

if __name__ == "__main__":
    pid = get_target_pid()
    if not pid:
        print("[-] Target process not running.")
        sys.exit(1)
    profile_pid(pid)
