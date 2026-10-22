"use client";

import { useEffect, useState, useMemo } from "react";
import {
  Search,
  Briefcase,
  Building2,
  Users,
  MapPin,
  Trash2,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Clock,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { AdminJob, api, getSession } from "@/lib/api";

const statuses: AdminJob["status"][] = ["Aberta", "Pausada", "Fechada"];

export default function AdminModerationPage() {
  const [jobs, setJobs] = useState<AdminJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("todas");
  const [jobToDelete, setJobToDelete] = useState<AdminJob | null>(null);
  const [updatingJobId, setUpdatingJobId] = useState<number | null>(null);
  const [expandedJobId, setExpandedJobId] = useState<number | null>(null);

  const session = getSession();

  function loadJobs() {
    if (!session) return;
    setLoading(true);
    api.adminJobs(session.token)
      .then((data) => {
        setJobs(data);
        setError("");
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadJobs();
  }, []);

  async function handleStatusChange(job: AdminJob, newStatus: AdminJob["status"]) {
    if (!session || job.status === newStatus) return;
    setUpdatingJobId(job.id);
    setError("");
    try {
      const updated = await api.updateAdminJobStatus(job.id, newStatus, session.token);
      setJobs((prev) => prev.map((item) => (item.id === updated.id ? updated : item)));
      setSuccessMsg(`Status da vaga "${job.titulo}" alterado para ${newStatus}.`);
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível atualizar a vaga.");
    } finally {
      setUpdatingJobId(null);
    }
  }

  async function handleDeleteJob() {
    if (!session || !jobToDelete) return;
    setError("");
    try {
      await api.deleteAdminJob(jobToDelete.id, session.token);
      setJobs((prev) => prev.filter((item) => item.id !== jobToDelete.id));
      setSuccessMsg(`Vaga "${jobToDelete.titulo}" excluída com sucesso.`);
      setJobToDelete(null);
      setTimeout(() => setSuccessMsg(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Erro ao excluir vaga.");
    }
  }

  // Estatísticas rápidas
  const counts = useMemo(() => {
    return {
      total: jobs.length,
      abertas: jobs.filter((j) => j.status === "Aberta").length,
      pausadas: jobs.filter((j) => j.status === "Pausada").length,
      fechadas: jobs.filter((j) => j.status === "Fechada").length,
    };
  }, [jobs]);

  // Filtragem
  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const matchesSearch =
        job.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (job.empresa_nome && job.empresa_nome.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (job.area && job.area.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (job.localizacao && job.localizacao.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus = statusFilter === "todas" || job.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [jobs, searchTerm, statusFilter]);

  const getStatusBadge = (status: AdminJob["status"]) => {
    switch (status) {
      case "Aberta":
        return "bg-emerald-50 text-emerald-700 border-emerald-200";
      case "Pausada":
        return "bg-amber-50 text-amber-700 border-amber-200";
      case "Fechada":
      default:
        return "bg-slate-100 text-slate-700 border-slate-200";
    }
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">Moderação de Vagas</h2>
          <p className="mt-1 text-sm text-slate-500">
            Gerencie o ciclo de vida, visibilidade e conformidade de todas as oportunidades.
          </p>
        </div>
        <button
          onClick={loadJobs}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-sky-600" : "text-slate-400"}`} />
          Atualizar
        </button>
      </div>

      {/* Cards de Métricas */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div
          onClick={() => setStatusFilter("todas")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            statusFilter === "todas" ? "border-sky-500 bg-sky-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <div className="flex items-center gap-1.5 text-slate-600">
            <Briefcase className="h-3.5 w-3.5" />
            <p className="text-xs font-semibold uppercase tracking-wider">Total de Vagas</p>
          </div>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.total}</p>
        </div>

        <div
          onClick={() => setStatusFilter("Aberta")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            statusFilter === "Aberta" ? "border-emerald-500 bg-emerald-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600">Abertas</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.abertas}</p>
        </div>

        <div
          onClick={() => setStatusFilter("Pausada")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            statusFilter === "Pausada" ? "border-amber-500 bg-amber-50/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-600">Pausadas</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.pausadas}</p>
        </div>

        <div
          onClick={() => setStatusFilter("Fechada")}
          className={`cursor-pointer rounded-xl border p-4 transition-all ${
            statusFilter === "Fechada" ? "border-slate-500 bg-slate-100/50 shadow-sm" : "border-slate-200 bg-white hover:border-slate-300"
          }`}
        >
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-600">Fechadas</p>
          <p className="mt-1 text-2xl font-bold text-slate-900">{counts.fechadas}</p>
        </div>
      </div>

      {/* Alertas */}
      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}
      {successMsg && (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-800">
          <CheckCircle2 className="h-5 w-5 shrink-0 text-emerald-600" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Barra de Filtros e Busca */}
      <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:flex-row sm:items-center sm:justify-between">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Pesquisar por título, empresa, área ou localização..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-lg border border-slate-200 bg-slate-50/50 py-2 pl-9 pr-4 text-sm text-slate-800 placeholder-slate-400 focus:border-sky-500 focus:bg-white focus:outline-none focus:ring-1 focus:ring-sky-500"
          />
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs font-medium text-slate-500">Filtrar por Status:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:border-sky-500 focus:outline-none focus:ring-1 focus:ring-sky-500"
          >
            <option value="todas">Todas ({counts.total})</option>
            <option value="Aberta">Abertas ({counts.abertas})</option>
            <option value="Pausada">Pausadas ({counts.pausadas})</option>
            <option value="Fechada">Fechadas ({counts.fechadas})</option>
          </select>
        </div>
      </div>

      {/* Lista de Vagas */}
      <div className="space-y-4">
        {filteredJobs.map((job) => {
          const isExpanded = expandedJobId === job.id;
          const formattedDate = job.data_criacao
            ? new Date(job.data_criacao).toLocaleDateString("pt-PT", {
                day: "2-digit",
                month: "short",
                year: "numeric",
              })
            : null;

          return (
            <article
              key={job.id}
              className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-slate-300"
            >
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="space-y-2 flex-1">
                  <div className="flex flex-wrap items-center gap-2.5">
                    <h3 className="text-lg font-bold text-slate-900">{job.titulo}</h3>
                    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${getStatusBadge(job.status)}`}>
                      {job.status}
                    </span>
                    {job.modalidade && (
                      <span className="rounded bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                        {job.modalidade}
                      </span>
                    )}
                  </div>

                  {/* Informações da Empresa e Metadados */}
                  <div className="flex flex-wrap items-center gap-y-1 gap-x-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1 font-semibold text-slate-700">
                      <Building2 className="h-3.5 w-3.5 text-sky-600" />
                      {job.empresa_nome}
                    </span>

                    {job.localizacao && (
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5 text-slate-400" />
                        {job.localizacao}
                      </span>
                    )}

                    <span className="flex items-center gap-1 font-medium text-sky-700">
                      <Users className="h-3.5 w-3.5" />
                      {job.total_candidaturas} candidatura{job.total_candidaturas !== 1 ? "s" : ""}
                    </span>

                    {formattedDate && (
                      <span className="flex items-center gap-1 text-slate-400">
                        <Clock className="h-3.5 w-3.5" />
                        {formattedDate}
                      </span>
                    )}
                  </div>

                  {/* Breve Descrição */}
                  <p className={`text-sm text-slate-600 ${!isExpanded ? "line-clamp-2" : ""}`}>
                    {job.descricao}
                  </p>

                  {/* Requisitos */}
                  {job.requisitos && job.requisitos.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {job.requisitos.map((req, idx) => (
                        <span
                          key={idx}
                          className="rounded-md border border-slate-100 bg-slate-50 px-2 py-0.5 text-xs text-slate-600"
                        >
                          {req}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Botão de Expandir / Recolher */}
                  <button
                    onClick={() => setExpandedJobId(isExpanded ? null : job.id)}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-sky-600 hover:text-sky-700"
                  >
                    {isExpanded ? (
                      <>
                        Ver menos <ChevronUp className="h-3.5 w-3.5" />
                      </>
                    ) : (
                      <>
                        Ver detalhes completos <ChevronDown className="h-3.5 w-3.5" />
                      </>
                    )}
                  </button>
                </div>

                {/* Ações de Moderação */}
                <div className="flex items-center gap-3 shrink-0 self-end lg:self-start">
                  <div className="flex items-center gap-2">
                    <label className="text-xs font-medium text-slate-500">Status:</label>
                    <select
                      disabled={updatingJobId === job.id}
                      value={job.status}
                      onChange={(e) => handleStatusChange(job, e.target.value as AdminJob["status"])}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:border-slate-300 focus:border-sky-500 focus:outline-none"
                    >
                      {statuses.map((st) => (
                        <option key={st} value={st}>
                          {st}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={() => setJobToDelete(job)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-100 transition-colors"
                    title="Excluir vaga"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                    Excluir
                  </button>
                </div>
              </div>
            </article>
          );
        })}

        {/* Estados vazios / Carregando */}
        {loading && (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-500">
            <RefreshCw className="mx-auto h-6 w-6 animate-spin text-sky-600 mb-2" />
            Carregando vagas...
          </div>
        )}

        {!loading && filteredJobs.length === 0 && (
          <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
            <p className="text-base font-semibold text-slate-800">Nenhuma vaga encontrada</p>
            <p className="mt-1 text-sm text-slate-500">
              {searchTerm || statusFilter !== "todas"
                ? "Tente ajustar os filtros ou os termos de pesquisa."
                : "Ainda não existem vagas publicadas na plataforma."}
            </p>
          </div>
        )}
      </div>

      {/* Modal de Confirmação de Exclusão da Vaga */}
      {jobToDelete && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-red-100 text-red-600 mb-4">
              <Trash2 className="h-6 w-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Excluir Vaga</h3>
            <p className="mt-2 text-sm text-slate-600">
              Tem certeza que deseja excluir permanentemente a vaga{" "}
              <strong className="text-slate-800">{jobToDelete.titulo}</strong> da empresa{" "}
              <strong className="text-slate-800">{jobToDelete.empresa_nome}</strong>?
            </p>
            <p className="mt-2 text-xs text-amber-700 bg-amber-50 p-2.5 rounded-lg border border-amber-200">
              Atenção: Todas as {jobToDelete.total_candidaturas} candidatura(s) atreladas a esta vaga também serão excluídas.
            </p>
            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setJobToDelete(null)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleDeleteJob}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white hover:bg-red-700 transition-colors"
              >
                Excluir Vaga
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
