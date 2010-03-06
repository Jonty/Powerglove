import Renderer, tempfile, shutil, rrdtool, os

class GraphRenderer(Renderer.Renderer):
    def render (self, startTime, endTime, params):

        graphtype = 'watts'
        label = 'Watts'
        colour = '1800FF'

        if 'type' in params and params['type'][0] == 'temp':
            graphtype = 'temp'
            label = 'Temperature'
            colour = 'FF0000'

        title = label
        if 'title' in params:
            title = params['title'][0]

        width = 540
        if 'width' in params:
            width = params['width'][0]

        height = 100
        if 'height' in params:
            height = params['height'][0]

        if 'colour' in params:
            colour = params['colour'][0]

        try:
            (fd, path) = tempfile.mkstemp('.png')

            rrdtool.graph(
                path,
                '--imgformat', 'PNG',
                '--width', str(width),
                '--height', str(height),
                '--start', str(startTime),
                '--end', str(endTime),
                '--vertical-label', label,
                '--title', title,
                '--lower-limit', '0',
                'DEF:data=%s:%s:AVERAGE' % (self.rrdFile, graphtype),
                'AREA:data#%s:%s' % (colour, label),
            )

            f = open(path, 'rb')

        except:
            self.handler.send_error(500, 'Graph failed to render')
            return

        try:
            self.responseCode(200)
            self.contentType('image/png')
            shutil.copyfileobj(f, self.handler.wfile)
        except socket.error, e:
            pass

        f.close()
        os.remove(path)
