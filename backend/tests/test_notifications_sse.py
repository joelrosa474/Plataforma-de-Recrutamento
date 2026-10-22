import unittest
from fastapi.testclient import TestClient

from src.main import app
from src.infrastructure.notifications.broadcaster import NotificationBroadcaster
from src.infrastructure.security.jwt_service import JWTService


class TestNotificationsSSE(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.broadcaster = NotificationBroadcaster()

    def test_broadcaster_subscribe_unsubscribe(self):
        """Verifica ciclo de vida de inscrição e cancelamento no broadcaster."""
        user_id = 99
        queue = self.broadcaster.subscribe(user_id)
        self.assertIn(user_id, self.broadcaster._subscribers)
        self.assertIn(queue, self.broadcaster._subscribers[user_id])

        self.broadcaster.unsubscribe(user_id, queue)
        self.assertNotIn(user_id, self.broadcaster._subscribers)

    def test_broadcaster_broadcast_delivery(self):
        """Verifica entrega de payload para fila do usuário inscrito."""
        user_id = 101
        queue = self.broadcaster.subscribe(user_id)
        payload = {"id": 1, "titulo": "Alerta", "mensagem": "Teste SSE"}

        self.broadcaster.broadcast(user_id, payload)
        self.assertFalse(queue.empty())
        item = queue.get_nowait()
        self.assertEqual(item["titulo"], "Alerta")

        self.broadcaster.unsubscribe(user_id, queue)

    def test_stream_without_token_returns_401(self):
        """Verifica que requisição SSE sem credenciais é rejeitada."""
        resp = self.client.get("/api/notificacoes/stream")
        self.assertEqual(resp.status_code, 401)

    def test_stream_with_invalid_token_returns_401(self):
        """Verifica que token inválido é rejeitado."""
        resp = self.client.get("/api/notificacoes/stream?token=invalid.jwt.token")
        self.assertEqual(resp.status_code, 401)


if __name__ == "__main__":
    unittest.main()
