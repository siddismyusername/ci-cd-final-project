"""Functional tests for the counter REST API."""

from unittest import TestCase

from service import app
from service.routes import reset_counters


class CounterServiceTests(TestCase):
    """Test the API through Flask's HTTP test client."""

    @classmethod
    def setUpClass(cls):
        app.testing = True

    @classmethod
    def tearDownClass(cls):
        app.testing = False

    def setUp(self):
        reset_counters()
        self.client = app.test_client()

    def test_index(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["message"], "Hit Counter Service")

    def test_health(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["status"], "OK")

    def test_list_empty(self):
        response = self.client.get("/counters")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), [])

    def test_create(self):
        response = self.client.post("/counters/foo")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json(), {"name": "foo", "counter": 0})
        self.assertTrue(response.headers["Location"].endswith("/counters/foo"))

    def test_duplicate_create_conflicts(self):
        self.client.post("/counters/foo")
        response = self.client.post("/counters/foo")
        self.assertEqual(response.status_code, 409)

    def test_list_existing_counters(self):
        self.client.post("/counters/zeta")
        self.client.post("/counters/alpha")
        response = self.client.get("/counters")
        self.assertEqual(
            response.get_json(),
            [{"name": "alpha", "counter": 0}, {"name": "zeta", "counter": 0}],
        )

    def test_read(self):
        self.client.post("/counters/foo")
        response = self.client.get("/counters/foo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["counter"], 0)

    def test_read_missing(self):
        response = self.client.get("/counters/unknown")
        self.assertEqual(response.status_code, 404)

    def test_increment(self):
        self.client.post("/counters/foo")
        response = self.client.put("/counters/foo")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["counter"], 1)

    def test_increment_twice(self):
        self.client.post("/counters/foo")
        self.client.put("/counters/foo")
        response = self.client.put("/counters/foo")
        self.assertEqual(response.get_json()["counter"], 2)

    def test_increment_missing(self):
        response = self.client.put("/counters/unknown")
        self.assertEqual(response.status_code, 404)

    def test_delete(self):
        self.client.post("/counters/foo")
        response = self.client.delete("/counters/foo")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.client.get("/counters/foo").status_code, 404)

    def test_delete_is_idempotent(self):
        response = self.client.delete("/counters/unknown")
        self.assertEqual(response.status_code, 204)
