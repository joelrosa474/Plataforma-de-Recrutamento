"use client";

import { useEffect, useState } from "react";
import { FileDown, Sparkles, MapPin, Mail, Calendar, FileText, CheckCircle, Clock } from "lucide-react";
import { api, ApiApplication, ApiJob, getSession, SessionUser } from "@/lib/api";

const phases = ["Triagem", "Entrevista", "Contratado", "Reprovado"] as const;

export default function CompanyCandidatesPage() {
  const [jobs, setJobs] = useState<ApiJob[]>([]);
  const [jobId, setJobId] = useState("");
  const [apps, setApps] = useState<ApiApplication[]>([]);
  const [profiles, setProfiles] = useState<Record<number, SessionUser>>({});
  const [error, setError] = useState("");
  const [downloadingId, setDownloadingId] = useState<number | null>(null);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      setError("Entre com uma conta de empresa para consultar candidatos.");
      return;
    }
    api.myJobs(session.token)
      .then((items) => {
        setJobs(items);
        if (items[0]) setJobId(String(items[0].id));
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  useEffect(() => {
    const session = getSession();
    if (!session || !jobId) return;
    api.applicationsByJob(Number(jobId), session.token)
      .then(setApps)
      .catch((e: Error) => setError(e.message));
  }, [jobId]);

  // Fallback caso a API não traga os dados embutidos
  useEffect(() => {
    const session = getSession();
    if (!session) return;
    apps.forEach((app) => {
      if (!app.candidato && !profiles[app.candidato_id]) {
        api.candidateProfile(app.candidato_id, session.token)
          .then((profile) => setProfiles((curr) => ({ ...curr, [app.candidato_id]: profile })))
          .catch(() => undefined);
      }
    });
  }, [apps, profiles]);

  async function changePhase(app: ApiApplication, phase: ApiApplication["fase_atual"]) {
    const session = getSession();
    if (!session) return;
    try {
      const updated = await api.updateApplicationPhase(app.id, phase, session.token);
      setApps((items) => items.map((item) => (item.id === updated.id ? { ...item, fase_atual: updated.fase_atual } : item)));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível atualizar a fase.");
    }
  }

  async function downloadCV(app: ApiApplication) {
    const session = getSession();
    if (!session) return;
    setDownloadingId(app.id);
    try {
      const blob = await api.downloadResume(app.id, session.token);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = app.curriculo_nome || `curriculo_candidato_${app.candidato_id}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível descarregar o ficheiro do currículo.");
    } finally {
      setDownloadingId(null);
    }
  }

  return (
    <section className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Gestão de Candidatos (ATS)</h1>
        <p className="mt-1 text-slate-600">Acompanhe a triagem inteligente e o avanço das candidaturas nas suas vagas.</p>
      </div>

      {error && (
        <div role="alert" className="rounded-lg bg-red-50 p-4 text-sm font-medium text-red-700 border border-red-200">
          {error}
        </div>
      )}

      <div className="flex flex-col sm:flex-row gap-4 sm:items-center">
        <label className="block max-w-md w-full text-sm font-medium text-slate-700">
          Filtrar por Vaga:
          <select
            value={jobId}
            onChange={(e) => setJobId(e.target.value)}
            className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500"
          >
            <option value="">Selecione uma vaga</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.titulo} ({job.status})
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        {jobId && apps.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-10 w-10 text-slate-300" />
            <p className="mt-3 text-base font-semibold text-slate-700">Nenhuma candidatura registada</p>
            <p className="mt-1 text-sm text-slate-500">Assim que candidatos se candidatarem a esta vaga, aparecerão listados aqui.</p>
          </div>
        ) : !jobId ? (
          <p className="p-8 text-sm text-slate-500">Selecione uma vaga acima para consultar os candidatos.</p>
        ) : (
          <div className="divide-y divide-slate-100">
            {apps.map((app) => {
              const candidato = app.candidato || profiles[app.candidato_id];
              const score = app.match_score;
              const hasCV = app.tem_curriculo ?? true;

              return (
                <article key={app.id} className="flex flex-col gap-5 p-6 hover:bg-slate-50/50 transition sm:flex-row sm:items-center sm:justify-between">
                  <div className="space-y-2">
                    <div className="flex flex-wrap items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-950">
                        {candidato?.nome ?? `Candidato #${app.candidato_id}`}
                      </h2>
                      {score !== null && score !== undefined ? (
                        <span
                          className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-bold ${
                            score >= 80
                              ? "bg-emerald-100 text-emerald-800"
                              : score >= 60
                              ? "bg-amber-100 text-amber-800"
                              : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          <Sparkles className="h-3 w-3" />
                          Match IA: {score.toFixed(0)}% {score >= 80 ? "· Alta Aderência" : score >= 60 ? "· Aderência Média" : "· Baixa Aderência"}
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 rounded-full bg-sky-50 px-2.5 py-0.5 text-xs font-medium text-sky-700 animate-pulse">
                          <Clock className="h-3 w-3" />
                          IA a analisar currículo em background…
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
                      {candidato?.email && (
                        <span className="flex items-center gap-1">
                          <Mail className="h-3.5 w-3.5" />
                          {candidato.email}
                        </span>
                      )}
                      {candidato?.localizacao && (
                        <span className="flex items-center gap-1">
                          <MapPin className="h-3.5 w-3.5" />
                          {candidato.localizacao}
                        </span>
                      )}
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3.5 w-3.5" />
                        {new Date(app.data_aplicacao).toLocaleDateString("pt-AO")}
                      </span>
                    </div>

                    {candidato?.competencias && candidato.competencias.length > 0 && (
                      <div className="flex flex-wrap gap-1 pt-1">
                        {candidato.competencias.map((skill) => (
                          <span key={skill} className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                            {skill}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap items-center gap-3">
                    {hasCV && (
                      <button
                        type="button"
                        onClick={() => downloadCV(app)}
                        disabled={downloadingId === app.id}
                        className="inline-flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3.5 py-2 text-xs font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:text-sky-700 disabled:opacity-50"
                        title="Descarregar currículo original em PDF"
                      >
                        <FileDown className="h-4 w-4 text-sky-600" />
                        {downloadingId === app.id ? "A descarregar…" : "Ver Currículo (PDF)"}
                      </button>
                    )}

                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-slate-500">Fase:</span>
                      <select
                        value={app.fase_atual}
                        onChange={(e) => changePhase(app, e.target.value as ApiApplication["fase_atual"])}
                        className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-semibold text-slate-800 shadow-sm outline-none focus:border-sky-500"
                      >
                        {phases.map((phase) => (
                          <option key={phase}>{phase}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
