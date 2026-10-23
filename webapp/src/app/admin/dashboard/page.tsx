"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  Building2,
  User,
  Briefcase,
  FileCheck2,
  ArrowRight,
  ShieldAlert,
  Sparkles,
  RefreshCw,
  AlertCircle,
  BrainCircuit,
  TrendingUp,
  PieChart,
  Layers,
  CheckCircle,
} from "lucide-react";
import { AdminSummary, api, getSession } from "@/lib/api";

export default function AdminDashboardPage() {
  const [summary, setSummary] = useState<AdminSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const session = getSession();

  function loadSummary() {
    if (!session) return;
    setLoading(true);
    api.adminSummary(session.token)
      .then((data) => {
        setSummary(data);
        setError("");
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadSummary();
  }, []);

  // Cálculos para gráficos de barras e percentuais
  const totalIA = summary?.triagens_ia_total ?? 0;
  const altaPercent = totalIA > 0 ? Math.round(((summary?.compatibilidade_alta ?? 0) / totalIA) * 100) : 0;
  const mediaPercent = totalIA > 0 ? Math.round(((summary?.compatibilidade_media ?? 0) / totalIA) * 100) : 0;
  const baixaPercent = totalIA > 0 ? Math.round(((summary?.compatibilidade_baixa ?? 0) / totalIA) * 100) : 0;

  const totalModalidades = (summary?.vagas_por_modalidade ?? []).reduce((acc, curr) => acc + curr.total, 0);
  const totalFases = (summary?.candidaturas_por_fase ?? []).reduce((acc, curr) => acc + curr.total, 0);

  return (
    <div className="space-y-8">
      {/* Cabeçalho */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 mb-2">
            <Sparkles className="h-3.5 w-3.5" />
            Governança e Inteligência
          </div>
          <h2 className="text-3xl font-extrabold tracking-tight text-slate-900">Painel do Administrador</h2>
          <p className="mt-1 text-sm text-slate-500">
            Acompanhe o volume da plataforma, a atividade semanal e a performance do recrutamento com IA.
          </p>
        </div>
        <button
          onClick={loadSummary}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3.5 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin text-sky-600" : "text-slate-400"}`} />
          Atualizar Indicadores
        </button>
      </div>

      {/* Alerta de Erro */}
      {error && (
        <div className="flex items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          <AlertCircle className="h-5 w-5 shrink-0 text-red-500" />
          <span>{error}</span>
        </div>
      )}

      {/* 1. Indicadores Chave de Desempenho (KPIs) */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Total de Utilizadores */}
        <Link
          href="/admin/users"
          className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-sky-300 hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-sky-50 text-sky-600">
              <Users className="h-5 w-5" />
            </span>
            <span className="flex items-center text-xs font-semibold text-slate-400 group-hover:text-sky-600 transition-colors">
              Ver todos <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </span>
          </div>
          <p className="mt-4 text-sm font-medium text-slate-500">Utilizadores na Plataforma</p>
          <p className="mt-1 text-3xl font-extrabold text-slate-900">{summary?.usuarios ?? 0}</p>
          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <span className="font-semibold text-slate-700">{summary?.candidatos ?? 0}</span> candidatos ·{" "}
            <span className="font-semibold text-slate-700">{summary?.empresas ?? 0}</span> empresas
          </div>
        </Link>

        {/* Vagas Ativas */}
        <Link
          href="/admin/moderation"
          className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition-all hover:border-emerald-300 hover:shadow-md"
        >
          <div className="flex items-center justify-between">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
              <Briefcase className="h-5 w-5" />
            </span>
            <span className="flex items-center text-xs font-semibold text-slate-400 group-hover:text-emerald-600 transition-colors">
              Moderar <ArrowRight className="ml-1 h-3.5 w-3.5" />
            </span>
          </div>
          <p className="mt-4 text-sm font-medium text-slate-500">Vagas Publicadas</p>
          <p className="mt-1 text-3xl font-extrabold text-slate-900">{summary?.vagas ?? 0}</p>
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="rounded bg-emerald-100 px-1.5 py-0.5 font-bold text-emerald-800">
              {summary?.vagas_abertas ?? 0} Abertas
            </span>
            {(summary?.novas_vagas_7d ?? 0) > 0 && (
              <span className="text-emerald-600 font-medium">+{summary?.novas_vagas_7d} nos últimos 7d</span>
            )}
          </div>
        </Link>

        {/* Candidaturas Totais */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-50 text-purple-600">
              <FileCheck2 className="h-5 w-5" />
            </span>
            {(summary?.novas_candidaturas_7d ?? 0) > 0 && (
              <span className="inline-flex items-center gap-1 text-xs font-semibold text-purple-700 bg-purple-50 px-2 py-0.5 rounded-full">
                <TrendingUp className="h-3 w-3" /> +{summary?.novas_candidaturas_7d} esta semana
              </span>
            )}
          </div>
          <p className="mt-4 text-sm font-medium text-slate-500">Candidaturas Submetidas</p>
          <p className="mt-1 text-3xl font-extrabold text-slate-900">{summary?.candidaturas ?? 0}</p>
          <p className="mt-3 text-xs text-slate-500">Total de inscrições registradas</p>
        </div>

        {/* Triagem com IA */}
        <div className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-amber-50 text-amber-600">
              <BrainCircuit className="h-5 w-5" />
            </span>
            <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">
              Ativa
            </span>
          </div>
          <p className="mt-4 text-sm font-medium text-slate-500">Taxa de Triagem IA</p>
          <p className="mt-1 text-3xl font-extrabold text-slate-900">{summary?.taxa_triagem_ia ?? 0}%</p>
          <p className="mt-3 text-xs text-slate-500">
            <span className="font-semibold text-slate-700">{summary?.triagens_ia_total ?? 0}</span> currículos avaliados
          </p>
        </div>
      </div>

      {/* 2. Seção de Monitoramento do Gemini Screener (IA) */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 p-6 text-white shadow-lg">
        <div className="flex flex-col gap-6 md:flex-row md:items-center md:justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-sky-500/20 text-sky-400">
                <BrainCircuit className="h-5 w-5" />
              </span>
              <h3 className="text-lg font-bold text-white">Monitor de Desempenho do Gemini Screener</h3>
              <span className="flex items-center gap-1 rounded-full bg-emerald-500/20 px-2.5 py-0.5 text-xs font-semibold text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Motor IA Operacional
              </span>
            </div>
            <p className="text-xs text-slate-300 max-w-xl">
              Análise semântica e cálculo de compatibilidade automatizada entre perfis de candidatos e requisitos das vagas.
            </p>
          </div>

          <div className="flex items-center gap-6 self-start md:self-center border-t md:border-t-0 md:border-l border-slate-800 pt-4 md:pt-0 md:pl-6">
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-400">Média de Match Score</p>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-3xl font-black text-sky-400">{summary?.media_match_score ?? 0}%</span>
                <span className="text-xs text-slate-400">geral</span>
              </div>
            </div>
            <div>
              <p className="text-xs uppercase tracking-wider text-slate-400">Currículos Triados</p>
              <div className="mt-1 flex items-baseline gap-1">
                <span className="text-3xl font-black text-white">{summary?.triagens_ia_total ?? 0}</span>
                <span className="text-xs text-slate-400">avaliados</span>
              </div>
            </div>
          </div>
        </div>

        {/* Barra de Distribuição de Compatibilidade */}
        <div className="mt-6 rounded-xl bg-slate-800/80 p-5 border border-slate-700/60">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-3">
            Distribuição de Compatibilidade dos Candidatos Triados
          </p>

          <div className="flex h-3.5 w-full overflow-hidden rounded-full bg-slate-900">
            <div
              style={{ width: `${altaPercent}%` }}
              className="bg-emerald-500 transition-all duration-500"
              title={`Alta compatibilidade: ${summary?.compatibilidade_alta ?? 0} (${altaPercent}%)`}
            />
            <div
              style={{ width: `${mediaPercent}%` }}
              className="bg-amber-500 transition-all duration-500"
              title={`Média compatibilidade: ${summary?.compatibilidade_media ?? 0} (${mediaPercent}%)`}
            />
            <div
              style={{ width: `${baixaPercent}%` }}
              className="bg-rose-500 transition-all duration-500"
              title={`Baixa compatibilidade: ${summary?.compatibilidade_baixa ?? 0} (${baixaPercent}%)`}
            />
          </div>

          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-2.5 text-xs">
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shrink-0" />
              <div>
                <span className="text-slate-300">Alta (&ge; 70%): </span>
                <strong className="text-white">{summary?.compatibilidade_alta ?? 0}</strong> ({altaPercent}%)
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500 shrink-0" />
              <div>
                <span className="text-slate-300">Média (40-69%): </span>
                <strong className="text-white">{summary?.compatibilidade_media ?? 0}</strong> ({mediaPercent}%)
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="h-2.5 w-2.5 rounded-full bg-rose-500 shrink-0" />
              <div>
                <span className="text-slate-300">Baixa (&lt; 40%): </span>
                <strong className="text-white">{summary?.compatibilidade_baixa ?? 0}</strong> ({baixaPercent}%)
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Seções Analíticas: Funil do ATS e Modalidades */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Funil de Candidaturas (ATS) */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-sky-600" />
              <h3 className="font-bold text-slate-900">Funil de Fases do ATS</h3>
            </div>
            <span className="text-xs text-slate-500">{totalFases} candidaturas em processo</span>
          </div>

          <div className="mt-5 space-y-4">
            {(summary?.candidaturas_por_fase ?? []).map((fase) => {
              const pct = totalFases > 0 ? Math.round((fase.total / totalFases) * 100) : 0;
              const getFaseColor = (label: string) => {
                switch (label) {
                  case "Contratado":
                    return "bg-emerald-500";
                  case "Entrevista":
                    return "bg-sky-500";
                  case "Reprovado":
                    return "bg-slate-400";
                  case "Triagem":
                  default:
                    return "bg-amber-500";
                }
              };

              return (
                <div key={fase.label} className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-semibold">
                    <span className="text-slate-700">{fase.label}</span>
                    <span className="text-slate-500">
                      {fase.total} ({pct}%)
                    </span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                    <div
                      style={{ width: `${pct}%` }}
                      className={`h-full rounded-full ${getFaseColor(fase.label)} transition-all duration-500`}
                    />
                  </div>
                </div>
              );
            })}

            {(!summary?.candidaturas_por_fase || summary.candidaturas_por_fase.length === 0) && (
              <p className="py-6 text-center text-xs text-slate-400">Nenhuma candidatura registada até o momento.</p>
            )}
          </div>
        </div>

        {/* Modalidades de Trabalho e Top Setores */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between pb-4 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-indigo-600" />
              <h3 className="font-bold text-slate-900">Modalidades e Áreas</h3>
            </div>
            <span className="text-xs text-slate-500">Distribuição das vagas</span>
          </div>

          <div className="mt-5 space-y-5">
            {/* Modalidades */}
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Modalidade</p>
              <div className="space-y-2">
                {(summary?.vagas_por_modalidade ?? []).map((mod) => {
                  const pct = totalModalidades > 0 ? Math.round((mod.total / totalModalidades) * 100) : 0;
                  return (
                    <div key={mod.label} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-slate-700">{mod.label}</span>
                        <span className="text-slate-500">
                          {mod.total} ({pct}%)
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                        <div
                          style={{ width: `${pct}%` }}
                          className="h-full rounded-full bg-indigo-500 transition-all duration-500"
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Top Áreas */}
            {summary?.top_areas && summary.top_areas.length > 0 && (
              <div className="pt-2 border-t border-slate-100">
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                  Áreas Mais Demandadas
                </p>
                <div className="flex flex-wrap gap-2">
                  {summary.top_areas.map((area) => (
                    <span
                      key={area.label}
                      className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-700"
                    >
                      {area.label}
                      <span className="rounded-full bg-slate-200 px-1.5 py-0.2 text-[10px] font-bold text-slate-600">
                        {area.total}
                      </span>
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* 4. Ações Rápidas de Administração */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900">Ações Rápidas de Moderação</h3>
        <p className="mt-1 text-sm text-slate-500">
          Acesse diretamente as ferramentas de governança mais utilizadas.
        </p>

        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Link
            href="/admin/users"
            className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/70 p-4 hover:border-slate-300 hover:bg-slate-100/70 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-100 text-sky-700">
                <Users className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold text-slate-800">Gestão de Utilizadores</p>
                <p className="text-xs text-slate-500">Alterar permissões, filtrar perfis e remover contas.</p>
              </div>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-400" />
          </Link>

          <Link
            href="/admin/moderation"
            className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/70 p-4 hover:border-slate-300 hover:bg-slate-100/70 transition-all"
          >
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100 text-emerald-700">
                <ShieldAlert className="h-5 w-5" />
              </div>
              <div>
                <p className="font-semibold text-slate-800">Moderação de Vagas</p>
                <p className="text-xs text-slate-500">Pausar, reabrir ou excluir vagas suspeitas/fora de conformidade.</p>
              </div>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-400" />
          </Link>
        </div>
      </div>
    </div>
  );
}
