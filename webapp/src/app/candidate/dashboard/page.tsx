"use client";

import { ChangeEvent, useEffect, useState } from "react";
import Link from "next/link";
import { BriefcaseBusiness, FileText, Search, X, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";
import { api, ApiJob, getSession } from "@/lib/api";

export default function CandidateDashboard() {
  const [jobs, setJobs] = useState<ApiJob[]>([]);
  const [query, setQuery] = useState("");
  const [localizacao, setLocalizacao] = useState("");
  const [modalidade, setModalidade] = useState("");
  const [area, setArea] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState<ApiJob | null>(null);
  const [resume, setResume] = useState<File | null>(null);
  const [applying, setApplying] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    setLoading(true);
    api.searchJobs({ termo: query, localizacao, modalidade, area })
      .then((result) => setJobs(result.items))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [query, localizacao, modalidade, area]);

  async function apply() {
    const session = getSession();
    if (!session || session.user.tipo_perfil === "Empresa") {
      setError("Entre com uma conta de candidato antes de se candidatar.");
      return;
    }
    if (!selected || !resume) {
      setError("Selecione o seu currículo em PDF.");
      return;
    }
    setApplying(true);
    setError("");
    try {
      await api.apply(selected.id, resume, session.token);
      const vagaTitulo = selected.titulo;
      setSelected(null);
      setResume(null);
      setSuccessMessage(`A sua candidatura para "${vagaTitulo}" foi enviada com sucesso! A nossa IA está a analisar o seu perfil.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível enviar a candidatura.");
    } finally {
      setApplying(false);
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8 space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md">
            <Sparkles className="h-3.5 w-3.5 text-sky-600" />
            Oportunidades em Aberto
          </span>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">Encontre a vaga ideal para a sua carreira</h1>
          <p className="mt-1 text-slate-600">Explore as ofertas das empresas mais dinâmicas e candidate-se com triagem inteligente.</p>
        </div>
        <Link
          href="/candidate/applications"
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:text-sky-700"
        >
          <FileText className="h-4 w-4 text-sky-600" />
          Minhas Candidaturas
        </Link>
      </div>

      {successMessage && (
        <div role="status" className="flex items-center justify-between rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-sm font-semibold text-emerald-800">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setSuccessMessage("")}
            className="text-emerald-700 hover:text-emerald-900"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}

      {error && (
        <div role="alert" className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm md:grid-cols-4">
        <label className="relative md:col-span-2">
          <Search className="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cargo, competência ou palavra-chave…"
            className="w-full rounded-xl border border-slate-200 bg-slate-50/50 py-3 pl-11 pr-4 text-sm outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
          />
        </label>
        <input
          value={localizacao}
          onChange={(e) => setLocalizacao(e.target.value)}
          placeholder="Localização (ex: Luanda)"
          className="rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-sm outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
        />
        <div className="grid grid-cols-2 gap-2">
          <select
            value={modalidade}
            onChange={(e) => setModalidade(e.target.value)}
            className="rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2 text-xs font-semibold text-slate-700 outline-none transition focus:border-sky-500 focus:bg-white"
          >
            <option value="">Modalidade</option>
            <option>Presencial</option>
            <option>Híbrido</option>
            <option>Remoto</option>
          </select>
          <select
            value={area}
            onChange={(e) => setArea(e.target.value)}
            className="rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2 text-xs font-semibold text-slate-700 outline-none transition focus:border-sky-500 focus:bg-white"
          >
            <option value="">Área</option>
            <option>Tecnologia</option>
            <option>Finanças</option>
            <option>Recursos Humanos</option>
            <option>Vendas</option>
            <option>Operações</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="py-16 text-center">
          <p className="text-sm font-medium text-slate-500">A carregar oportunidades…</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
          <BriefcaseBusiness className="mx-auto h-12 w-12 text-slate-300" />
          <h2 className="mt-4 text-base font-bold text-slate-800">Nenhuma vaga aberta encontrada</h2>
          <p className="mt-1 text-sm text-slate-500">Experimente alterar os termos da pesquisa ou os filtros de localização e modalidade.</p>
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => (
            <article
              key={job.id}
              className="flex min-h-80 flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:shadow-md hover:border-sky-200"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
                  <BriefcaseBusiness className="h-6 w-6" />
                </div>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 border border-emerald-200">
                  {job.status}
                </span>
              </div>

              <h2 className="mt-4 text-xl font-bold tracking-tight text-slate-950">{job.titulo}</h2>
              <p className="mt-1 text-xs font-semibold text-sky-700">
                {[job.area, job.localizacao, job.modalidade].filter(Boolean).join(" · ") || "Geral"}
              </p>

              <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">{job.descricao}</p>

              <div className="mt-4 flex flex-wrap gap-1.5">
                {job.requisitos.slice(0, 4).map((r) => (
                  <span key={r} className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {r}
                  </span>
                ))}
                {job.requisitos.length > 4 && (
                  <span className="rounded-md bg-slate-50 px-1.5 py-0.5 text-xs text-slate-500">
                    +{job.requisitos.length - 4}
                  </span>
                )}
              </div>

              <div className="mt-auto pt-6 flex items-center justify-between border-t border-slate-100">
                <Link
                  href={`/jobs/${job.id}`}
                  className="text-xs font-semibold text-slate-500 hover:text-slate-900"
                >
                  Ver detalhes
                </Link>
                <button
                  type="button"
                  onClick={() => {
                    setSelected(job);
                    setError("");
                  }}
                  className="inline-flex items-center gap-1 text-sm font-bold text-sky-700 hover:text-sky-800"
                >
                  Candidatar-me <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm px-4">
          <section role="dialog" aria-modal="true" className="w-full max-w-lg rounded-2xl bg-white p-7 shadow-2xl space-y-6">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-sky-600">Submissão de Candidatura</span>
                <h2 className="mt-1 text-2xl font-bold text-slate-950">{selected.titulo}</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {[selected.area, selected.localizacao, selected.modalidade].filter(Boolean).join(" · ")}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                aria-label="Fechar"
                className="rounded-lg p-1 text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-semibold text-slate-800">
                Anexar Currículo (PDF) *
                <input
                  type="file"
                  accept="application/pdf,.pdf"
                  onChange={(e: ChangeEvent<HTMLInputElement>) => setResume(e.target.files?.[0] ?? null)}
                  className="mt-2 block w-full text-sm text-slate-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer"
                />
              </label>
              <p className="text-xs text-slate-500">
                O seu currículo será armazenado de forma segura e avaliado pelo nosso assistente de IA Gemini para calcular a aderência com a vaga.
              </p>
            </div>

            {error && (
              <div role="alert" className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs font-semibold text-red-700">
                {error}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={apply}
                disabled={applying || !resume}
                className="inline-flex items-center gap-2 rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-sky-700 disabled:opacity-50"
              >
                {applying ? "A enviar e a analisar…" : "Enviar candidatura"}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
