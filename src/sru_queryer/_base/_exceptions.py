from __future__ import annotations

class NoExplainResponseException(Exception):
    """This is an exception for the case that the explainResponse request does not return an
    explainResponse. This is usually due to an error in the explainResponse request."""
    
    def __init__(self, message, content):
        self.message = message
        self.content = content
        super().__init__(self.message)

class ExplainResponseParserException(Exception):
    """This returns when there is an explainResponse in the correct format, but for some reason
    the parser cannot parse it. This would likely be due to logic error or oversight in the program."""
    
    def __init__(self, message, content):
        self.message = message
        self.content = content
        super().__init__(self.message)

class ExplainResponseContentTypeException(Exception):
    """This exception is thrown when the actual request contents could not be parsed into a
    python dictionary using xmltodict. This is likely because the server returned a format
    other than XML"""
    def __init__(self, message, content):
        self.message = message
        self.content = content
        super().__init__(self.message)