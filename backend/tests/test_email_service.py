
import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.main import app
from src.infrastructure.email.email_service import EmailService


class TestEmailService(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_mock_console_email_send(self):
        """Verifica que o envio no modo padrão/mock funciona sem falhas."""
        service = EmailService()
        result = service.enviar_email(
            destinatario="candidato@teste.com",
            assunto="Teste de Assunto",
            corpo_html="<p>Conteúdo de teste</p>"
        )
        self.assertTrue(result)

    def test_recuperacao_senha_template(self):
        """Verifica se o e-mail de recuperação de senha contém o link e nome."""
        service = EmailService()
        with patch.object(service, "enviar_email", return_value=True) as mock_send:
            res = service.enviar_recuperacao_senha(
                destinatario="usuario@teste.com",
                nome="Ana Silva",
                link_redefinicao="https://recrutamento.empresa.com/auth?token=xyz123"
            )
            self.assertTrue(res)
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            dest, assunto, html, texto = args
            self.assertEqual(dest, "usuario@teste.com")
            self.assertIn("Redefinição de Palavra-passe", assunto)
            self.assertIn("Ana Silva", html)
            self.assertIn("https://recrutamento.empresa.com/auth?token=xyz123", html)

    def test_notificacao_candidatura_template(self):
        """Verifica se o e-mail de atualização de fase contém título e fase."""
        service = EmailService()
        with patch.object(service, "enviar_email", return_value=True) as mock_send:
            res = service.enviar_notificacao_candidatura(
                destinatario="candidato@teste.com",
                nome_candidato="Carlos Santos",
                titulo_vaga="Desenvolvedor Full Stack",
                nova_fase="Entrevista"
            )
            self.assertTrue(res)
            mock_send.assert_called_once()
            args, kwargs = mock_send.call_args
            dest, assunto, html, texto = args
            self.assertIn("Desenvolvedor Full Stack", assunto)
            self.assertIn("Carlos Santos", html)
            self.assertIn("Entrevista", html)

    @patch("smtplib.SMTP")
    def test_smtp_send_success(self, mock_smtp):
        """Verifica envio bem-sucedido via SMTP STARTTLS."""
        instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = instance

        service = EmailService(
            smtp_host="smtp.empresa.com",
            smtp_port=587,
            smtp_user="usuario_smtp",
            smtp_password="senha_secreta",
            from_email="noreply@empresa.com",
            use_tls=True
        )

        res = service.enviar_email("dest@teste.com", "Assunto", "<p>Corpo</p>")
        self.assertTrue(res)
        instance.starttls.assert_called_once()
        instance.login.assert_called_once_with("usuario_smtp", "senha_secreta")
        instance.sendmail.assert_called_once()

    @patch("smtplib.SMTP", side_effect=Exception("Falha na conexão SMTP"))
    def test_smtp_send_graceful_failure(self, mock_smtp):
        """Verifica que falha de rede/SMTP é capturada com segurança sem explodir a aplicação."""
        service = EmailService(
            smtp_host="smtp.empresa.com",
            smtp_port=587,
            smtp_user="user",
            smtp_password="pass"
        )
        res = service.enviar_email("dest@teste.com", "Assunto", "<p>Corpo</p>")
        self.assertFalse(res)

    def test_endpoint_recuperar_senha_dispatches_email(self):
        """Verifica se o endpoint /api/auth/recuperar-senha roda normalmente com background task."""
        resp = self.client.post("/api/auth/recuperar-senha", json={"email": "inexistente@empresa.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("message", resp.json())


if __name__ == "__main__":
    unittest.main()
