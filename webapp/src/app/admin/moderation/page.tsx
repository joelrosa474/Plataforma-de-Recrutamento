"use client";

import { useEffect, useState } from "react";
import { api, ApiJob, getSession } from "@/lib/api";

const statuses: ApiJob["status"][] = ["Aberta", "Pausada", "Fechada"];

export default function AdminModerationPage() {
  const [jobs, setJobs] = useState<ApiJob[]>([]); const [error, setError] = useState("");
  useEffect(() => { const session = getSession(); if (session) api.adminJobs(session.token).then(setJobs).catch((e: Error) => setError(e.message)); }, []);
  async function setStatus(job: ApiJob, status: ApiJob["status"]) { const session = getSession(); if (!session) return; try { const updated = await api.updateAdminJobStatus(job.id, status, session.token); setJobs((items) => items.map((item) => item.id === updated.id ? updated : item)); } catch (e) { setError(e instanceof Error ? e.message : "Não foi possível atualizar a vaga."); } }
  return <section><h2 className="text-2xl font-bold text-slate-950">Moderação de vagas</h2><p className="mt-2 text-slate-600">Altere a visibilidade de vagas publicadas.</p>{error && <p className="mt-6 rounded-md bg-red-50 p-3 text-sm text-red-700">{error}</p>}<div className="mt-6 divide-y divide-slate-100 overflow-hidden rounded-xl border border-slate-200 bg-white">{jobs.map((job) => <article key={job.id} className="flex flex-col gap-4 p-5 md:flex-row md:items-center md:justify-between"><div><h3 className="font-bold text-slate-950">{job.titulo}</h3><p className="mt-1 max-w-2xl text-sm text-slate-600">{job.descricao}</p><p className="mt-2 text-xs text-slate-500">Empresa #{job.empresa_id} · {job.requisitos.join(" · ")}</p></div><select value={job.status} onChange={(event) => setStatus(job, event.target.value as ApiJob["status"])} className="rounded-md border border-slate-300 bg-white px-3 py-2 text-sm">{statuses.map((status) => <option key={status}>{status}</option>)}</select></article>)}{jobs.length === 0 && <p className="p-6 text-slate-600">Nenhuma vaga publicada.</p>}</div></section>;
}
