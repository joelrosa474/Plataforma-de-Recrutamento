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
    def enviar_boas_vindas(
        self,
        destinatario: str,
        nome: str,
        tipo_perfil: str
    ) -> bool:
        """Envia e-mail de boas-vindas da plataforma É Salú com descrições das funcionalidades."""
        pass

    @abstractmethod
    def enviar_notificacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nova_fase: str,
        nome_empresa: Optional[str] = None
    ) -> bool:
        """Notifica o candidato sobre atualização na fase da sua candidatura incluindo a empresa recrutadora."""
        pass

    @abstractmethod
    def enviar_confirmacao_candidatura(
        self,
        destinatario: str,
        nome_candidato: str,
        titulo_vaga: str,
        nome_empresa: Optional[str] = None
    ) -> bool:
        """Confirma a receção da candidatura ao candidato indicando a empresa recrutadora."""
        pass

    @abstractmethod
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
        """Envia confirmação do agendamento de entrevista com os dados da empresa recrutadora."""
        pass

    @abstractmethod
    def enviar_alerta_documento_invalido(
        self,
        email_recrutador: str,
        nome_empresa: str,
        titulo_vaga: str,
        nome_candidato: str,
        email_candidato: str,
        motivo_ia: str
    ) -> bool:
        """Notifica o recrutador que o documento submetido pelo candidato não é um currículo."""
        pass
