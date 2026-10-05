from typing import List, Optional
from src.domain.entities.usuario import Usuario
from src.application.ports.usuario_repository import UsuarioRepository

class UsuarioRepositoryMemory(UsuarioRepository):
    def __init__(self):
        self.usuarios: List[Usuario] = []
        self._current_id = 1

    def salvar(self, usuario: Usuario) -> Usuario:
        if usuario.id is None:
            usuario.id = self._current_id
            self._current_id += 1
            self.usuarios.append(usuario)
            return usuario

        for i, u in enumerate(self.usuarios):
            if u.id == usuario.id:
                self.usuarios[i] = usuario
                return usuario

        usuario.id = self._current_id
        self._current_id += 1
        self.usuarios.append(usuario)
        return usuario

    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        for usuario in self.usuarios:
            if usuario.email == email:
                return usuario
        return None

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        for usuario in self.usuarios:
            if usuario.id == usuario_id:
                return usuario
        return None

    def deletar(self, usuario_id: int) -> bool:
        usuario = self.buscar_por_id(usuario_id)
        if not usuario:
            return False
        self.usuarios.remove(usuario)
        return True
