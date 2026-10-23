"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BriefcaseBusiness, FileText, Users, PlusCircle, ArrowRight } from "lucide-react";
import { api, ApiApplication, ApiJob, getSession } from "@/lib/api";

export default function CompanyDashboard() {
  const [jobs, setJobs] = useState<ApiJob[]>([]);
  const [applications, setApplications] = useState<ApiApplication[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      setError("Entre com uma conta de empresa para ver o painel.");
      setLoading(false);
      return;
    }
    api.myJobs(session.token)
      .then(async (ownJobs) => {
        setJobs(ownJobs);
        const lists = await Promise.all(ownJobs.map((job) => api.applicationsByJob(job.id, session.token)));
        setApplications(lists.flat());
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const active = jobs.filter((job) => job.status === "Aberta").length;
  const interviewing = applications.filter((app) => app.fase_atual === "Entrevista").length;

  const cards = [
    { label: "Vagas Abertas", value: active, icon: BriefcaseBusiness, href: "/company/jobs", color: "text-sky-600 bg-sky-50" },
    { label: "Candidaturas Recebidas", value: applications.length, icon: Users, href: "/company/candidates", color: "text-indigo-600 bg-indigo-50" },
    { label: "Em Entrevista", value: interviewing, icon: FileText, href: "/company/candidates", color: "text-emerald-600 bg-emerald-50" },
  ];

  return (
    <section className="space-y-6 sm:space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs sm:text-sm font-semibold uppercase tracking-wider text-sky-700">Visão Geral da Empresa</p>
          <h1 className="mt-1 text-2xl sm:text-3xl font-bold tracking-tight text-slate-950">Painel de Controlo</h1>
          <p className="mt-1 text-xs sm:text-sm text-slate-600">Acompanhe a atividade das suas vagas e o fluxo de candidatos em tempo real.</p>
        </div>
        <Link
          href="/company/jobs"
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700 w-full sm:w-auto"
        >
          <PlusCircle className="h-4 w-4" />
          Publicar Nova Vaga
        </Link>
      </div>

      {error ? (
        <div className="rounded-xl bg-red-50 p-4 text-sm font-medium text-red-700 border border-red-200">
          {error}
        </div>
      ) : (
        <>
          {/* Cards de Métricas Responsivos */}
          <div className="grid gap-4 sm:gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
            {cards.map((card) => {
              const Icon = card.icon;
              return (
                <Link
                  key={card.label}
                  href={card.href}
                  className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm transition hover:border-sky-300 hover:shadow-md"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs sm:text-sm font-semibold text-slate-500">{card.label}</span>
                    <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${card.color}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                  </div>
                  <p className="mt-3 text-2xl sm:text-3xl font-bold text-slate-950">{loading ? "…" : card.value}</p>
                </Link>
              );
            })}
          </div>

          {/* Vagas Recentes */}
          <section className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
            <div className="flex items-center justify-between border-b border-slate-100 p-4 sm:p-5">
              <h2 className="text-base sm:text-lg font-bold text-slate-950">Vagas Recentes</h2>
              <Link href="/company/jobs" className="text-xs sm:text-sm font-semibold text-sky-600 hover:text-sky-800 transition">
                Ver todas →
              </Link>
            </div>

            {loading ? (
              <p className="p-8 text-center text-sm text-slate-500">A carregar vagas…</p>
            ) : jobs.length === 0 ? (
              <div className="p-8 sm:p-12 text-center">
                <BriefcaseBusiness className="mx-auto h-10 w-10 text-slate-300" />
                <p className="mt-3 text-sm font-semibold text-slate-700">Ainda não publicou vagas</p>
                <p className="mt-1 text-xs text-slate-500">Comece publicando a sua primeira oportunidade.</p>
              </div>
            ) : (
              <div className="divide-y divide-slate-100">
                {jobs.slice(0, 5).map((job) => (
                  <Link
                    key={job.id}
                    href="/company/jobs"
                    className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 sm:p-5 hover:bg-slate-50/70 transition gap-2 sm:gap-4"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="font-bold text-slate-950 text-sm sm:text-base truncate">{job.titulo}</p>
                      <p className="mt-0.5 text-xs text-slate-500 truncate">
                        {[job.area, job.localizacao, job.modalidade].filter(Boolean).join(" · ")}
                      </p>
                    </div>
                    <div className="flex items-center justify-between sm:justify-end gap-3 pt-1 sm:pt-0">
                      <span
                        className={`rounded-full px-2.5 py-0.5 text-xs font-bold border ${
                          job.status === "Aberta"
                            ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                            : "bg-slate-100 text-slate-600 border-slate-200"
                        }`}
                      >
                        {job.status}
                      </span>
                      <ArrowRight className="h-4 w-4 text-slate-400 hidden sm:inline" />
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </section>
  );
}
