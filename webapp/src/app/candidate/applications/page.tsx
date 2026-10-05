"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileDown, FileText, ArrowRight, Sparkles } from "lucide-react";
import { api, ApiApplication, ApiJob, getSession } from "@/lib/api";

const phaseClass: Record<string, string> = {
  Triagem: "bg-amber-100 text-amber-800",
  Entrevista: "bg-sky-100 text-sky-800",
  Contratado: "bg-emerald-100 text-emerald-800",
  Reprovado: "bg-red-100 text-red-800",
};

export default function CandidateApplicationsPage() {
  const [applications, setApplications] = useState<ApiApplication[]>([]);
  const [jobs, setJobs] = useState<ApiJob[]>([]);
  const [state, setState] = useState<"loading" | "ready" | "signed-out" | "error">("loading");
  const [error, setError] = useState("");
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      setState("signed-out");
      return;
    }
    Promise.all([api.myApplications(session.token), api.listJobs()])
      .then(([apps, apiJobs]) => {
        setApplications(apps);
        setJobs(apiJobs);
        setState("ready");
      })
      .catch((e: Error) => {
        setError(e.message);
        setState("error");
      });
  }, []);

  async function downloadCV(app: ApiApplication) {
    const session = getSession();
    if (!session) return;
    setDownloadingId(app.id);
    try {
      const blob = await api.downloadResume(app.id, session.token);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = app.curriculo_nome || `meu_curriculo.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Não foi possível descarregar o currículo.");
    } finally {
      setDownloadingId(null);
    }
  }

  if (state === "loading") {
    return (
      <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
        <p className="text-slate-500">A carregar o seu histórico de candidaturas…</p>
      </div>
    );
  }

  if (state === "signed-out") {
    return (
      <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
        <div className="rounded-xl border border-slate-200 bg-white p-8 shadow-sm">
          <h1 className="text-2xl font-bold text-slate-950">Aceda à sua conta</h1>
          <p className="mt-2 text-slate-600">Inicie sessão para acompanhar o estado das suas candidaturas em tempo real.</p>
          <Link
            href="/auth"
            className="mt-5 inline-flex items-center gap-2 rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-sky-700"
          >
            Iniciar Sessão <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    );
  }

  if (state === "error") {
    return (
      <div className="mx-auto max-w-7xl px-5 py-12 sm:px-8">
        <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-sm text-red-700">{error}</div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl px-5 py-10 sm:px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Minhas Candidaturas</h1>
        <p className="mt-1 text-slate-600">Acompanhe a evolução do seu perfil em cada vaga submetida.</p>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {applications.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-10 w-10 text-slate-300" />
            <p className="mt-3 text-base font-semibold text-slate-700">Ainda não realizou nenhuma candidatura</p>
            <p className="mt-1 text-sm text-slate-500">Explore as vagas em aberto e envie o seu currículo.</p>
            <Link
              href="/candidate/dashboard"
              className="mt-5 inline-flex items-center gap-2 rounded-lg bg-sky-600 px-5 py-2.5 text-sm font-bold text-white hover:bg-sky-700"
            >
              Explorar vagas abertas <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {applications.map((app) => {
              const job = jobs.find((j) => j.id === app.vaga_id);
              const score = app.match_score;

              return (
                <article
                  key={app.id}
                  className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between hover:bg-slate-50/50 transition"
                >
                  <div className="space-y-1">
                    <h2 className="text-lg font-bold text-slate-950">{job?.titulo ?? `Vaga #${app.vaga_id}`}</h2>
                    <p className="text-xs text-slate-500">
                      Submetida em {new Date(app.data_aplicacao).toLocaleDateString("pt-AO")}
                      {job?.localizacao && ` · ${job.localizacao}`}
                      {job?.modalidade && ` · ${job.modalidade}`}
                    </p>
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    {score !== null && score !== undefined && (
                      <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                        <Sparkles className="h-3 w-3 text-sky-600" />
                        Match: {score.toFixed(0)}%
                      </span>
                    )}

                    <span className={`rounded-full px-3 py-1 text-xs font-bold ${phaseClass[app.fase_atual] || "bg-slate-100 text-slate-700"}`}>
                      {app.fase_atual}
                    </span>

                    <button
                      type="button"
                      onClick={() => downloadCV(app)}
                      disabled={downloadingId === app.id}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 hover:text-sky-700 disabled:opacity-50"
                      title="Descarregar currículo enviado"
                    >
                      <FileDown className="h-3.5 w-3.5 text-sky-600" />
                      {downloadingId === app.id ? "A abrir…" : "Meu CV (PDF)"}
                    </button>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
