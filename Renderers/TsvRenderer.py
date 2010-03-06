import Renderer, rrdtool

class TsvRenderer (Renderer.Renderer):
    def render (self, startTime, endTime, params):

        (metadata, titles, data) = rrdtool.fetch(
            self.rrdFile, 
            "--start", str(startTime),
            "--end", str(endTime), 
            "AVERAGE"
        )

        try:
            self.responseCode(200)
            self.contentType('text/plain; charset=utf-8')

            print "Timestamp\tWatts\tTemp"

            timestamp = metadata[0]
            for item in data:

                first = item[0]
                if first == None:
                    first = 0;

                second = item[1]
                if second == None:
                    second = 0;

                print "%d\t%f\t%f" % (timestamp, first, second)

                timestamp = timestamp + metadata[2]

        except socket.error, e:
            pass
