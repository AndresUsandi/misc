class BookParserRegistry:
    def __init__(self):
        self._parsers = {}
        
    def register_parser(self, extension: str, parser_class, unwrap=None):
        self._parsers[extension.lower()] = (parser_class, unwrap)
        
    def get_parser(self, extension: str):
        val = self._parsers.get(extension.lower())
        if not val:
            return None
        parser_class, default_unwrap = val
        if default_unwrap is not None:
            try:
                return parser_class(unwrap=default_unwrap)
            except TypeError:
                return parser_class()
        return parser_class()
