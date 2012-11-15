import sys

class stdout:
    def __init__(self, main):
        self.main = main
        self.channel = None

    def write(self, toprint):
        if self.channel:
            print(toprint, file=sys.__stdout__)
        elif toprint != "\n":
            self.main.b.Msg(self.channel,toprint)

class Command:
    def __init__(self, name):
        self.name = name
        self.callbacks = []
        self.modules = []
        self.level = 0
        self.helptext = ""
        self.usage = ""
        self.source = None
        self.user = None
        self.message = None
        
    def AddListener(self, callback, level = None):
        self.callbacks.append(callback)
        self.modules.append(callback.__self__)
        if not level:
            self.level = level
        