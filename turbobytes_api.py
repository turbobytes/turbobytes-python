import hashlib
import hmac
from datetime import datetime
import httplib2, json
from urllib import urlencode

class TurboBytesAPI(object):
    def __init__(self, api_key, api_secret, server="https://api.turbobytes.com", use_local_time=True):
        """
        Contact Turbobytes support for api_key and api_secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.http = httplib2.Http() #Need this cause httplib2 does not know PositiveSSL
        self.server = server
        self.use_local_time = use_local_time

    def generate_auth_headers(self):
        """
        Returns the values for X-TB-Timestamp and Authentication headers
        """
        if self.use_local_time:
            timestamp = datetime.utcnow().isoformat()
        else:
            timestamp = self.get_server_time()
        document = "%s:%s" %(self.api_key, timestamp)
        signature = hmac.new(self.api_secret, document, hashlib.sha1).digest().encode("base64")[:-1]
        auth = "%s:%s" %(self.api_key, signature)
        return timestamp, auth

    def get(self, path, needs_auth=True):
        """
        Makes a GET request
        """
        return self.request("GET", path, needs_auth=needs_auth)

    def request(self, method, path, data=None, needs_auth=True):
        """
        Makes a request to the api
        """
        endpoint = self.server + path
        headers = {}
        if needs_auth:
            headers["X-TB-Timestamp"], headers["Authorization"] = self.generate_auth_headers()
        if method in ["POST", "PUT"]:
            r, c = self.http.request(endpoint, method, data, headers=headers)
        else:
            r, c = self.http.request(endpoint, "GET", headers=headers)
        if r["status"] != "200":
            f = open("/tmp/err.html", "w")
            f.write(c)
            f.close()
            raise Exception(r["status"], r, c)
        else:
            return json.loads(c)


    def post(self, path, data, needs_auth=True):
        """
        Makes a POST request
        """
        return self.request("POST", path, data=data, needs_auth=needs_auth)

    def put(self, path, data, needs_auth=True):
        """
        Makes a PUT request
        """
        return self.request("PUT", path, data=data, needs_auth=needs_auth)


    def get_server_time(self):
        """
        Gets timestamp string from the server. Usefull if timegap is over 15 mins between server and client
        """
        return self.get("/api/now/", needs_auth=False)["timestamp"]

    def who_am_i(self):
        """
        Returns username of current user
        """
        return self.get("/api/whoami/")["username"]

    def list_all_zones(self):
        """
        Gets all zones owned by the current user
        """
        return self.get("/api/zones/")

    def get_zone(self, zoneid):
        """
        Gets a zone identified by zoneid
        """
        return self.get("/api/zone/%s/" %(zoneid))

    def get_report(self, zoneid, day, byday=False):
        """
        Gets Zone reports
        day format is string yyyy-mm-dd for day report and yyyy-mm for month report
        """
        if byday:
            qs = "?byday=true"
        else:
            qs = ""
        uri = "/".join(day.split("-"))
        path = "/api/zone/%s/report/%s/%s" %(zoneid, "/".join(day.split("-")), qs)
        return self.get(path)

    def get_log_link(self, zoneid, day):
        """
        Gets link to download access log for zone. If logging is enabled.
        day format is string yyyy-mm-dd
        """
        path = "/api/zone/%s/log/%s/" %(zoneid, day)
        return self.get(path)

    def purge(self, zoneid, files):
        """
        Purges the list files for zoneid
        """
        payload = json.dumps({"files": files})
        path = "/api/zone/%s/purge/" %(zoneid)
        print payload
        return self.post(path, payload)

    def latest_purges(self, zoneid):
        path = "/api/zone/%s/purges/" %(zoneid)
        return self.get(path)

