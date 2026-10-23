"use client";

import { FormEvent, useEffect, useState } from "react";
import { Building2, CheckCircle2, AlertCircle } from "lucide-react";
import { api, getSession, saveSession, SessionUser } from "@/lib/api";

export default function CompanyProfilePage() {
  const [company, setCompany] = useState<SessionUser | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (session) api.myProfile(session.token).then(setCompany).catch((e: Error) => setError(e.message));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const session = getSession();
    if (!session) return;
    const form = new FormData(event.currentTarget);
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const updated = await api.updateProfile(
        {
          nome: String(form.get("nome")),
          localizacao: String(form.get("localizacao")) || null,
          experiencia: String(form.get("experiencia")) || null,
          competencias: String(form.get("competencias"))
            .split(",")
            .map((item) => item.trim())
            .filter(Boolean),
          linkedin_url: String(form.get("linkedin_url")) || null,
          github_url: String(form.get("github_url")) || null,
        },
        session.token
      );
      setCompany(updated);
      saveSession(session.token, updated);
      setMessage("Perfil institucional atualizado com sucesso.");
      setTimeout(() => setMessage(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível guardar o perfil.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-3xl">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-8 shadow-sm">
        <div className="flex items-center gap-2.5 text-sky-700">
          <Building2 className="h-6 w-6" />
          <h1 className="text-xl sm:text-2xl font-bold text-slate-950">Perfil da Empresa</h1>
        </div>
        <p className="mt-1 text-xs sm:text-sm text-slate-600">
          Apresente a sua organização aos candidatos e organize os dados institucionais da marca.
        </p>

        {message && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-emerald-50 p-3.5 text-sm font-semibold text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
            <span>{message}</span>
          </div>
        )}

        {error && (
          <div className="mt-4 flex items-center gap-2 rounded-xl bg-red-50 p-3.5 text-sm font-semibold text-red-700 border border-red-200">
            <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form key={company?.id} onSubmit={submit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Nome da Empresa *
            <input
              required
              name="nome"
              defaultValue={company?.nome}
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Sede / Localização
            <input
              name="localizacao"
              defaultValue={company?.localizacao ?? ""}
              placeholder="Ex.: Luanda, Angola"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800 sm:col-span-2">
            Sobre a Empresa
            <textarea
              name="experiencia"
              rows={4}
              defaultValue={company?.experiencia ?? ""}
              placeholder="Setor, missão, cultura da empresa e benefícios oferecidos..."
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800 sm:col-span-2">
            Áreas de Atuação (separadas por vírgula)
            <input
              name="competencias"
              defaultValue={company?.competencias?.join(", ") ?? ""}
              placeholder="Ex.: Tecnologia, Consultoria, Telecomunicações"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Página do LinkedIn
            <input
              type="url"
              name="linkedin_url"
              defaultValue={company?.linkedin_url ?? ""}
              placeholder="https://linkedin.com/company/sua-empresa"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Website Oficial
            <input
              type="url"
              name="github_url"
              defaultValue={company?.github_url ?? ""}
              placeholder="https://suaempresa.co.ao"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <div className="sm:col-span-2 pt-2">
            <button
              disabled={saving}
              className="w-full sm:w-auto rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700 disabled:opacity-60"
            >
              {saving ? "A guardar…" : "Guardar Perfil"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
