import json
import socket
import threading
import time
import unittest
from http.client import HTTPConnection

from arnold_api import ArnoldAPI


class ArnoldAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = ArnoldAPI()
        cls.app.load('IT\'S SHOWTIME\nROUTE "GET" "/hello/<name>"\nTALK TO THE HAND "hello"\nENOUGH TALK\nYOU HAVE BEEN TERMINATED')
        cls.server_thread = threading.Thread(target=cls.app.serve, kwargs={"port": 18765}, daemon=True)
        cls.server_thread.start()
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1", 18765), timeout=0.1): break
            except OSError: time.sleep(0.05)
        else: raise RuntimeError("test server did not start")

    def request(self, path):
        conn = HTTPConnection("127.0.0.1", 18765, timeout=3); conn.request("GET", path)
        response = conn.getresponse(); body = response.read(); conn.close(); return response.status, body

    def test_route_and_params(self):
        status, body = self.request("/hello/Arnold")
        self.assertEqual(status, 200); self.assertEqual(body, b"hello")

    def test_not_found(self):
        status, body = self.request("/missing")
        self.assertEqual(status, 404); self.assertEqual(json.loads(body), {"error": "not found"})


if __name__ == "__main__": unittest.main()
