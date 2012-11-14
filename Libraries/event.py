import traceback
class Event:
    def __init__(self):
        self.handlers = []

    def handle(self, handler):
        self.handlers.append(handler)
        return self

    def unhandle(self, handler):
        try:
            self.handlers.remove(handler)
        except:
            raise ValueError("Handler is not handling this event, so cannot unhandle it.")
        return self

    def fire(self, *args, **kargs):
        for handler in self.handlers:
            try:
                handler(*args, **kargs)
            except:
                traceback.print_exc()

    def getHandlerCount(self):
        return len(self.handlers)

    __iadd__ = handle
    __isub__ = unhandle
    __call__ = fire
    __len__  = getHandlerCount
