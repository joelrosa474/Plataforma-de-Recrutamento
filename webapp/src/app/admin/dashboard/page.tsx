"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AdminSummary, api, getSession } from "@/lib/api";

const cards: { key: keyof AdminSummary; label: string; href: string }[] = [
  { key: "usuarios", label: "Utilizadores", href: "/admin/users" },
  { key: "empresas", label: "Empresas", href: "/admin/users" },
  { key: "candidatos", label: "Candidatos", href: "/admin/users" },
  { key: "vagas", label: "Vagas publicadas", href: "/admin/moderation" },
  { key: "candidaturas", label: "Candidaturas", href: "/admin/moderation" },
];

export default function AdminDashboardPage() {
  const [summary, setSummary] = useState<AdminSummary | null>(null); const [error, setError] = useState("");
  useEffect(() => { const session = getSession(); if (session) api.adminSummary(session.token).then(setSummary).catch((e: Error) => setError(e.message)); }, []);
  return <section><p className="text-sm font-semibold text-sky-700">Administração</p><h2 className="mt-1 text-3xl font-bold text-slate-950">Visão geral</h2><p className="mt-2 text-slate-600">Acompanhe a atividade da plataforma.</p>{error && <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>}{!summary && !error ? <p className="mt-6 text-slate-600">A carregar indicadores…</p> : summary && <div className="mt-7 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">{cards.map((card) => <Link key={card.key} href={card.href} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm hover:border-sky-300"><p className="text-sm font-medium text-slate-500">{card.label}</p><p className="mt-2 text-3xl font-bold text-slate-950">{summary[card.key]}</p></Link>)}</div>}</section>;
}
