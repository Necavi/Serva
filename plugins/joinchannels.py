import constants
import plugin
class joichannels(plugin.plugin):
    def __init__(self):
        self.main.b.Join(", ".join(constants.channels))