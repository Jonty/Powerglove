import Renderer, rrdtool

class JsonRenderer (Renderer.Renderer):
    def render (self, startTime, endTime, params):

        (metadata, titles, data) = rrdtool.fetch(
            self.rrdFile, 
            "--start", str(startTime),
            "--end", str(endTime), 
            "AVERAGE"
        )

        dataStrings = []
        timestamp = metadata[0]
        for item in data:

            first = item[0]
            if first == None:
                first = 0;

            second = item[1]
            if second == None:
                second = 0;

            dataStrings.append(
                "{timestamp: %d, %s: %f, %s: %f}" % 
                (timestamp, titles[0], first, titles[1], second)
            )

            timestamp = timestamp + metadata[2]

        try:
            self.responseCode(200)
            self.contentType('application/x-javascript; charset=utf-8')

            if 'jsonp' in params:
                print "%s(" % (params['jsonp'][0])

            print "{start: %d, end: %d, step: %d, data: [\n%s\n]}" % (metadata[0], metadata[1], metadata[2], ',\n'.join(dataStrings))

            if 'jsonp' in params:
                print ');'

        except socket.error, e:
            pass
