import inspect
import imp
import plugin
import glob

class pluginmanager:
    def __init__(self, main):
        self.main = main
        self.instances = {}

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
                        if isinstance(i, plugin.plugin):
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

    def FindPlugin(self, name):
        if name in self.instances.keys():
            return self.instances[name]

    def PluginExists(self, name):
        return name in self.instances.keys()
