class Renderer:
    def __init__ (self, handler, config):
        self.handler = handler
        self.config = config
        self.rrdFile = config.get('rrdtool', 'file')

    def responseCode (self, code):
        self.handler.send_response(200)

    def contentType (self, contentType):
        self.handler.send_header('Content-type', contentType)
        self.handler.end_headers()
