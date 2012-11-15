import constants
import plugintemplate
class joichannels(plugintemplate.plugin):
    def __init__(self):
        self.main.b.Join(", ".join(constants.channels))