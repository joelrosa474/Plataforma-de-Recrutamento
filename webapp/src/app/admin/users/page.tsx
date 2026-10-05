"use client";

import { useEffect, useState } from "react";
import { api, getSession, SessionUser } from "@/lib/api";

export default function AdminUsersPage() {
  const [users, setUsers] = useState<SessionUser[]>([]); const [error, setError] = useState("");
  useEffect(() => { const session = getSession(); if (session) api.adminUsers(session.token).then(setUsers).catch((e: Error) => setError(e.message)); }, []);
  return <section><h2 className="text-2xl font-bold text-slate-950">Gestão de utilizadores</h2><p className="mt-2 text-slate-600">Contas registadas na plataforma.</p>{error ? <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p> : <div className="mt-6 overflow-hidden rounded-xl border border-slate-200 bg-white"><div className="overflow-x-auto"><table className="w-full text-left text-sm"><thead className="bg-slate-50 text-slate-600"><tr><th className="p-4">Nome</th><th className="p-4">E-mail</th><th className="p-4">Perfil</th><th className="p-4">Localização</th></tr></thead><tbody>{users.map((user) => <tr key={user.id} className="border-t border-slate-100"><td className="p-4 font-medium text-slate-950">{user.nome}</td><td className="p-4 text-slate-600">{user.email}</td><td className="p-4"><span className="rounded-full bg-sky-50 px-2.5 py-1 text-xs font-semibold text-sky-700">{user.tipo_perfil}</span></td><td className="p-4 text-slate-600">{user.localizacao ?? "—"}</td></tr>)}</tbody></table></div>{users.length === 0 && <p className="p-6 text-slate-600">Nenhum utilizador registado.</p>}</div>}</section>;
}
