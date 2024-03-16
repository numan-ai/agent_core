

import abc
import time
import threading


def handle_input(api, say):
    while True:
        code = input()
        try:
            output = eval(code, {}, {
                "api": api,
                "say": say,
            })
        except Exception as e:
            output = str(e)
        print('>', output)


def api_say(self, text, block=True):
    print(f">> {text}")
    if block:
        input("User answer: ")


class Scenario(abc.ABC):
    def __init__(self, world):
        self.world = world
        self.api = self.world.api
    
    def say(self, text: str):
        print(f">> {text}")
        
    def run(self):
        threading.Thread(
            target=handle_input,
            kwargs={
                "api": self.world.api,
                "say": api_say
            },
            daemon=True
        ).start()
        
        self.setup()
        while True:
            if self.check():
                return
            self.world.step()
            time.sleep(0.1)
         
    @abc.abstractmethod   
    def setup(self):
        pass
    
    @abc.abstractmethod
    def check(self):
        pass
    