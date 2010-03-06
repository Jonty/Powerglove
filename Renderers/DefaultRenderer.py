import Renderer, sys, glob, re

class DefaultRenderer (Renderer.Renderer):
    def render (self, startTime, endTime, params):

        self.responseCode(200)
        self.contentType('text/html; charset=utf-8')

        print '<h1>Powerglove Output Formats</h1>'
        print '<ul>'

        files = glob.glob('Renderers/*Renderer.py')
        for item in files:
            match = re.match('Renderers/(\w+)Renderer.py', item)

            if match and match.group(1) != 'Default':
                module = match.group(1)
                print "<li><a href='/%s'>%s</a></li>" % (module, module)

        print '</ul>'
