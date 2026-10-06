"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, KeyRound, Mail, Trash2, X } from "lucide-react";
import { api, getSession, saveSession } from "@/lib/api";

export default function CompanySettingsPage() {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleting, setDeleting] = useState(false);
  const router = useRouter();

  async function changeEmail(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const session = getSession();
    if (!session) return;
    const form = new FormData(event.currentTarget);
    try {
      const user = await api.updateEmail(String(form.get("email")), String(form.get("senha")), session.token);
      saveSession(session.token, user);
      setMessage("E-mail atualizado com sucesso.");
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível atualizar o e-mail.");
      setMessage("");
    }
  }

  async function changePassword(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const session = getSession();
    if (!session) return;
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    try {
      await api.updatePassword(String(form.get("senha_atual")), String(form.get("nova_senha")), session.token);
      setMessage("Palavra-passe atualizada com sucesso.");
      setError("");
      formElement?.reset();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível atualizar a palavra-passe.");
      setMessage("");
    }
  }

  async function handleConfirmDelete() {
    const session = getSession();
    if (!session) return;
    if (!deletePassword) {
      setError("Digite a sua palavra-passe para confirmar.");
      return;
    }
    setDeleting(true);
    setError("");
    try {
      await api.deleteAccount(deletePassword, session.token);
      window.localStorage.removeItem("rh-session");
      router.push("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Não foi possível eliminar a conta.");
      setDeleting(false);
    }
  }

  return (
    <section className="max-w-2xl space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-950">Configurações da Conta</h1>
        <p className="mt-1 text-slate-600">Faça a gestão dos dados de acesso e segurança da sua empresa.</p>
      </div>

      {message && (
        <div role="status" className="rounded-lg bg-emerald-50 border border-emerald-200 p-4 text-sm font-medium text-emerald-800">
          {message}
        </div>
      )}

      {error && (
        <div role="alert" className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={changeEmail} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-sky-600" />
          <h2 className="text-lg font-bold text-slate-900">Alterar E-mail</h2>
        </div>
        <p className="text-xs text-slate-500">Introduza o novo e-mail corporativo e a sua palavra-passe atual para confirmar.</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Novo E-mail
            <input
              required
              type="email"
              name="email"
              placeholder="novo.email@empresa.com"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Palavra-passe Atual
            <input
              required
              type="password"
              name="senha"
              placeholder="••••••••"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500"
            />
          </label>
        </div>
        <button
          type="submit"
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700"
        >
          Guardar Novo E-mail
        </button>
      </form>

      <form onSubmit={changePassword} className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-sky-600" />
          <h2 className="text-lg font-bold text-slate-900">Alterar Palavra-passe</h2>
        </div>
        <p className="text-xs text-slate-500">A nova palavra-passe deve conter pelo menos 8 caracteres.</p>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm font-medium text-slate-700">
            Palavra-passe Atual
            <input
              required
              type="password"
              name="senha_atual"
              placeholder="••••••••"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500"
            />
          </label>
          <label className="block text-sm font-medium text-slate-700">
            Nova Palavra-passe
            <input
              required
              minLength={8}
              type="password"
              name="nova_senha"
              placeholder="Pelo menos 8 caracteres"
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none focus:border-sky-500"
            />
          </label>
        </div>
        <button
          type="submit"
          className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700"
        >
          Atualizar Palavra-passe
        </button>
      </form>

      <div className="rounded-xl border border-red-200 bg-red-50/50 p-6 space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <h2 className="text-lg font-bold text-red-950">Zona de Perigo</h2>
        </div>
        <p className="text-sm text-red-800">
          A eliminação da conta institucional é irreversível. Todas as vagas em aberto e históricos associados serão removidos.
        </p>
        <button
          type="button"
          onClick={() => {
            setDeletePassword("");
            setShowDeleteModal(true);
          }}
          className="inline-flex items-center gap-2 rounded-lg border border-red-300 bg-white px-4 py-2 text-sm font-bold text-red-700 shadow-sm transition hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4" />
          Eliminar Conta Permanentemente
        </button>
      </div>

      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/50 backdrop-blur-sm px-4">
          <div role="dialog" aria-modal="true" className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-red-700 font-bold text-lg">
                <AlertTriangle className="h-5 w-5" />
                Confirmar Eliminação
              </div>
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-lg p-1 text-slate-400 hover:text-slate-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="text-sm text-slate-600">
              Tem a certeza de que deseja eliminar esta conta? Para confirmar esta operação crítica, introduza a sua palavra-passe:
            </p>

            <label className="block text-sm font-medium text-slate-700">
              Palavra-passe
              <input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Introduza a sua palavra-passe"
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500"
                autoFocus
              />
            </label>

            <div className="flex justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 hover:bg-slate-50"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={deleting || !deletePassword}
                className="rounded-lg bg-red-600 px-4 py-2 text-sm font-bold text-white shadow-sm hover:bg-red-700 disabled:opacity-50"
              >
                {deleting ? "A eliminar…" : "Sim, eliminar conta"}
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
