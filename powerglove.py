import os, serial, rrdtool, time, BaseHTTPServer, socket
import urlparse, cgi, ConfigParser, sys, re

from xml.etree.ElementTree import fromstring
from threading import Thread

config = ConfigParser.ConfigParser()
config.read('powerglove.conf')
rrdFile = config.get('rrdtool', 'file')

class LogThread (Thread):
    def __init__ (self):
        Thread.__init__(self)

    def run (self):

        if not os.path.exists(rrdFile):

            rrdtool.create (
                rrdFile,
                '--step', '6',              # The currentcost meter updates every 6s
                '--start', str(int(time.time())),
                'DS:watts:GAUGE:600:U:U',
                'DS:temp:GAUGE:600:U:U',
                'RRA:AVERAGE:0.5:1:300',    # Every 6s for the last 30mins
                'RRA:AVERAGE:0.5:5:1440',   # Every 30s for the last 12hrs
                'RRA:AVERAGE:0.5:10:10080', # Every min for the last week
                'RRA:AVERAGE:0.5:50:25920', # Every 5m for the last 3mon
                'RRA:AVERAGE:0.5:300:17280',# Every 30m for the last 12mon
            )

        sio = serial.Serial(
            config.get('serial', 'port'), 
            config.get('serial', 'baudrate'), 
            timeout = 1
        )

        lastTime = 0
        while True:
            line = sio.readline()

            if line:

                try:
                    tree = fromstring(line)
                except:
                    continue

                temp = tree.find('tmpr')
                watts = tree.find('ch1/watts')
                now = int(time.time())

                # Sporadically two lines are output with the same timestamp
                # which makes rrdtool freak out
                if temp != None and watts != None and now > lastTime:
                    rrdtool.update (
                        rrdFile,
                        '%d:%s:%s' % (now, int(watts.text), float(temp.text))
                    )

                    lastTime = now


class ServerThread (Thread):
    def __init__ (self):
        Thread.__init__(self)

    def run (self):
        httpd = BaseHTTPServer.HTTPServer(('', int(config.get('http', 'port'))), Server)
        httpd.serve_forever()


class Server(BaseHTTPServer.BaseHTTPRequestHandler):

    # Disable logging DNS lookups for moar speed
    def address_string(self):
        return str(self.client_address[0])

    def do_GET(self):

        url = urlparse.urlparse(self.path)
        params = cgi.parse_qs(url.query)

        # Default to the last hour
        now = int(time.time())
        startTime = now - 3600
        endTime = now

        try:
            if 'end' in params:
                endTime = int(params['end'][0])

            if 'back' in params:
                startTime = endTime - int(params['back'][0])

            if 'start' in params:
                startTime = int(params['start'][0])

        except:
            self.send_error(500, 'Failed to parse params')
            return

        match = re.match('/(\w+)', url[2])
        if match:
            moduleName = match.group(1)
        else:
            moduleName = 'default'

        moduleName = moduleName.capitalize() + 'Renderer'

        try:
            module = __import__('Renderers.' + moduleName)
            submodule = module.__getattribute__(moduleName)
            renderer = submodule.__getattribute__(moduleName)(self, config)
        except ImportError:
            renderer = None

        if renderer:

            stdout = sys.stdout
            try:
                sys.stdout = self.wfile
                renderer.render(startTime, endTime, params)
                stdout = sys.stdout
            finally:
                sys.stdout = stdout

        else:
            self.send_error(404, 'Unknown Renderer')


log = LogThread()
log.setDaemon(True)
log.start()

server = ServerThread()
server.setDaemon(True)
server.start()

# So this thread can be killed, watch the threads rather than joining them
while log.isAlive() and server.isAlive():
    time.sleep(1)
