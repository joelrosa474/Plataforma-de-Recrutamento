import unittest

from fastapi.testclient import TestClient

from src.main import app


class TestProductionHardening(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_check_has_expected_shape(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "ok")
        self.assertIn("API de Recrutamento", payload["message"])

    def test_security_headers_present_on_response(self):
        response = self.client.get("/")

        self.assertIn("X-Request-Id", response.headers)
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")


if __name__ == "__main__":
    unittest.main()
