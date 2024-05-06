class LED:
    def __init__(self, value) -> None:
        self.value = value
    
    @property
    def is_on(self):
        return self.value == 1
    
    @is_on.setter
    def is_on(self, value):
        self.value = 1 if value else 0

Instance("Pin", {
    "value": Instance("Number", {
        "value": 12
    })   
})
led = LED(1)
led.value = 0

print(led.is_on)

led.is_on = True

print(led.value)
