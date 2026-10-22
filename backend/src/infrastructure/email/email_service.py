import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import httpx

from src.application.ports.email_service_port import EmailServicePort

logger = logging.getLogger("rh_api")


class EmailService(EmailServicePort):
    """
    Serviço de envio de e-mails transacionais.
    Suporta três modos operacionais configurados via ambiente:
    1. Resend API HTTP (se RESEND_API_KEY estiver configurado)
    2. SMTP padrão (Gmail, SendGrid, Mailtrap, Amazon SES, etc., se SMTP_HOST estiver configurado)
    3. Console / Mock (fallback seguro para desenvolvimento e testes automatizados)
    """

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        use_tls: bool = True,
        resend_api_key: Optional[str] = None,
    ):
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")
        self.from_email = from_email or os.getenv("SMTP_FROM_EMAIL", "noreply@recrutamento.local")
        self.from_name = from_name or os.getenv("SMTP_FROM_NAME", "Recrutamento RH")
        self.use_tls = use_tls if use_tls is not None else (os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1"))
        self.resend_api_key = resend_api_key or os.getenv("RESEND_API_KEY")

    def _render_layout(self, titulo: str, conteudo_html: str) -> str:
        """Gera o invólucro HTML padrão com estilo corporativo moderno e responsivo."""
        return f"""<!DOCTYPE html>
<html lang="pt">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{titulo}</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      background-color: #f1f5f9;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
    }}
    .wrapper {{
      width: 100%;
      background-color: #f1f5f9;
      padding: 40px 10px;
    }}
    .container {{
      max-width: 580px;
      margin: 0 auto;
      background-color: #ffffff;
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
    }}
    .header {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
      padding: 30px;
      text-align: center;
      color: #ffffff;
    }}
    .header h1 {{
      margin: 0;
      font-size: 22px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .header p {{
      margin: 6px 0 0;
      font-size: 13px;
      color: #94a3b8;
    }}
    .content {{
      padding: 36px 32px;
      line-height: 1.6;
      font-size: 15px;
    }}
    .btn {{
      display: inline-block;
      background-color: #2563eb;
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 600;
      font-size: 15px;
      padding: 13px 28px;
      border-radius: 8px;
      margin: 24px 0;
      text-align: center;
    }}
    .footer {{
      background-color: #f8fafc;
      padding: 24px 32px;
      text-align: center;
      font-size: 12px;
      color: #64748b;
      border-top: 1px solid #e2e8f0;
    }}
    .footer p {{
      margin: 4px 0;
    }}
    .badge {{
      display: inline-block;
      background-color: #e0e7ff;
      color: #3730a3;
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 13px;
    }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="container">
      <div class="header">
        <h1>{self.from_name}</h1>
        <p>Plataforma Inteligente de Recrutamento & Seleção</p>
      </div>
      <div class="content">
        {conteudo_html}
      </div>
      <div class="footer">
        <p>Este é um e-mail automático gerado pelo sistema. Por favor, não responda diretamente a esta mensagem.</p>
        <p>&copy; Plataforma de Recrutamento RH. Todos os direitos reservados.</p>
      </div>
    </div>
  </div>
</body>
</html>"""

    def enviar_email(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: Optional[str] = None
    ) -> bool:
        """Envia e-mail selecionando o provedor disponível (Resend -> SMTP -> Console fallback)."""
        html_completo = self._render_layout(assunto, corpo_html)
        texto_simples = corpo_texto or "Por favor, visualize este e-mail num cliente compatível com HTML."

        # Opção 1: Resend HTTP API
        if self.resend_api_key:
            return self._enviar_via_resend(destinatario, assunto, html_completo, texto_simples)

        # Opção 2: SMTP padrão
        if self.smtp_host and self.smtp_user and self.smtp_password:
            return self._enviar_via_smtp(destinatario, assunto, html_completo, texto_simples)

        # Opção 3: Console / Mock (desenvolvimento e testes)
        logger.info(
            f"[EMAIL MOCK/CONSOLE] De: '{self.from_name}' <{self.from_email}> | "
            f"Para: {destinatario} | Assunto: '{assunto}'"
        )
        return True

    def _enviar_via_resend(self, destinatario: str, assunto: str, html: str, texto: str) -> bool:
        try:
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [destinatario],
                "subject": assunto,
                "html": html,
                "text": texto
            }
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    logger.info(f"E-mail enviado com sucesso via Resend para {destinatario}")
                    return True
                else:
                    logger.error(f"Erro ao enviar e-mail via Resend ({resp.status_code}): {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Falha de conexão com Resend API: {e}")
            return False

    def _enviar_via_smtp(self, destinatario: str, assunto: str, html: str, texto: str) -> bool:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = assunto
            msg["From"] = f"{self.from_name} <{self.from_email}>"
            msg["To"] = destinatario

            part_text = MIMEText(texto, "plain", "utf-8")
            part_html = MIMEText(html, "html", "utf-8")
            msg.attach(part_text)
            msg.attach(part_html)

            if self.smtp_port == 465:
                # SSL direto
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=10) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, [destinatario], msg.as_string())
            else:
                # STARTTLS
                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                    if self.use_tls:
                        server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                    server.sendmail(self.from_email, [destinatario], msg.as_string())

            logger.info(f"E-mail enviado com sucesso via SMTP para {destinatario}")
            return True
        except Exception as e:
            logger.error(f"Falha no envio de e-mail via SMTP ({self.smtp_host}:{self.smtp_port}): {e}")
            return False

    def enviar_recuperacao_senha(
        self,
        destinatario: str,
        nome: str,
        link_redefinicao: str
    ) -> bool:
        """Gera e envia o e-mail de recuperação de senha com botão de ação seguro."""
        assunto = "Redefinição de Palavra-passe - Plataforma de Recrutamento"
        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">Olá, {nome or 'Utilizador'}!</h2>
        <p>Recebemos uma solicitação para redefinir a palavra-passe da sua conta na <strong>Plataforma de Recrutamento RH</strong>.</p>
        <p>Clique no botão abaixo para escolher uma nova palavra-passe segura:</p>
        
        <div style="text-align: center; margin: 30px 0;">
          <a href="{link_redefinicao}" class="btn" target="_blank">Redefinir Minha Palavra-passe</a>
        </div>

        <p style="font-size: 13px; color: #64748b;">
          Se o botão não funcionar, copie e cole o link abaixo diretamente no seu navegador:<br>
          <a href="{link_redefinicao}" style="color: #2563eb; word-break: break-all;">{link_redefinicao}</a>
        </p>

        <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 24px 0;" />

        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 0;">
          🔒 <strong>Segurança:</strong> Se você não solicitou esta redefinição, nenhuma ação é necessária. 
          A sua conta continua segura e este link expirará automaticamente.
        </p>
        """
        corpo_texto = f"""Olá {nome},\n\nRecebemos um pedido de redefinição de palavra-passe. Aceda ao link para continuar:\n{link_redefinicao}\n\nSe não solicitou, ignore esta mensagem."""
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)

    def enviar_notificacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nova_fase: str
    ) -> bool:
        """Notifica o candidato sobre atualização de fase no processo seletivo."""
        assunto = f"Atualização da sua candidatura: {titulo_vaga}"
        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">Olá, {nome_candidato}!</h2>
        <p>Temos novidades sobre o seu processo seletivo para a vaga <strong>{titulo_vaga}</strong>.</p>
        
        <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 16px; margin: 20px 0; border-radius: 4px;">
          <p style="margin: 0; font-size: 14px; color: #475569;">A sua candidatura avançou para:</p>
          <p style="margin: 6px 0 0; font-size: 18px; font-weight: 700; color: #1e293b;">
            <span class="badge">{nova_fase}</span>
          </p>
        </div>

        <p>Aceda ao portal para acompanhar todos os detalhes e mensagens dos recrutadores:</p>

        <div style="text-align: center; margin: 25px 0;">
          <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/candidate/applications" class="btn" target="_blank">Acompanhar Candidatura</a>
        </div>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nA sua candidatura para '{titulo_vaga}' avançou para a fase: {nova_fase}.\nAceda ao portal para acompanhar."
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)
