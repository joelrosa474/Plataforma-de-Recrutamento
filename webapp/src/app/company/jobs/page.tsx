"use client";

import { FormEvent, useEffect, useState } from "react";
import { PlusCircle, Briefcase, Sparkles, AlertCircle, Edit, Pause, Lock, Trash2 } from "lucide-react";
import { api, ApiJob, getSession } from "@/lib/api";

const clean = (value: FormDataEntryValue | null) =>
  String(value ?? "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

export default function CompanyJobsPage() {
  const [jobs, setJobs] = useState<ApiJob[]>([]);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [editing, setEditing] = useState<ApiJob | null>(null);

  const load = async () => {
    const session = getSession();
    if (!session) return;
    try {
      setJobs(await api.myJobs(session.token));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível carregar vagas.");
    }
  };

  useEffect(() => {
    void load();
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const session = getSession();
    if (!session) return setError("Entre com uma conta de empresa para continuar.");
    const formEl = event.currentTarget;
    const form = new FormData(formEl);
    const data = {
      titulo: String(form.get("titulo")),
      descricao: String(form.get("descricao")),
      requisitos: clean(form.get("requisitos")),
      localizacao: String(form.get("localizacao")) || null,
      modalidade: String(form.get("modalidade")) || null,
      area: String(form.get("area")) || null,
    };
    setSaving(true);
    setError("");
    try {
      if (editing) await api.updateJob(editing.id, data, session.token);
      else await api.createJob(data, session.token);
      formEl?.reset();
      setEditing(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível guardar a vaga.");
    } finally {
      setSaving(false);
    }
  }

  async function action(id: number, type: "pause" | "close" | "delete") {
    const session = getSession();
    if (!session) return;
    if (type === "delete" && !window.confirm("Eliminar esta vaga? Esta ação não pode ser desfeita.")) return;
    try {
      if (type === "pause") await api.pauseJob(id, session.token);
      if (type === "close") await api.closeJob(id, session.token);
      if (type === "delete") await api.deleteJob(id, session.token);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível concluir a ação.");
    }
  }

  return (
    <div className="grid gap-6 sm:gap-8 xl:grid-cols-[380px_1fr]">
      {/* Formulário de Criação / Edição de Vagas */}
      <section className="h-fit rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
        <div className="flex items-center gap-2 text-sky-700">
          <PlusCircle className="h-5 w-5" />
          <h1 className="text-lg sm:text-xl font-bold text-slate-950">
            {editing ? "Editar Vaga" : "Publicar Nova Vaga"}
          </h1>
        </div>
        <p className="mt-1 text-xs sm:text-sm text-slate-600">
          {editing ? "Atualize as informações da oportunidade." : "A vaga será publicada imediatamente para os candidatos."}
        </p>

        <form key={editing?.id ?? "new"} onSubmit={submit} className="mt-5 space-y-4">
          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Título da Vaga *
            <input
              required
              name="titulo"
              defaultValue={editing?.titulo}
              placeholder="Ex.: Desenvolvedor Frontend React"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-1 gap-3">
            <label className="block text-xs sm:text-sm font-semibold text-slate-800">
              Área de Atuação
              <select
                name="area"
                defaultValue={editing?.area ?? ""}
                className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white"
              >
                <option value="">Selecione a Área</option>
                <option>Tecnologia</option>
                <option>Finanças</option>
                <option>Recursos Humanos</option>
                <option>Vendas</option>
                <option>Operações</option>
              </select>
            </label>

            <label className="block text-xs sm:text-sm font-semibold text-slate-800">
              Modalidade
              <select
                name="modalidade"
                defaultValue={editing?.modalidade ?? ""}
                className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white"
              >
                <option value="">Selecione a Modalidade</option>
                <option>Presencial</option>
                <option>Híbrido</option>
                <option>Remoto</option>
              </select>
            </label>
          </div>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Localização
            <input
              name="localizacao"
              defaultValue={editing?.localizacao ?? ""}
              placeholder="Ex.: Luanda, Talatona"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Descrição da Oportunidade *
            <textarea
              required
              name="descricao"
              rows={4}
              defaultValue={editing?.descricao}
              placeholder="Descreva as responsabilidades e o escopo da função..."
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Requisitos (separados por vírgula)
            <input
              name="requisitos"
              defaultValue={editing?.requisitos.join(", ")}
              placeholder="Ex.: React, TypeScript, Inglês"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <div className="flex flex-col sm:flex-row gap-2.5 pt-2">
            <button
              disabled={saving}
              className="flex-1 rounded-xl bg-sky-600 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700 disabled:opacity-60"
            >
              {saving ? "A guardar…" : editing ? "Guardar Alterações" : "Publicar Vaga"}
            </button>
            {editing && (
              <button
                type="button"
                onClick={() => setEditing(null)}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition"
              >
                Cancelar
              </button>
            )}
          </div>
        </form>

        {error && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-red-50 p-3 text-xs font-semibold text-red-700 border border-red-200">
            <AlertCircle className="h-4 w-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </section>

      {/* Lista de Minhas Vagas */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-950">Vagas Publicadas</h2>
          <p className="mt-1 text-xs sm:text-sm text-slate-600">
            Faça a gestão do status, edite ou pause as vagas da sua empresa.
          </p>
        </div>

        <div className="space-y-3">
          {jobs.map((job) => (
            <article
              key={job.id}
              className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm transition hover:border-slate-300"
            >
              <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-start">
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <h3 className="font-bold text-slate-950 text-base sm:text-lg truncate">{job.titulo}</h3>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-bold border ${
                        job.status === "Aberta"
                          ? "bg-emerald-50 text-emerald-700 border-emerald-200"
                          : job.status === "Pausada"
                          ? "bg-amber-50 text-amber-700 border-amber-200"
                          : "bg-slate-100 text-slate-600 border-slate-200"
                      }`}
                    >
                      {job.status}
                    </span>
                  </div>

                  <p className="text-xs font-medium text-sky-700">
                    {[job.area, job.localizacao, job.modalidade].filter(Boolean).join(" · ")}
                  </p>

                  <p className="text-xs sm:text-sm leading-relaxed text-slate-600 line-clamp-2">
                    {job.descricao}
                  </p>

                  {job.requisitos.length > 0 && (
                    <div className="flex flex-wrap gap-1 pt-1">
                      {job.requisitos.map((req) => (
                        <span key={req} className="rounded-md bg-slate-100 px-2 py-0.5 text-[11px] font-medium text-slate-600">
                          {req}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                {/* Ações da Vaga */}
                <div className="flex flex-wrap items-center gap-2 sm:self-start pt-2 sm:pt-0 border-t border-slate-100 sm:border-0">
                  <button
                    onClick={() => setEditing(job)}
                    className="inline-flex items-center gap-1 rounded-lg border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition"
                  >
                    Editar
                  </button>
                  {job.status === "Aberta" && (
                    <button
                      onClick={() => action(job.id, "pause")}
                      className="inline-flex items-center gap-1 rounded-lg border border-amber-200 bg-amber-50/50 px-3 py-1.5 text-xs font-semibold text-amber-700 hover:bg-amber-100 transition"
                    >
                      Pausar
                    </button>
                  )}
                  {job.status !== "Fechada" && (
                    <button
                      onClick={() => action(job.id, "close")}
                      className="inline-flex items-center gap-1 rounded-lg border border-red-200 bg-red-50/50 px-3 py-1.5 text-xs font-semibold text-red-700 hover:bg-red-100 transition"
                    >
                      Fechar
                    </button>
                  )}
                  <button
                    onClick={() => action(job.id, "delete")}
                    className="inline-flex items-center gap-1 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-red-600 hover:bg-red-50 transition"
                    title="Eliminar vaga"
                  >
                    Eliminar
                  </button>
                </div>
              </div>
            </article>
          ))}

          {jobs.length === 0 && (
            <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center">
              <Briefcase className="mx-auto h-10 w-10 text-slate-300" />
              <p className="mt-3 text-base font-semibold text-slate-700">Ainda não publicou vagas</p>
              <p className="mt-1 text-xs sm:text-sm text-slate-500">
                Preencha o formulário ao lado para abrir o seu primeiro processo seletivo.
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
