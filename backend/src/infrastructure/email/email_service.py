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
    Suporta quatro modos operacionais configurados via ambiente:
    1. Brevo HTTP API (se BREVO_API_KEY configurado - ideal para nuvens como Render onde portas SMTP são bloqueadas)
    2. Resend HTTP API (se RESEND_API_KEY configurado)
    3. SMTP padrão (Gmail, SendGrid, Mailtrap, se portas 587/465 estiverem liberadas na rede)
    4. Console / Mock (fallback seguro para desenvolvimento e testes automatizados)
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
        brevo_api_key: Optional[str] = None,
    ):
        def _clean(val: Optional[str]) -> Optional[str]:
            if val is None:
                return None
            s = str(val).strip()
            return s if s else None

        self.smtp_host = _clean(smtp_host or os.getenv("SMTP_HOST"))
        raw_port = str(os.getenv("SMTP_PORT", "587")).strip()
        self.smtp_port = smtp_port or (int(raw_port) if raw_port.isdigit() else 587)
        self.smtp_user = _clean(smtp_user or os.getenv("SMTP_USER"))
        self.smtp_password = _clean(smtp_password or os.getenv("SMTP_PASSWORD"))
        self.from_email = _clean(from_email or os.getenv("SMTP_FROM_EMAIL")) or "noreply@recrutamento.local"
        self.from_name = _clean(from_name or os.getenv("SMTP_FROM_NAME")) or "Recrutamento RH"
        self.use_tls = use_tls if use_tls is not None else (os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1"))
        self.resend_api_key = _clean(resend_api_key or os.getenv("RESEND_API_KEY"))
        self.brevo_api_key = _clean(brevo_api_key or os.getenv("BREVO_API_KEY"))

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

        # Opção 1: Brevo HTTP API (Porta 443 HTTPS - Funciona perfeitamente no Render e nuvem sem bloqueio)
        if self.brevo_api_key:
            return self._enviar_via_brevo(destinatario, assunto, html_completo, texto_simples)

        # Opção 2: Resend HTTP API (Porta 443 HTTPS)
        if self.resend_api_key:
            sucesso = self._enviar_via_resend(destinatario, assunto, html_completo, texto_simples)
            if sucesso:
                return True
            if self.smtp_host and self.smtp_user and self.smtp_password:
                logger.warning("Falha no Resend API; tentando envio via SMTP padrão configurado...")
                return self._enviar_via_smtp(destinatario, assunto, html_completo, texto_simples)
            return False

        # Opção 3: SMTP padrão (Gmail, Outlook, etc. - Bloqueado em plataformas como Render/Free Tier)
        if self.smtp_host and self.smtp_user and self.smtp_password:
            return self._enviar_via_smtp(destinatario, assunto, html_completo, texto_simples)

        # Opção 4: Console / Mock (desenvolvimento e testes)
        logger.info(
            f"[EMAIL MOCK/CONSOLE] De: '{self.from_name}' <{self.from_email}> | "
            f"Para: {destinatario} | Assunto: '{assunto}'"
        )
        return True

    def _enviar_via_brevo(self, destinatario: str, assunto: str, html: str, texto: str) -> bool:
        """Envia e-mail através da API REST do Brevo via HTTPS (Porta 443 - compatível com Render)."""
        try:
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "api-key": self.brevo_api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
            payload = {
                "sender": {"name": self.from_name, "email": self.from_email},
                "to": [{"email": destinatario}],
                "subject": assunto,
                "htmlContent": html,
                "textContent": texto,
            }
            with httpx.Client(timeout=12.0) as client:
                resp = client.post(url, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    logger.info(f"E-mail enviado com sucesso via Brevo API para {destinatario}")
                    return True
                else:
                    logger.error(f"Erro ao enviar e-mail via Brevo API ({resp.status_code}): {resp.text}")
                    return False
        except Exception as e:
            logger.error(f"Falha de conexão com a API do Brevo: {e}")
            return False

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
                    logger.error(
                        f"Erro ao enviar e-mail via Resend ({resp.status_code}): {resp.text}. "
                        "Atenção: No plano gratuito do Resend sem domínio verificado, use 'SMTP_FROM_EMAIL=onboarding@resend.dev' "
                        "e envie apenas para o e-mail da sua conta Resend, ou configure SMTP_HOST/SMTP_USER/SMTP_PASSWORD para envio irrestrito."
                    )
                    return False
        except Exception as e:
            logger.error(f"Falha de conexão com Resend API: {e}")
            return False

    def _enviar_via_smtp(self, destinatario: str, assunto: str, html: str, texto: str) -> bool:
        try:
            from email.header import Header

            msg = MIMEMultipart("alternative")
            msg["Subject"] = Header(assunto, "utf-8")
            msg["From"] = f"{Header(self.from_name, 'utf-8')} <{self.from_email}>"
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
        """Notifica o candidato sobre atualização de fase no processo seletivo com conteúdo personalizado por fase."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        link_portal = f"{frontend_url}/candidate/applications"

        if nova_fase == "Entrevista":
            assunto = f"Parabéns! Foi selecionado(a) para a fase de Entrevista: {titulo_vaga}"
            titulo_cabecalho = f"Parabéns, {nome_candidato}!"
            cor_destaque = "#2563eb"
            badge_cor = "background-color: #dbeafe; color: #1e40af;"
            mensagem_fase = (
                f"<p style='font-size: 16px; color: #1e293b;'>O seu perfil destacou-se e foi <strong>selecionado(a) para a fase de Entrevista</strong> na vaga <strong>{titulo_vaga}</strong>!</p>"
                "<p>A equipa de recrutamento entrará em contacto ou disponibilizará o link e data da entrevista diretamente na plataforma. Aceda ao portal para acompanhar todas as atualizações.</p>"
            )
            texto_botao = "Aceder às Minhas Candidaturas"
        elif nova_fase == "Contratado":
            assunto = f"Parabéns! Foi contratado(a) para a vaga: {titulo_vaga}"
            titulo_cabecalho = f"Excelente notícia, {nome_candidato}!"
            cor_destaque = "#10b981"
            badge_cor = "background-color: #d1fae5; color: #065f46;"
            mensagem_fase = (
                f"<p style='font-size: 16px; color: #1e293b;'>🎉 Temos o enorme prazer de informar que foi <strong>aprovado(a) e contratado(a)</strong> para a vaga <strong>{titulo_vaga}</strong>!</p>"
                "<p>A empresa responsável entrará em contacto muito em breve para alinhar os detalhes da sua contratação e os passos de acolhimento. Parabéns por esta grande conquista!</p>"
            )
            texto_botao = "Ver Detalhes da Contratação"
        elif nova_fase == "Reprovado":
            assunto = f"Atualização sobre a sua candidatura: {titulo_vaga}"
            titulo_cabecalho = f"Olá, {nome_candidato}"
            cor_destaque = "#64748b"
            badge_cor = "background-color: #f1f5f9; color: #475569;"
            mensagem_fase = (
                f"<p>Agradecemos sinceramente o seu interesse e o tempo dedicado ao candidatar-se à vaga <strong>{titulo_vaga}</strong>.</p>"
                "<p>Após avaliação cuidadosa, a empresa decidiu prosseguir com outros perfis cujas competências atendem mais diretamente às necessidades operacionais imediatas para esta posição.</p>"
                "<p>O seu currículo continuará registado no nosso <strong>Banco de Talentos</strong>, e novas vagas recomendadas serão disponibilizadas no seu painel.</p>"
            )
            texto_botao = "Explorar Outras Vagas Disponíveis"
            link_portal = f"{frontend_url}/candidate/dashboard"
        else:
            assunto = f"Atualização da sua candidatura: {titulo_vaga}"
            titulo_cabecalho = f"Olá, {nome_candidato}!"
            cor_destaque = "#2563eb"
            badge_cor = "background-color: #e0e7ff; color: #3730a3;"
            mensagem_fase = (
                f"<p>A sua candidatura para a vaga <strong>{titulo_vaga}</strong> teve uma atualização de estado.</p>"
            )
            texto_botao = "Acompanhar Candidatura"

        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">{titulo_cabecalho}</h2>
        {mensagem_fase}
        
        <div style="background-color: #f8fafc; border-left: 4px solid {cor_destaque}; padding: 16px; margin: 24px 0; border-radius: 6px;">
          <p style="margin: 0; font-size: 13px; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">Novo Estado no Processo:</p>
          <p style="margin: 6px 0 0; font-size: 18px; font-weight: 700;">
            <span style="display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: 700; {badge_cor}">{nova_fase}</span>
          </p>
        </div>

        <div style="text-align: center; margin: 30px 0;">
          <a href="{link_portal}" class="btn" target="_blank">{texto_botao}</a>
        </div>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nA sua candidatura para '{titulo_vaga}' foi atualizada para: {nova_fase}.\nAceda ao portal para acompanhar: {link_portal}"
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)

    def enviar_convite_entrevista(self, destinatario: str, nome_candidato: str, titulo_vaga: str, data_hora: str, link: Optional[str], notas: Optional[str]) -> bool:
        """Envia a confirmação imediata do agendamento de entrevista."""
        assunto = f"Entrevista agendada: {titulo_vaga}"
        link_html = f'<p><a href="{link}" class="btn" target="_blank">Entrar na entrevista</a></p>' if link else ""
        notas_html = f"<p><strong>Informações da empresa:</strong><br>{notas}</p>" if notas else ""
        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">Olá, {nome_candidato}!</h2>
        <p>A sua entrevista para a vaga <strong>{titulo_vaga}</strong> foi agendada.</p>
        <div style="background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 16px; margin: 20px 0; border-radius: 4px;"><strong>Data e hora:</strong> {data_hora}</div>
        {link_html}{notas_html}
        <p>Confirme os detalhes no portal e prepare-se para a conversa. Boa sorte!</p>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nA entrevista para '{titulo_vaga}' foi agendada para {data_hora}." + (f"\nLink: {link}" if link else "") + (f"\nInformações: {notas}" if notas else "")
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)
