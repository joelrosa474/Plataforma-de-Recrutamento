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

    def enviar_boas_vindas(
        self,
        destinatario: str,
        nome: str,
        tipo_perfil: str
    ) -> bool:
        """Envia e-mail de boas-vindas da plataforma É Salú ao novo utilizador com descrições das funcionalidades."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        nome_exibicao = (nome or "").strip() or "Utilizador"
        eh_empresa = (tipo_perfil or "").strip().lower() == "empresa"

        if eh_empresa:
            assunto = "Bem-vindo(a) à É Salú - Transforme o Recrutamento da sua Empresa!"
            link_acao = f"{frontend_url}/company/jobs"
            texto_botao = "Publicar Primeira Vaga"
            conteudo_especifico = """
            <p style="font-size: 16px; color: #1e293b; line-height: 1.6;">
              É com enorme satisfação que damos as boas-vindas à sua organização na <strong>É Salú</strong>!
            </p>
            <p style="color: #475569; line-height: 1.6;">
              A <strong>É Salú</strong> é a plataforma moderna concebida para aproximar empresas visionárias dos melhores profissionais do mercado, combinando velocidade, assertividade e inteligência artificial avançada.
            </p>

            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; padding: 20px; margin: 24px 0; border-radius: 8px;">
              <h3 style="margin-top: 0; color: #0f172a; font-size: 15px;">Recursos exclusivos para a sua empresa na É Salú:</h3>
              <ul style="padding-left: 20px; margin: 10px 0; color: #334155; font-size: 14px; line-height: 1.8;">
                <li><strong>Publicação Ágil de Vagas:</strong> Crie oportunidades nas modalidades Presencial, Híbrida ou Remota com requisitos claros.</li>
                <li><strong>Triagem Inteligente com Gemini IA:</strong> Análise instantânea de currículos em PDF com pontuação de afinidade (<em>Match Score</em>) e justificativa semântica.</li>
                <li><strong>Funil Completo do Processo Seletivo (ATS):</strong> Mova candidatos entre Triagem, Entrevista e Contratado com notificações automáticas.</li>
                <li><strong>Geração Automática de Roteiros de Entrevista:</strong> A IA formula perguntas técnicas e situacionais personalizadas para o perfil de cada candidato.</li>
                <li><strong>Busca Ativa no Banco de Talentos:</strong> Pesquise diretamente profissionais qualificados por área, competências e localização.</li>
              </ul>
            </div>

            <p style="font-size: 14px; color: #64748b;">
              O próximo grande talento da sua equipa pode estar a um clique. Publique a sua primeira vaga e comece a receber candidaturas triadas.
            </p>
            """
        else:
            assunto = "Bem-vindo(a) à É Salú - O seu próximo passo profissional começa aqui!"
            link_acao = f"{frontend_url}/candidate/profile"
            texto_botao = "Completar Meu Perfil e Currículo"
            conteudo_especifico = """
            <p style="font-size: 16px; color: #1e293b; line-height: 1.6;">
              Temos o prazer de lhe dar as boas-vindas à <strong>É Salú</strong>! A sua conta foi registada com sucesso.
            </p>
            <p style="color: #475569; line-height: 1.6;">
              A <strong>É Salú</strong> é a sua nova ponte para o mercado de trabalho. Aqui, conectamos as suas experiências e ambições a empresas de destaque, valorizando o seu potencial com tecnologia de ponta.
            </p>

            <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #10b981; padding: 20px; margin: 24px 0; border-radius: 8px;">
              <h3 style="margin-top: 0; color: #0f172a; font-size: 15px;">Como a É Salú impulsiona a sua carreira:</h3>
              <ul style="padding-left: 20px; margin: 10px 0; color: #334155; font-size: 14px; line-height: 1.8;">
                <li><strong>Vagas Recomendadas para Si:</strong> Algoritmos inteligentes indicam oportunidades altamente compatíveis com o seu histórico.</li>
                <li><strong>Triagem Transparente por IA:</strong> Saiba em tempo real o seu nível de afinidade com os requisitos das vagas a que se candidata.</li>
                <li><strong>Acompanhamento Passo a Passo:</strong> Notificações imediatas por e-mail quando a sua candidatura avança para Entrevista ou Contratação.</li>
                <li><strong>Destaque no Banco de Talentos:</strong> Permita que empresas e recrutadores encontrem o seu perfil proativamente.</li>
              </ul>
            </div>

            <div style="background-color: #ecfdf5; border: 1px dashed #6ee7b7; padding: 14px; margin: 20px 0; border-radius: 6px;">
              <p style="margin: 0; font-size: 13px; color: #065f46;">
                💡 <strong>Dica para se destacar:</strong> Complete o seu perfil com as suas principais competências e carregue o seu currículo em PDF. Candidatos com perfil completo recebem 3x mais contactos de recrutadores!
              </p>
            </div>
            """

        corpo_html = f"""
        <div style="text-align: center; margin-bottom: 24px;">
          <h2 style="color: #0f172a; margin: 0 0 8px 0; font-size: 24px;">Bem-vindo(a) à É Salú, {nome_exibicao}!</h2>
          <span style="display: inline-block; padding: 4px 12px; border-radius: 6px; font-weight: 700; font-size: 12px; background-color: #e0e7ff; color: #3730a3;">Perfil: {tipo_perfil}</span>
        </div>

        {conteudo_especifico}

        <div style="text-align: center; margin: 32px 0;">
          <a href="{link_acao}" class="btn" target="_blank">{texto_botao}</a>
        </div>

        <p style="font-size: 13px; color: #64748b; text-align: center; margin-top: 24px; border-top: 1px solid #f1f5f9; padding-top: 16px;">
          Estamos aqui para ajudar em cada etapa do seu caminho. Desejamos-lhe as maiores felicidades e muito sucesso na <strong>É Salú</strong>!
        </p>
        """

        corpo_texto = f"""Bem-vindo(a) à É Salú, {nome_exibicao}!\n\nA sua conta de {tipo_perfil} foi criada com sucesso na plataforma É Salú.\nAceda ao portal e dê o próximo passo:\n{link_acao}"""

        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)

    def enviar_confirmacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nome_empresa: Optional[str] = None
    ) -> bool:
        """Envia confirmação imediata ao candidato de que a candidatura foi recebida com sucesso."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        link_portal = f"{frontend_url}/candidate/applications"
        empresa_rotulo = (nome_empresa or "").strip() or "Empresa Recrutadora"

        assunto = f"Candidatura recebida: {titulo_vaga} - {empresa_rotulo}"
        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">Olá, {nome_candidato}!</h2>
        <p>A sua candidatura para a vaga <strong>{titulo_vaga}</strong> na empresa <strong>{empresa_rotulo}</strong> foi submetida com sucesso!</p>
        
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; padding: 18px; margin: 24px 0; border-radius: 8px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 4px 0; color: #64748b; width: 150px;"><strong>Empresa Recrutadora:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 700;">{empresa_rotulo}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Vaga:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 600;">{titulo_vaga}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Estado Inicial:</strong></td>
              <td style="padding: 4px 0;"><span style="display: inline-block; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 13px; background-color: #fef3c7; color: #92400e;">Triagem</span></td>
            </tr>
          </table>
        </div>

        <p>O seu currículo já está disponível para análise pela equipa da <strong>{empresa_rotulo}</strong> e a nossa triagem inteligente já iniciou o processamento.</p>

        <div style="text-align: center; margin: 30px 0;">
          <a href="{link_portal}" class="btn" target="_blank">Acompanhar Minhas Candidaturas</a>
        </div>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nA sua candidatura para '{titulo_vaga}' na empresa {empresa_rotulo} foi submetida com sucesso.\nAceda ao portal para acompanhar: {link_portal}"
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)

    def enviar_notificacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nova_fase: str,
        nome_empresa: Optional[str] = None
    ) -> bool:
        """Notifica o candidato sobre atualização de fase no processo seletivo com conteúdo personalizado por fase e empresa recrutadora."""
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        link_portal = f"{frontend_url}/candidate/applications"
        empresa_rotulo = (nome_empresa or "").strip() or "Empresa Recrutadora"

        if nova_fase == "Entrevista":
            assunto = f"Parabéns! Foi selecionado(a) para a fase de Entrevista: {titulo_vaga} - {empresa_rotulo}"
            titulo_cabecalho = f"Parabéns, {nome_candidato}!"
            cor_destaque = "#2563eb"
            badge_cor = "background-color: #dbeafe; color: #1e40af;"
            mensagem_fase = (
                f"<p style='font-size: 16px; color: #1e293b;'>O seu perfil destacou-se e foi <strong>selecionado(a) para a fase de Entrevista</strong> na vaga <strong>{titulo_vaga}</strong> da empresa <strong>{empresa_rotulo}</strong>!</p>"
                f"<p>A equipa de recrutamento da <strong>{empresa_rotulo}</strong> entrará em contacto ou disponibilizará o link e a data da entrevista diretamente na plataforma. Aceda ao portal para acompanhar todas as atualizações.</p>"
            )
            texto_botao = "Aceder às Minhas Candidaturas"
        elif nova_fase == "Contratado":
            assunto = f"Parabéns! Foi contratado(a) para a vaga: {titulo_vaga} - {empresa_rotulo}"
            titulo_cabecalho = f"Excelente notícia, {nome_candidato}!"
            cor_destaque = "#10b981"
            badge_cor = "background-color: #d1fae5; color: #065f46;"
            mensagem_fase = (
                f"<p style='font-size: 16px; color: #1e293b;'>🎉 Temos o enorme prazer de informar que foi <strong>aprovado(a) e contratado(a)</strong> para a vaga <strong>{titulo_vaga}</strong> na empresa <strong>{empresa_rotulo}</strong>!</p>"
                f"<p>A equipa da <strong>{empresa_rotulo}</strong> entrará em contacto muito em breve para alinhar os detalhes da sua contratação e os passos de acolhimento. Parabéns por esta grande conquista!</p>"
            )
            texto_botao = "Ver Detalhes da Contratação"
        elif nova_fase == "Reprovado":
            assunto = f"Atualização sobre a sua candidatura: {titulo_vaga} - {empresa_rotulo}"
            titulo_cabecalho = f"Olá, {nome_candidato}"
            cor_destaque = "#64748b"
            badge_cor = "background-color: #f1f5f9; color: #475569;"
            mensagem_fase = (
                f"<p>Agradecemos sinceramente o seu interesse e o tempo dedicado ao candidatar-se à vaga <strong>{titulo_vaga}</strong> na empresa <strong>{empresa_rotulo}</strong>.</p>"
                f"<p>Após avaliação cuidadosa, a equipa de recrutamento da <strong>{empresa_rotulo}</strong> decidiu prosseguir com outros perfis cujas competências atendem mais diretamente às necessidades operacionais imediatas para esta posição.</p>"
                "<p>O seu currículo continuará registado no nosso <strong>Banco de Talentos</strong>, e novas vagas recomendadas serão disponibilizadas no seu painel.</p>"
            )
            texto_botao = "Explorar Outras Vagas Disponíveis"
            link_portal = f"{frontend_url}/candidate/dashboard"
        else:
            assunto = f"Atualização da sua candidatura: {titulo_vaga} - {empresa_rotulo}"
            titulo_cabecalho = f"Olá, {nome_candidato}!"
            cor_destaque = "#2563eb"
            badge_cor = "background-color: #e0e7ff; color: #3730a3;"
            mensagem_fase = (
                f"<p>A sua candidatura para a vaga <strong>{titulo_vaga}</strong> na empresa <strong>{empresa_rotulo}</strong> teve uma atualização de estado.</p>"
            )
            texto_botao = "Acompanhar Candidatura"

        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">{titulo_cabecalho}</h2>
        {mensagem_fase}
        
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid {cor_destaque}; padding: 18px; margin: 24px 0; border-radius: 8px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 4px 0; color: #64748b; width: 150px;"><strong>Empresa Recrutadora:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 700;">{empresa_rotulo}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Vaga:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 600;">{titulo_vaga}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Estado Atual:</strong></td>
              <td style="padding: 4px 0;"><span style="display: inline-block; padding: 3px 10px; border-radius: 6px; font-weight: 700; font-size: 13px; {badge_cor}">{nova_fase}</span></td>
            </tr>
          </table>
        </div>

        <div style="text-align: center; margin: 30px 0;">
          <a href="{link_portal}" class="btn" target="_blank">{texto_botao}</a>
        </div>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nEmpresa: {empresa_rotulo}\nVaga: {titulo_vaga}\nEstado: {nova_fase}\n\nAceda ao portal para acompanhar: {link_portal}"
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)

    def enviar_convite_entrevista(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        data_hora: str,
        link: Optional[str],
        notas: Optional[str],
        nome_empresa: Optional[str] = None
    ) -> bool:
        """Envia a confirmação imediata do agendamento de entrevista incluindo a empresa recrutadora."""
        empresa_rotulo = (nome_empresa or "").strip() or "Empresa Recrutadora"
        assunto = f"Entrevista agendada: {titulo_vaga} - {empresa_rotulo}"
        link_html = f'<p style="margin-top: 15px;"><a href="{link}" class="btn" target="_blank">Aceder à Sala da Entrevista</a></p>' if link else ""
        notas_html = f"<div style='margin-top: 15px; padding: 12px; background: #fff; border-radius: 6px; border: 1px dashed #cbd5e1;'><strong style='color: #475569;'>Instruções da {empresa_rotulo}:</strong><p style='margin: 6px 0 0 0; color: #334155;'>{notas}</p></div>" if notas else ""
        corpo_html = f"""
        <h2 style="color: #0f172a; margin-top: 0;">Olá, {nome_candidato}!</h2>
        <p>A sua entrevista com a empresa <strong>{empresa_rotulo}</strong> para a vaga <strong>{titulo_vaga}</strong> foi agendada.</p>
        
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #2563eb; padding: 18px; margin: 20px 0; border-radius: 8px;">
          <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
            <tr>
              <td style="padding: 4px 0; color: #64748b; width: 150px;"><strong>Empresa Recrutadora:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 700;">{empresa_rotulo}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Vaga:</strong></td>
              <td style="padding: 4px 0; color: #0f172a; font-weight: 600;">{titulo_vaga}</td>
            </tr>
            <tr>
              <td style="padding: 4px 0; color: #64748b;"><strong>Data e Hora:</strong></td>
              <td style="padding: 4px 0; color: #2563eb; font-weight: 700;">{data_hora}</td>
            </tr>
          </table>
          {notas_html}
        </div>
        
        {link_html}
        <p style="color: #64748b; font-size: 13px;">Confirme os detalhes no portal e prepare-se para a conversa. Desejamos-lhe muito sucesso!</p>
        """
        corpo_texto = f"Olá {nome_candidato},\n\nEntrevista agendada com a empresa: {empresa_rotulo}\nVaga: {titulo_vaga}\nData e hora: {data_hora}" + (f"\nLink: {link}" if link else "") + (f"\nInstruções: {notas}" if notas else "")
        return self.enviar_email(destinatario, assunto, corpo_html, corpo_texto)
