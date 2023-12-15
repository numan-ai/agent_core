import os
import shlex
import subprocess
import time


class SensoryModule:
    def __init__(self):
        pass

    def get_sensory_data(self):
        cmd = shlex.split("bash -c \"ls -ohAp | tail --lines=+2 | sed -re 's/^[^ ]* *[^ ]* *[^ ]*//'\"")
        output = subprocess.check_output(cmd)
        
        file_content = output.decode('utf-8').rstrip()
        
        current_time = subprocess.check_output(shlex.split("date")).decode('utf-8').rstrip()
        
        return f"Time: {current_time}\nContent:\n{file_content}"


def main():
    os.chdir('./workdir/')
    sensory_module = SensoryModule()
    while True:
        print(sensory_module.get_sensory_data())
        time.sleep(1)
    pass


if __name__ == '__main__':
    main()
