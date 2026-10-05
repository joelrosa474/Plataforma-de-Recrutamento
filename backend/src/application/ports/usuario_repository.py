from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities.usuario import Usuario

class UsuarioRepository(ABC):
    @abstractmethod
    def salvar(self, usuario: Usuario) -> Usuario:
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        pass
    
    @abstractmethod
    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        pass

    @abstractmethod
    def deletar(self, usuario_id: int) -> bool:
        pass
