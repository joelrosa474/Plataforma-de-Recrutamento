"use client";

import { useEffect, useState } from "react";
import { Bell } from "lucide-react";
import { api, getSession, Notification } from "@/lib/api";

export function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]); const [open, setOpen] = useState(false);
  const load = () => { const session = getSession(); if (session) api.notifications(session.token).then(setItems).catch(() => undefined); };
  useEffect(() => { load(); }, []);
  const unread = items.filter((item) => !item.lida).length;
  async function read(item: Notification) { const session = getSession(); if (!session || item.lida) return; const updated = await api.readNotification(item.id, session.token); setItems((current) => current.map((entry) => entry.id === updated.id ? updated : entry)); }
  async function readAll() { const session = getSession(); if (!session) return; await api.readAllNotifications(session.token); setItems((current) => current.map((item) => ({ ...item, lida: true }))); }
  return <div className="relative"><button onClick={() => { setOpen((value) => !value); if (!open) load(); }} aria-label="Notificações" className="relative rounded-md p-2 text-slate-600 hover:bg-slate-100"><Bell className="h-5 w-5" />{unread > 0 && <span className="absolute right-0 top-0 min-w-4 rounded-full bg-red-600 px-1 text-[10px] font-bold text-white">{unread}</span>}</button>{open && <section className="absolute right-0 z-50 mt-2 w-80 overflow-hidden rounded-xl border border-slate-200 bg-white shadow-xl"><div className="flex items-center justify-between border-b border-slate-100 p-4"><h2 className="font-bold text-slate-950">Notificações</h2>{unread > 0 && <button onClick={readAll} className="text-xs font-semibold text-sky-700">Marcar todas como lidas</button>}</div><div className="max-h-96 overflow-y-auto">{items.map((item) => <button key={item.id} onClick={() => read(item)} className={`block w-full border-b border-slate-100 p-4 text-left hover:bg-slate-50 ${item.lida ? "" : "bg-sky-50/60"}`}><p className="text-sm font-bold text-slate-950">{item.titulo}</p><p className="mt-1 text-sm text-slate-600">{item.mensagem}</p><p className="mt-2 text-xs text-slate-400">{new Date(item.data_criacao).toLocaleString("pt-AO")}</p></button>)}{items.length === 0 && <p className="p-5 text-sm text-slate-600">Ainda não há notificações.</p>}</div></section>}</div>;
}
