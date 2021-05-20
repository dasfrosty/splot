class LazyProxy:
    """
    Proxy for an object that is lazily initialized upon first use.
    Inspired by werkzeug.local.LocalProxy.
    """

    def __init__(self, initializer):
        self.initializer = initializer
        self.initialized = False
        self.proxied = None

    def _object(self):
        if not self.initialized:
            self.proxied = self.initializer()
            self.initialized = True
        return self.proxied

    def __getattr__(self, name):
        if name == "__members__":
            return dir(self._object())
        return getattr(self._object(), name)

    def __getitem__(self, key):
        return self._object()[key]

    def __repr__(self):
        return repr(self._object())
