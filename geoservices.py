import json, signal
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
import urllib.parse
import tornado.gen

adrs_request_url = "https://geocoder.api.here.com/6.2/geocode.json?app_id=pb0CIzZpApR3GtVA0b0R&app_code=mZY9zSdqy3o46PG0ecnokQ&searchtext="
coord_request_url = "https://reverse.geocoder.api.here.com/6.2/reversegeocode.json?app_id=pb0CIzZpApR3GtVA0b0R&app_code=mZY9zSdqy3o46PG0ecnokQ&mode=retrieveAddresses&prox="

class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header("Content-Type", "text/html")
        self.render("geoindex.html")

class FetchCoordHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        # encode user input properly
        address_string = urllib.parse.quote(self.get_argument("address"))
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(adrs_request_url + address_string, method="GET")
        response_json = json.loads(response.body)

        self.set_header("Content-Type", "application/json")

        try:
            lat = response_json["Response"]["View"][0]["Result"][0]["Location"]["NavigationPosition"][0]["Latitude"]
            lon = response_json["Response"]["View"][0]["Result"][0]["Location"]["NavigationPosition"][0]["Longitude"]
            self.write(json.dumps({"success": True, "lat": lat, "lon": lon}))
        except Exception as e:
        	## Backup service to be invoked
        	## Google geocoding service
            print(e)
            self.write(json.dumps({"success": False}))

class FetchAdrsHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        # encode user input properly
        address_string = urllib.parse.quote(self.get_argument("address"))
        http_client = AsyncHTTPClient()
        response = yield http_client.fetch(coord_request_url + address_string, method="GET")
        response_json = json.loads(response.body)

        self.set_header("Content-Type", "application/json")

        try:
            adrs = response_json["Response"]["View"][0]["Result"][0]["Location"]["Address"]
            self.write(json.dumps({"success": True, "Address": adrs}))
        except Exception as e:
        	## Backup service to be invoked
        	## Google geocoding service        	
            print(e)
            self.write(json.dumps({"success": False}))
            tornado.ioloop.IOLoop.instance().stop()

app = tornado.web.Application([
        (r"/", RootHandler),
        (r"/fetchCoords", FetchCoordHandler),
        (r"/fetchAdrs", FetchAdrsHandler),
])

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app.listen(80)
    tornado.ioloop.IOLoop.instance().start()