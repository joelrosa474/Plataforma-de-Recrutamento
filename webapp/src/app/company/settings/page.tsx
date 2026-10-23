"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, KeyRound, Mail, Trash2, X, CheckCircle2, AlertCircle } from "lucide-react";
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
    <section className="max-w-2xl space-y-6 sm:space-y-8">
      <div>
        <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-950">Configurações da Conta</h1>
        <p className="mt-1 text-xs sm:text-sm text-slate-600">Faça a gestão dos dados de acesso e segurança da sua empresa.</p>
      </div>

      {message && (
        <div role="status" className="flex items-center gap-2 rounded-xl bg-emerald-50 border border-emerald-200 p-4 text-sm font-semibold text-emerald-800">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div role="alert" className="flex items-center gap-2 rounded-xl bg-red-50 border border-red-200 p-4 text-sm font-semibold text-red-700">
          <AlertCircle className="h-5 w-5 text-red-500 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Formulário de E-mail */}
      <form onSubmit={changeEmail} className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Mail className="h-5 w-5 text-sky-600" />
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Alterar E-mail</h2>
        </div>
        <p className="text-xs text-slate-500">Introduza o novo e-mail corporativo e a palavra-passe atual para confirmar.</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-xs sm:text-sm font-semibold text-slate-700">
            Novo E-mail
            <input
              required
              type="email"
              name="email"
              placeholder="novo.email@empresa.com"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm shadow-sm outline-none focus:border-sky-500 focus:bg-white"
            />
          </label>
          <label className="block text-xs sm:text-sm font-semibold text-slate-700">
            Palavra-passe Atual
            <input
              required
              type="password"
              name="senha"
              placeholder="••••••••"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm shadow-sm outline-none focus:border-sky-500 focus:bg-white"
            />
          </label>
        </div>
        <button
          type="submit"
          className="w-full sm:w-auto rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700"
        >
          Guardar Novo E-mail
        </button>
      </form>

      {/* Formulário de Palavra-passe */}
      <form onSubmit={changePassword} className="rounded-2xl border border-slate-200 bg-white p-4 sm:p-6 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-sky-600" />
          <h2 className="text-base sm:text-lg font-bold text-slate-900">Alterar Palavra-passe</h2>
        </div>
        <p className="text-xs text-slate-500">A nova palavra-passe deve conter pelo menos 8 caracteres.</p>
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="block text-xs sm:text-sm font-semibold text-slate-700">
            Palavra-passe Atual
            <input
              required
              type="password"
              name="senha_atual"
              placeholder="••••••••"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm shadow-sm outline-none focus:border-sky-500 focus:bg-white"
            />
          </label>
          <label className="block text-xs sm:text-sm font-semibold text-slate-700">
            Nova Palavra-passe
            <input
              required
              minLength={8}
              type="password"
              name="nova_senha"
              placeholder="Pelo menos 8 caracteres"
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-slate-50/50 px-3.5 py-2.5 text-base sm:text-sm shadow-sm outline-none focus:border-sky-500 focus:bg-white"
            />
          </label>
        </div>
        <button
          type="submit"
          className="w-full sm:w-auto rounded-xl bg-sky-600 px-5 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-sky-700"
        >
          Atualizar Palavra-passe
        </button>
      </form>

      {/* Zona de Perigo */}
      <div className="rounded-2xl border border-red-200 bg-red-50/50 p-4 sm:p-6 space-y-3">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <h2 className="text-base sm:text-lg font-bold text-red-950">Zona de Perigo</h2>
        </div>
        <p className="text-xs sm:text-sm text-red-800 leading-relaxed">
          A eliminação da conta institucional é irreversível. Todas as vagas em aberto e históricos associados serão removidos.
        </p>
        <button
          type="button"
          onClick={() => {
            setDeletePassword("");
            setShowDeleteModal(true);
          }}
          className="w-full sm:w-auto inline-flex items-center justify-center gap-2 rounded-xl border border-red-300 bg-white px-4 py-2.5 text-xs sm:text-sm font-bold text-red-700 shadow-sm transition hover:bg-red-50"
        >
          <Trash2 className="h-4 w-4" />
          Eliminar Conta Permanentemente
        </button>
      </div>

      {/* Modal de Confirmação */}
      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-sm p-4 overflow-y-auto">
          <div role="dialog" aria-modal="true" className="w-full max-w-md rounded-2xl bg-white p-5 sm:p-6 shadow-2xl space-y-4 my-auto">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-red-700 font-bold text-base sm:text-lg">
                <AlertTriangle className="h-5 w-5 shrink-0" />
                Confirmar Eliminação
              </div>
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="rounded-lg p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              Tem a certeza de que deseja eliminar esta conta? Para confirmar esta operação crítica, introduza a sua palavra-passe:
            </p>

            <label className="block text-xs sm:text-sm font-semibold text-slate-700">
              Palavra-passe
              <input
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Introduza a sua palavra-passe"
                className="mt-1.5 w-full rounded-xl border border-slate-200 px-3.5 py-2.5 text-base sm:text-sm shadow-sm outline-none focus:border-red-500 focus:ring-1 focus:ring-red-500"
                autoFocus
              />
            </label>

            <div className="flex flex-col-reverse sm:flex-row justify-end gap-2.5 pt-2">
              <button
                type="button"
                onClick={() => setShowDeleteModal(false)}
                className="w-full sm:w-auto rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-50 transition"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleConfirmDelete}
                disabled={deleting || !deletePassword}
                className="w-full sm:w-auto rounded-xl bg-red-600 px-4 py-2.5 text-sm font-bold text-white shadow-sm hover:bg-red-700 disabled:opacity-50 transition"
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
