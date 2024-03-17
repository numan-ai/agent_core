import os
import abc
import time
import logging
import threading


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    
    log_id = max([
        int(f.split("_")[1].split(".")[0])
        for f in os.listdir("logs")
        if f.startswith("log_") and f.endswith(".txt")
    ], default=-1) + 1
    log_name = f"logs/log_{log_id}.txt"
    logging.basicConfig(filename=log_name,
        filemode='a',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.DEBUG)


setup_logging()
logger = logging.getLogger(__name__)


def handle_input(api, say):
    while True:
        user_input = input("")
        func_name, *args = user_input.split()
        logger.info("< %s", user_input)
        
        args = [
            int(arg) if arg.isdigit() else arg
            for arg in args
        ]
        
        if func_name == "say":
            func = say
        elif hasattr(api, func_name):
            func = getattr(api, func_name)
        else:
            print(f"Unknown function: {func_name}")
            logger.info("Unknown function: %s", func_name)
            continue
        
        try:
            output = func(*args)
        except Exception as e:
            output = f"{type(e)} {str(e)}"
        logger.info("> %s", output)
        print('>', output)


def api_say(text, block=True):
    print(f">> {text}")
    logger.info(">> %s", text)
    if block:
        answer = input("User answer: ")
        logger.info("User answer: %s", answer)


class Scenario(abc.ABC):
    def __init__(self, world):
        self.world = world
        self.api = self.world.api
    
    def say(self, text: str):
        print(f">> {text}")
        logger.info(">> %s", text)
        
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
    