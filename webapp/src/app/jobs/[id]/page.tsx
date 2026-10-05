"use client";

import { ChangeEvent, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowLeft, Briefcase, CheckCircle2, FileText, MapPin, Sparkles } from "lucide-react";
import { api, ApiJob, getSession } from "@/lib/api";

export default function JobDetailsPage() {
  const params = useParams<{ id: string }>();
  const [job, setJob] = useState<ApiJob | null>(null);
  const [resume, setResume] = useState<File | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);

  useEffect(() => {
    if (params?.id) {
      api.getJob(Number(params.id))
        .then(setJob)
        .catch((e: Error) => setError(e.message));
    }
  }, [params?.id]);

  async function apply() {
    const session = getSession();
    if (!session || session.user.tipo_perfil !== "Candidato") {
      setError("Inicie sessão com uma conta de Candidato para se candidatar.");
      return;
    }
    if (!resume || !job) {
      setError("Selecione o seu currículo em PDF.");
      return;
    }
    setSending(true);
    setError("");
    setMessage("");
    try {
      await api.apply(job.id, resume, session.token);
      setMessage("Candidatura enviada com sucesso! A nossa IA está a avaliar o seu perfil.");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível enviar a candidatura.");
    } finally {
      setSending(false);
    }
  }

  if (error && !job) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-16">
        <div className="rounded-2xl bg-red-50 border border-red-200 p-6 text-red-700">
          <p className="font-semibold">{error}</p>
          <Link
            href="/candidate/dashboard"
            className="mt-4 inline-flex items-center gap-1.5 text-sm font-bold text-sky-700 hover:underline"
          >
            <ArrowLeft className="h-4 w-4" /> Voltar às vagas abertas
          </Link>
        </div>
      </main>
    );
  }

  if (!job) {
    return (
      <main className="mx-auto max-w-3xl px-5 py-24 text-center">
        <p className="text-slate-500">A carregar os detalhes da vaga…</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-3xl px-5 py-12">
      <Link
        href="/candidate/dashboard"
        className="inline-flex items-center gap-2 text-sm font-semibold text-slate-600 hover:text-sky-700 transition"
      >
        <ArrowLeft className="h-4 w-4" /> Voltar à lista de vagas
      </Link>

      <article className="mt-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm space-y-8">
        <div>
          <div className="flex items-center gap-2">
            <span className="rounded-full bg-emerald-50 border border-emerald-200 px-3 py-1 text-xs font-bold text-emerald-800">
              {job.status}
            </span>
            {job.modalidade && (
              <span className="rounded-full bg-sky-50 border border-sky-100 px-3 py-1 text-xs font-semibold text-sky-700">
                {job.modalidade}
              </span>
            )}
          </div>
          <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-950">{job.titulo}</h1>
          <p className="mt-2 text-sm font-semibold text-sky-700">
            {[job.area, job.localizacao].filter(Boolean).join(" · ") || "Geral"}
          </p>
        </div>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-slate-900">Descrição da Função</h2>
          <p className="whitespace-pre-wrap leading-relaxed text-slate-600">{job.descricao}</p>
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-bold text-slate-900">Requisitos e Competências</h2>
          <ul className="flex flex-wrap gap-2">
            {job.requisitos.map((item) => (
              <li key={item} className="rounded-lg bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-700">
                {item}
              </li>
            ))}
          </ul>
        </section>

        <section className="border-t border-slate-100 pt-8 space-y-4">
          <div className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-sky-600" />
            <h2 className="text-xl font-bold text-slate-950">Submeter Candidatura</h2>
          </div>
          <p className="text-sm text-slate-600">
            Envie o seu currículo em formato PDF. O sistema irá realizar a triagem inteligente da sua compatibilidade com os requisitos descritos.
          </p>

          <label className="block text-sm font-medium text-slate-700">
            Currículo em PDF *
            <input
              type="file"
              accept="application/pdf,.pdf"
              onChange={(e: ChangeEvent<HTMLInputElement>) => setResume(e.target.files?.[0] ?? null)}
              className="mt-2 block w-full text-sm text-slate-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-bold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100 cursor-pointer"
            />
          </label>

          <button
            type="button"
            onClick={apply}
            disabled={sending || !resume}
            className="inline-flex items-center justify-center rounded-xl bg-sky-600 px-6 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700 disabled:opacity-50"
          >
            {sending ? "A processar pela IA…" : "Confirmar e Enviar Candidatura"}
          </button>

          {message && (
            <div className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-sm font-semibold text-emerald-800">
              <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
              <span>{message}</span>
            </div>
          )}

          {error && (
            <div className="rounded-xl bg-red-50 border border-red-200 p-4 text-sm font-medium text-red-700">
              {error}
            </div>
          )}
        </section>
      </article>
    </main>
  );
}
