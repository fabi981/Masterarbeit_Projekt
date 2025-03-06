import subprocess

#Zum Profilen des Speicherverbrauchs und so weiter
#import psutil
#import time





def run_dash():
    return subprocess.Popen(["python3", "Dash_Module.py"])

def run_flask():
    return subprocess.Popen(["python3", "Flask_Module.py"])

if __name__ == '__main__':
    flask_process = run_flask()
    dash_process = run_dash()
