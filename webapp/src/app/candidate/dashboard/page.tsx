"use client";

import { ChangeEvent, useEffect, useState } from "react";
import Link from "next/link";
import { BriefcaseBusiness, FileText, Search, X, Sparkles, CheckCircle2, ArrowRight } from "lucide-react";
import { api, ApiJob, getSession, RecommendedJob } from "@/lib/api";

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
  const [recommendations, setRecommendations] = useState<RecommendedJob[]>([]);

  useEffect(() => {
    setLoading(true);
    api.searchJobs({ termo: query, localizacao, modalidade, area })
      .then((result) => setJobs(result.items))
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [query, localizacao, modalidade, area]);

  useEffect(() => {
    const session = getSession();
    if (!session || session.user.tipo_perfil !== "Candidato") return;
    api.recommendedJobs(session.token).then(setRecommendations).catch(() => undefined);
  }, []);

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
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-10 space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <span className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-sky-700 bg-sky-50 px-2.5 py-1 rounded-md">
            <Sparkles className="h-3.5 w-3.5 text-sky-600" />
            Oportunidades em Aberto
          </span>
          <h1 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight text-slate-950">
            Encontre a vaga ideal para a sua carreira
          </h1>
          <p className="mt-1 text-sm sm:text-base text-slate-600">
            Explore as ofertas das empresas mais dinâmicas e candidate-se com triagem inteligente.
          </p>
        </div>
        <Link
          href="/candidate/applications"
          className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:text-sky-700 w-full sm:w-auto"
        >
          <FileText className="h-4 w-4 text-sky-600" />
          Minhas Candidaturas
        </Link>
      </div>

      {successMessage && (
        <div role="status" className="flex items-center justify-between rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-sm font-semibold text-emerald-800">
          <div className="flex items-center gap-2.5">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
            <span>{successMessage}</span>
          </div>
          <button
            type="button"
            onClick={() => setSuccessMessage("")}
            className="rounded-lg p-1 text-emerald-700 hover:bg-emerald-100 transition"
            aria-label="Fechar"
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

      {recommendations.length > 0 && (
        <section className="rounded-2xl border border-violet-100 bg-gradient-to-r from-violet-50 via-sky-50 to-white p-5 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div><p className="inline-flex items-center gap-1 text-xs font-bold uppercase tracking-wider text-violet-700"><Sparkles className="h-3.5 w-3.5" />Para o seu perfil</p><h2 className="mt-1 text-xl font-bold text-slate-950">Vagas recomendadas</h2><p className="mt-1 text-sm text-slate-600">Sugestões explicáveis baseadas nas competências, experiência e localização do seu perfil.</p></div>
            <Link href="/candidate/profile" className="shrink-0 text-xs font-bold text-sky-700 hover:text-sky-900">Atualizar perfil</Link>
          </div>
          <div className="mt-4 grid gap-3 md:grid-cols-3">
            {recommendations.map((job) => <article key={job.id} className="rounded-xl border border-white bg-white/90 p-4 shadow-sm"><div className="flex items-start justify-between gap-2"><h3 className="font-bold text-slate-950">{job.titulo}</h3><span className="shrink-0 rounded-full bg-violet-100 px-2 py-0.5 text-xs font-bold text-violet-800">{job.match_score.toFixed(0)}%</span></div><p className="mt-1 text-xs text-sky-700">{[job.area, job.localizacao, job.modalidade].filter(Boolean).join(" · ")}</p><ul className="mt-3 space-y-1 text-xs leading-relaxed text-slate-600">{job.motivos.slice(0, 2).map((motivo) => <li key={motivo}>• {motivo}</li>)}</ul><button type="button" onClick={() => setSelected(job)} className="mt-4 text-xs font-bold text-sky-700 hover:text-sky-900">Ver vaga e candidatar-me →</button></article>)}
          </div>
        </section>
      )}

      {/* Filtros de Busca Responsivos */}
      <div className="grid gap-3 rounded-2xl border border-slate-200 bg-white p-3.5 sm:p-4 shadow-sm grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        <label className="relative sm:col-span-2 lg:col-span-2">
          <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-slate-400" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Cargo, competência ou palavra-chave…"
            className="w-full rounded-xl border border-slate-200 bg-slate-50/50 py-3 pl-11 pr-4 text-base sm:text-sm outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
          />
        </label>
        <input
          value={localizacao}
          onChange={(e) => setLocalizacao(e.target.value)}
          placeholder="Localização (ex: Luanda)"
          className="rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-3 text-base sm:text-sm outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
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

      {/* Lista de Vagas */}
      {loading ? (
        <div className="py-16 text-center">
          <p className="text-sm font-medium text-slate-500">A carregar oportunidades…</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 sm:p-12 text-center">
          <BriefcaseBusiness className="mx-auto h-12 w-12 text-slate-300" />
          <h2 className="mt-4 text-base font-bold text-slate-800">Nenhuma vaga aberta encontrada</h2>
          <p className="mt-1 text-sm text-slate-500">Experimente alterar os termos da pesquisa ou os filtros de localização e modalidade.</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:gap-5 grid-cols-1 md:grid-cols-2 xl:grid-cols-3">
          {jobs.map((job) => (
            <article
              key={job.id}
              className="flex min-h-80 flex-col rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm transition hover:shadow-md hover:border-sky-200"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-sky-50 text-sky-700 shrink-0">
                  <BriefcaseBusiness className="h-6 w-6" />
                </div>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 border border-emerald-200">
                  {job.status}
                </span>
              </div>

              <h2 className="mt-4 text-lg font-bold text-slate-950 line-clamp-1">{job.titulo}</h2>
              <p className="mt-1 text-xs font-medium text-sky-700">
                {[job.area, job.localizacao, job.modalidade].filter(Boolean).join(" · ")}
              </p>

              <p className="mt-3 text-sm leading-relaxed text-slate-600 line-clamp-3 flex-1">{job.descricao}</p>

              {job.requisitos.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-1.5 border-t border-slate-100 pt-3">
                  {job.requisitos.slice(0, 3).map((item) => (
                    <span key={item} className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                      {item}
                    </span>
                  ))}
                  {job.requisitos.length > 3 && (
                    <span className="rounded-md bg-slate-100 px-2 py-0.5 text-xs text-slate-600">
                      +{job.requisitos.length - 3}
                    </span>
                  )}
                </div>
              )}

              <div className="mt-5 pt-3 border-t border-slate-100 flex items-center justify-between gap-2">
                <span className="text-[11px] text-slate-400">
                  {new Date(job.data_criacao).toLocaleDateString("pt-AO")}
                </span>
                <button
                  type="button"
                  onClick={() => setSelected(job)}
                  className="inline-flex items-center gap-1.5 rounded-xl bg-sky-600 px-4 py-2 text-xs font-bold text-white shadow-sm transition hover:bg-sky-700"
                >
                  Candidatar-me
                  <ArrowRight className="h-3.5 w-3.5" />
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      {/* Modal de Candidatura Totalmente Responsivo */}
      {selected && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4 overflow-y-auto">
          <section role="dialog" aria-modal="true" className="w-full max-w-lg rounded-2xl bg-white p-5 sm:p-7 shadow-2xl space-y-6 my-auto max-h-[92vh] overflow-y-auto">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-sky-600">Submissão de Candidatura</span>
                <h2 className="mt-1 text-xl sm:text-2xl font-bold text-slate-950">{selected.titulo}</h2>
                <p className="text-xs text-slate-500 mt-0.5">
                  {[selected.area, selected.localizacao, selected.modalidade].filter(Boolean).join(" · ")}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelected(null)}
                aria-label="Fechar"
                className="rounded-lg p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
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
                  className="mt-2 block w-full text-sm text-slate-600 file:mr-3 sm:file:mr-4 file:py-2.5 file:px-3 sm:file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer"
                />
              </label>
              <p className="text-xs text-slate-500">
                O seu currículo será avaliado pelo nosso assistente de IA Gemini para calcular a aderência com a vaga.
              </p>
            </div>

            {error && (
              <div role="alert" className="rounded-lg bg-red-50 border border-red-200 p-3 text-xs font-semibold text-red-700">
                {error}
              </div>
            )}

            <div className="flex flex-col-reverse sm:flex-row justify-end gap-2.5 sm:gap-3 pt-2">
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="w-full sm:w-auto rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={apply}
                disabled={applying || !resume}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-sky-700 disabled:opacity-50 transition"
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
