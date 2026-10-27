"use client";

import { FormEvent, useEffect, useState } from "react";
import { ExternalLink, Mail, MapPin, Search, Users } from "lucide-react";
import { api, getSession, Talent } from "@/lib/api";

export default function TalentPoolPage() {
  const [talents, setTalents] = useState<Talent[]>([]);
  const [total, setTotal] = useState(0);
  const [term, setTerm] = useState("");
  const [location, setLocation] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function search(filters: { termo?: string; localizacao?: string } = { termo: term, localizacao: location }) {
    const session = getSession();
    if (!session) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.searchTalents(filters, session.token);
      setTalents(result.items);
      setTotal(result.total);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível pesquisar o Banco de Talentos.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void search({}); }, []);

  function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void search();
  }

  return (
    <section className="space-y-6">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-sky-100 p-3 text-sky-700"><Users className="h-6 w-6" /></div>
        <div><h1 className="text-3xl font-bold tracking-tight text-slate-950">Banco de Talentos</h1><p className="mt-1 text-slate-600">Encontre profissionais que autorizaram a visibilidade do seu perfil.</p></div>
      </div>

      <form onSubmit={submit} className="grid gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-[1fr_240px_auto]">
        <input value={term} onChange={(event) => setTerm(event.target.value)} placeholder="Competência, experiência ou nome…" className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500" />
        <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="Localização, ex.: Luanda" className="rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-sky-500" />
        <button className="inline-flex items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-2 text-sm font-bold text-white hover:bg-sky-700"><Search className="h-4 w-4" />Pesquisar</button>
      </form>

      {error && <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm font-medium text-red-700">{error}</div>}
      {!loading && <p className="text-sm text-slate-500">{total} {total === 1 ? "perfil encontrado" : "perfis encontrados"}.</p>}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {loading ? <p className="text-sm text-slate-500">A pesquisar talentos…</p> : talents.map((talent) => (
          <article key={talent.id} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-bold text-slate-950">{talent.nome}</h2>
            {talent.localizacao && <p className="mt-1 flex items-center gap-1.5 text-sm text-slate-500"><MapPin className="h-4 w-4" />{talent.localizacao}</p>}
            {talent.experiencia && <p className="mt-3 line-clamp-3 text-sm leading-relaxed text-slate-600">{talent.experiencia}</p>}
            {!!talent.competencias?.length && <div className="mt-3 flex flex-wrap gap-1.5">{talent.competencias.map((skill) => <span key={skill} className="rounded-full bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-800">{skill}</span>)}</div>}
            <div className="mt-4 flex flex-wrap gap-3 border-t border-slate-100 pt-3 text-sm font-semibold text-sky-700">
              <a href={`mailto:${talent.email}`} className="inline-flex items-center gap-1 hover:text-sky-900"><Mail className="h-4 w-4" />Contactar</a>
              {talent.linkedin_url && <a href={talent.linkedin_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:text-sky-900">LinkedIn <ExternalLink className="h-3.5 w-3.5" /></a>}
              {talent.github_url && <a href={talent.github_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 hover:text-sky-900">Portfólio <ExternalLink className="h-3.5 w-3.5" /></a>}
            </div>
          </article>
        ))}
      </div>
      {!loading && talents.length === 0 && !error && <div className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-sm text-slate-500">Ainda não existem perfis disponíveis com estes filtros.</div>}
    </section>
  );
}
