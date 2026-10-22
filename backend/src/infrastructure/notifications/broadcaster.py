import asyncio
import logging
from collections import defaultdict
from typing import Dict, Set

logger = logging.getLogger("rh_api")


class NotificationBroadcaster:
    """
    Gerenciador de transmissão de notificações em tempo real via Server-Sent Events (SSE).
    Permite que múltiplos clientes conectados recebam atualizações instantâneas.
    """

    def __init__(self):
        self._subscribers: Dict[int, Set[asyncio.Queue]] = defaultdict(set)

    def subscribe(self, user_id: int) -> asyncio.Queue:
        """Cria e registra uma nova fila para o usuário conectado."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        self._subscribers[user_id].add(queue)
        logger.debug(f"[SSE] Usuário {user_id} inscrito. Total de conexões ativas: {len(self._subscribers[user_id])}")
        return queue

    def unsubscribe(self, user_id: int, queue: asyncio.Queue):
        """Remove a fila quando a conexão for encerrada."""
        if user_id in self._subscribers:
            self._subscribers[user_id].discard(queue)
            if not self._subscribers[user_id]:
                del self._subscribers[user_id]
        logger.debug(f"[SSE] Conexão encerrada para o usuário {user_id}.")

    def broadcast(self, user_id: int, data: dict):
        """Transmite uma notificação para todas as sessões ativas do usuário."""
        if user_id not in self._subscribers:
            return

        for queue in list(self._subscribers[user_id]):
            try:
                try:
                    loop = asyncio.get_running_loop()
                    loop.call_soon_threadsafe(queue.put_nowait, data)
                except RuntimeError:
                    queue.put_nowait(data)
            except asyncio.QueueFull:
                logger.warning(f"[SSE] Fila cheia para o usuário {user_id}. Notificação descartada na sessão.")
            except Exception as e:
                logger.warning(f"[SSE] Falha ao despachar evento para o usuário {user_id}: {e}")


# Instância singleton global do broadcaster
notification_broadcaster = NotificationBroadcaster()
