from Libraries import biblib
from threading import Timer
import constants
import imp
import glob
import os
import sys
import traceback
        
class main:
    def __init__(self):
        self.b = biblib.bot()
        self.nick = constants.nick
        self.b.initconnection(constants.ircinfo,self.nick)
        self.instances = {}
        self.t = Timer(5.0,self.Flush)
        self.t.start()
        self.errorlog = open(os.getcwd() + "/logs/bot.txt","a")
        self.b.ircevents.Connected += self.Connected
        
    def Connected(self):
        result = self.LoadAll()
        self.b.PrintCon("Successfully loaded: {} utilities and {} modules!".format(result[0],result[1]))   
        
    def LogError(self):
        error = traceback.format_exc()
        self.b.PrintCon(error)
        self.errorlog.write(error)
        
    def Flush(self):
        self.errorlog.flush()
        self.t = Timer(5.0, self.Flush)
        self.t.start()
    
    def LoadAll(self):
        return self.LoadPlugins("utilities"), self.LoadPlugins("modules")
        
    def LoadPlugins(self, path):
        sys.path.append(os.getcwd() + "/" + path)
        modules = glob.glob(path + "/*.py")
        loaded = 0
        for i in modules:
            split = i.split("/")
            name = split[len(split)-1].split(".")
            if(self.Load(name[0])):
                loaded = loaded + 1
        sys.path.remove(os.getcwd() + "/" + path)
        return loaded
        
    def Load(self, name):
        success = False
        try:
            file = imp.find_module(name)
            if(file):
                try:
                    module = imp.load_module(name, file[0], file[1], file[2])
                    self.instances[name] = module.main(self)
                    success = True
                except:
                    self.LogError()
                finally:
                    file[0].close()
        except ImportError:
            self.LogError()
        return success

main()
