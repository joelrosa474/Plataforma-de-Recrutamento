from abc import ABC, abstractmethod
from typing import Optional


class EmailServicePort(ABC):
    """Porta (Interface) para o serviço de envio de e-mails transacionais."""

    @abstractmethod
    def enviar_email(
        self,
        destinatario: str,
        assunto: str,
        corpo_html: str,
        corpo_texto: Optional[str] = None
    ) -> bool:
        """Envia um e-mail genérico."""
        pass

    @abstractmethod
    def enviar_recuperacao_senha(
        self,
        destinatario: str,
        nome: str,
        link_redefinicao: str
    ) -> bool:
        """Envia e-mail de recuperação e redefinição de palavra-passe."""
        pass

    @abstractmethod
    def enviar_notificacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nova_fase: str
    ) -> bool:
        """Notifica o candidato sobre atualização na fase da sua candidatura."""
        pass
