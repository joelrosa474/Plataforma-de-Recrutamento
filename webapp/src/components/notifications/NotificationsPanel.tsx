"use client";

import { useEffect, useState, useRef } from "react";
import { Bell, Check, X, Sparkles, CheckCheck } from "lucide-react";
import { api, getSession, Notification } from "@/lib/api";

export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);
  const [open, setOpen] = useState(false);
  const [activeToast, setActiveToast] = useState<Notification | null>(null);
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const loadNotifications = () => {
    const session = getSession();
    if (session) {
      api.notifications(session.token)
        .then(setItems)
        .catch(() => undefined);
    }
  };

  useEffect(() => {
    loadNotifications();

    const session = getSession();
    if (!session?.token) return;

    // Conexão em tempo real via Server-Sent Events (SSE)
    const streamUrl = api.notificationsStreamUrl(session.token);
    const eventSource = new EventSource(streamUrl);

    eventSource.addEventListener("notification", (event) => {
      try {
        const newNotif: Notification = JSON.parse(event.data);
        
        // Atualiza a lista prependendo a notificação instantaneamente
        setItems((prev) => {
          // Evita duplicações
          if (prev.some((n) => n.id === newNotif.id)) return prev;
          return [newNotif, ...prev];
        });

        // Dispara o Toast animado flutuante
        setActiveToast(newNotif);
        if (toastTimeoutRef.current) {
          clearTimeout(toastTimeoutRef.current);
        }
        toastTimeoutRef.current = setTimeout(() => {
          setActiveToast(null);
        }, 6000);
      } catch (err) {
        console.error("Erro ao processar notificação em tempo real:", err);
      }
    });

    eventSource.onerror = () => {
      // EventSource reconecta automaticamente por padrão
      console.debug("SSE reconectando...");
    };

    return () => {
      eventSource.close();
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const unreadCount = items.filter((item) => !item.lida).length;

  async function handleMarkAsRead(item: Notification) {
    const session = getSession();
    if (!session || item.lida) return;
    try {
      const updated = await api.readNotification(item.id, session.token);
      setItems((current) =>
        current.map((entry) => (entry.id === updated.id ? updated : entry))
      );
    } catch (err) {
      console.error(err);
    }
  }

  async function handleMarkAllAsRead() {
    const session = getSession();
    if (!session) return;
    try {
      await api.readAllNotifications(session.token);
      setItems((current) => current.map((item) => ({ ...item, lida: true })));
    } catch (err) {
      console.error(err);
    }
  }

  return (
    <>
      <div className="relative">
        <button
          onClick={() => {
            setOpen((value) => !value);
            if (!open) loadNotifications();
          }}
          aria-label="Notificações"
          className="relative rounded-lg p-2 text-slate-600 transition hover:bg-slate-100 hover:text-slate-900 focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-600 px-1 text-[11px] font-bold text-white shadow-sm ring-2 ring-white animate-pulse">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
        </button>

        {open && (
          <section className="absolute -right-2 sm:right-0 z-50 mt-2 w-[calc(100vw-2rem)] max-w-sm sm:w-96 overflow-hidden rounded-2xl border border-slate-200 bg-white/95 backdrop-blur-md shadow-2xl transition-all duration-200 animate-in fade-in slide-in-from-top-2">
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50/70 px-4 py-3">
              <div className="flex items-center gap-2">
                <h2 className="font-bold text-slate-900 text-sm sm:text-base">Notificações</h2>
                <span className="rounded-full bg-sky-100 px-2 py-0.5 text-xs font-semibold text-sky-800">
                  {unreadCount} não lidas
                </span>
              </div>
              {unreadCount > 0 && (
                <button
                  onClick={handleMarkAllAsRead}
                  className="flex items-center gap-1 text-xs font-semibold text-sky-600 hover:text-sky-800 transition"
                >
                  <CheckCheck className="h-3.5 w-3.5" />
                  Marcar todas
                </button>
              )}
            </div>

            <div className="max-h-[22rem] divide-y divide-slate-100 overflow-y-auto">
              {items.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleMarkAsRead(item)}
                  className={`block w-full p-4 text-left transition hover:bg-slate-50 ${
                    item.lida ? "opacity-75" : "bg-sky-50/50 hover:bg-sky-50/80"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className={`text-sm ${item.lida ? "font-medium text-slate-800" : "font-bold text-slate-950"}`}>
                      {item.titulo}
                    </p>
                    {!item.lida && (
                      <span className="h-2 w-2 flex-shrink-0 rounded-full bg-sky-600 mt-1" />
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-600 line-clamp-2 leading-relaxed">
                    {item.mensagem}
                  </p>
                  <p className="mt-2 text-[10px] text-slate-400">
                    {new Date(item.data_criacao).toLocaleString("pt-AO", {
                      day: "2-digit",
                      month: "short",
                      hour: "2-digit",
                      minute: "2-digit"
                    })}
                  </p>
                </button>
              ))}

              {items.length === 0 && (
                <div className="p-8 text-center">
                  <Bell className="mx-auto h-8 w-8 text-slate-300 stroke-[1.5]" />
                  <p className="mt-2 text-sm text-slate-500">Sem notificações por agora.</p>
                </div>
              )}
            </div>
          </section>
        )}
      </div>

      {/* Toast Flutuante em Tempo Real */}
      {activeToast && (
        <aside
          role="status"
          aria-live="polite"
          className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-6 sm:bottom-6 sm:w-96 max-w-md z-50 flex items-start gap-3 rounded-2xl border border-sky-100 bg-white/95 backdrop-blur-md p-4 shadow-2xl ring-1 ring-slate-900/5 transition-all animate-in slide-in-from-bottom-5 duration-300"
        >
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 text-white shadow-md shadow-sky-600/20">
            <Sparkles className="h-5 w-5" />
          </div>

          <div className="flex-1 min-w-0 pr-1">
            <p className="text-xs font-bold uppercase tracking-wider text-sky-600">Nova Notificação</p>
            <h3 className="text-sm font-bold text-slate-900 truncate mt-0.5">{activeToast.titulo}</h3>
            <p className="text-xs text-slate-600 mt-1 line-clamp-2 leading-relaxed">
              {activeToast.mensagem}
            </p>
          </div>

          <button
            onClick={() => {
              handleMarkAsRead(activeToast);
              setActiveToast(null);
            }}
            className="flex-shrink-0 rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
            aria-label="Fechar notificação"
          >
            <X className="h-4 w-4" />
          </button>
        </aside>
      )}
    </>
  );
}
