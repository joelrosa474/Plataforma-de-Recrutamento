"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";
import { User, CheckCircle2, AlertCircle } from "lucide-react";
import { api, getSession, saveSession, SessionUser } from "@/lib/api";

export default function CandidateProfilePage() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session) return;
    api.myProfile(session.token).then(setUser).catch((e: Error) => setError(e.message));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const session = getSession();
    if (!session) return;
    const form = new FormData(event.currentTarget);
    setSaving(true);
    setError("");
    setMessage("");
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
      setUser(updated);
      saveSession(session.token, updated);
      setMessage("Perfil atualizado com sucesso.");
      setTimeout(() => setMessage(""), 4000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível atualizar o perfil.");
    } finally {
      setSaving(false);
    }
  }

  if (!getSession()) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-8 sm:px-6">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 sm:p-8 text-center">
          <User className="mx-auto h-10 w-10 text-slate-300" />
          <h1 className="mt-3 text-xl font-bold text-slate-900">Acesse a sua conta</h1>
          <p className="mt-1 text-sm text-slate-500">Entre para gerir as suas informações profissionais.</p>
          <Link
            href="/auth"
            className="mt-5 inline-block rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white transition hover:bg-sky-700"
          >
            Entrar na Conta →
          </Link>
        </section>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-10">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-8 shadow-sm">
        <div className="flex items-center gap-2.5 text-sky-700">
          <User className="h-6 w-6" />
          <h1 className="text-xl sm:text-2xl font-bold text-slate-950">Meu Perfil Profissional</h1>
        </div>
        <p className="mt-1 text-xs sm:text-sm text-slate-600">
          Estes dados ajudam as empresas a conhecerem a sua experiência e qualificações durante a triagem.
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

        <form key={user?.id} onSubmit={submit} className="mt-6 grid gap-4 sm:grid-cols-2">
          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Nome Completo *
            <input
              required
              name="nome"
              defaultValue={user?.nome}
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Localização
            <input
              name="localizacao"
              defaultValue={user?.localizacao ?? ""}
              placeholder="Ex.: Luanda"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800 sm:col-span-2">
            E-mail da Conta (Não alterável)
            <input
              disabled
              value={user?.email ?? ""}
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-100 px-3.5 py-2.5 text-sm text-slate-500 cursor-not-allowed"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800 sm:col-span-2">
            Resumo de Experiência Profissional
            <textarea
              name="experiencia"
              rows={4}
              defaultValue={user?.experiencia ?? ""}
              placeholder="Descreva as suas principais experiências e funções anteriores..."
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800 sm:col-span-2">
            Competências e Habilidades (separadas por vírgula)
            <input
              name="competencias"
              defaultValue={user?.competencias?.join(", ") ?? ""}
              placeholder="Ex.: React, Node.js, Gestão de Equipas, Excel Avançado"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            Perfil do LinkedIn (URL)
            <input
              type="url"
              name="linkedin_url"
              defaultValue={user?.linkedin_url ?? ""}
              placeholder="https://linkedin.com/in/seu-perfil"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <label className="block text-xs sm:text-sm font-semibold text-slate-800">
            GitHub ou Portfólio (URL)
            <input
              type="url"
              name="github_url"
              defaultValue={user?.github_url ?? ""}
              placeholder="https://github.com/seu-usuario"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm text-slate-900 outline-none transition focus:border-sky-500 focus:bg-white focus:ring-1 focus:ring-sky-500"
            />
          </label>

          <div className="sm:col-span-2 pt-2">
            <button
              disabled={saving}
              className="w-full sm:w-auto rounded-xl bg-sky-600 px-6 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700 disabled:opacity-60"
            >
              {saving ? "A guardar…" : "Guardar Alterações"}
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
