import inspect
import imp
import plugintemplate
import glob
import sys
import os

class pluginmanager:
    def __init__(self, main):
        self.main = main
        self.instances = {}
        sys.path.append(os.getcwd() + "/plugins")

    def LoadPlugins(self):
        modules = glob.glob("plugins/*.py")
        loaded = 0
        for i in modules:
            split = i.split("/")
            name = split[len(split)-1].split(".")
            if self.Load(name[0]):
                loaded += 1
        return loaded

    def Load(self, name):
        success = False
        try:
            file = imp.find_module(name)
            if file:
                try:
                    module = imp.load_module(name, file[0], file[1], file[2])
                    for i in inspect.getmembers(module, inspect.isclass):
                        if isinstance(i, plugintemplate.plugin):
                            self.instances[name] = i
                            i.main = self
                            i.OnEnable()
                            success = True
                            break
                except:
                    self.main.LogError()
                finally:
                    file[0].close()
        except ImportError:
            self.main.LogError()
        return success

    def Unload(self, name):
        if name in self.instances.keys():
            self.instances[name].OnDisable()
            del self.instances[name]

    def FindPlugin(self, name):
        if name in self.instances.keys():
            return self.instances[name]

    def PluginExists(self, name):
        return name in self.instances.keys()

    def Load(self,command):
        split = command.message.split(" ")
        user = self.main.um.users[command.nick]
        if split[0] == "@all":
            self.main.b.Msg(command.source,"I have successfully loaded {} plugins for you, {}".format(self.LoadAll(),user.RandTag()))
        else:
            if self.Load(split[0]):
                self.main.b.Msg(command.source,"I have successfully loaded the module: {} for you, {}.".format(split[0],user.RandTag()))
            else:
                self.main.b.Msg(command.source,"I was unable to load that module, {}, perhaps it does not exist?".format(user.RandTag()))

    def Unload(self,command):
        split = command.message.split(" ")
        user = self.main.um.users[command.nick]
        if split[0] in self.instances.keys():
            self.Unload(split[0])
            self.main.b.Msg(command.source,"I have successfully unloaded the module you requested, {}!".format(user.RandTag()))
