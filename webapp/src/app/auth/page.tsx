"use client";

import { FormEvent, Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api, saveSession, SessionUser } from "@/lib/api";

export default function AuthPage() {
  return (
    <Suspense fallback={<main className="flex min-h-screen items-center justify-center bg-slate-50 px-5"><div className="text-slate-600">A carregar…</div></main>}>
      <AuthPageContent />
    </Suspense>
  );
}

function AuthPageContent() {
  const searchParams = useSearchParams();
  const [mode, setMode] = useState<"login" | "register" | "forgot" | "reset">("login");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [debugLink, setDebugLink] = useState("");
  const router = useRouter();

  useEffect(() => {
    const qMode = searchParams.get("mode");
    const qToken = searchParams.get("token");
    if (qMode === "reset" || qToken) {
      setMode("reset");
      if (qToken) setResetToken(qToken);
    } else if (qMode === "register") {
      setMode("register");
    }
  }, [searchParams]);

  function validatePassword(senha: string): string {
    const bytes = new TextEncoder().encode(senha).length;
    if (bytes > 72) {
      return "A palavra-passe não pode exceder 72 bytes. Use uma senha mais curta.";
    }
    if (senha.length < 8) {
      return "A palavra-passe deve ter pelo menos 8 caracteres.";
    }
    return "";
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setSuccessMessage("");
    setDebugLink("");

    const data = new FormData(event.currentTarget);
    const email = String(data.get("email") || "");
    const senha = String(data.get("senha") || "");

    try {
      if (mode === "forgot") {
        const res = await api.requestPasswordReset(email);
        setSuccessMessage(res.message);
        if (res.debug_token) {
          setDebugLink(`/auth?mode=reset&token=${res.debug_token}`);
        }
        return;
      }

      if (mode === "reset") {
        const tokenVal = String(data.get("token") || resetToken);
        const novaSenha = String(data.get("nova_senha") || "");
        const pwError = validatePassword(novaSenha);
        if (pwError) {
          setError(pwError);
          return;
        }
        const res = await api.resetPassword(tokenVal, novaSenha);
        setSuccessMessage(res.message);
        setMode("login");
        return;
      }

      if (mode === "register") {
        const passwordError = validatePassword(senha);
        if (passwordError) {
          setError(passwordError);
          return;
        }
        await api.register({
          nome: String(data.get("nome")),
          email,
          senha,
          tipo_perfil: String(data.get("tipo_perfil")),
        });
      }

      // Login
      const tokenData = await api.login(email, senha);
      const user: SessionUser = tokenData.usuario;
      saveSession(tokenData.access_token, user);
      router.push(
        searchParams.get("next") ??
          (user.tipo_perfil === "Administrador"
            ? "/admin/dashboard"
            : user.tipo_perfil === "Empresa"
            ? "/company/dashboard"
            : "/candidate/dashboard")
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ocorreu um erro inesperado.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-50 px-5 py-8">
      <section className="w-full max-w-md rounded-xl border border-slate-200 bg-white p-7 shadow-sm">
        <Link href="/" className="text-xl font-bold text-sky-700">
          É Salú
        </Link>

        <h1 className="mt-6 text-2xl font-bold text-slate-950">
          {mode === "login" && "Entre na sua conta"}
          {mode === "register" && "Crie a sua conta"}
          {mode === "forgot" && "Recuperar palavra-passe"}
          {mode === "reset" && "Definir nova palavra-passe"}
        </h1>

        <p className="mt-2 text-sm text-slate-600">
          {mode === "login" && "Aceda às vagas e acompanhe o seu processo de recrutamento."}
          {mode === "register" && "Junte-se à plataforma como candidato ou recrutador."}
          {mode === "forgot" && "Indique o seu e-mail para receber um link de redefinição."}
          {mode === "reset" && "Insira o token de segurança e a sua nova palavra-passe."}
        </p>

        {successMessage && (
          <div className="mt-4 rounded-md bg-emerald-50 p-3 text-sm text-emerald-800 border border-emerald-200">
            {successMessage}
            {debugLink && (
              <div className="mt-2 pt-2 border-t border-emerald-200">
                <span className="text-xs text-emerald-600 block mb-1">Ambiente Local (Atalho):</span>
                <Link href={debugLink} className="font-semibold underline text-emerald-800 text-xs hover:text-emerald-950">
                  Clique aqui para preencher o formulário de redefinição automaticamente
                </Link>
              </div>
            )}
          </div>
        )}

        <form onSubmit={submit} className="mt-6 space-y-4">
          {mode === "register" && (
            <>
              <label className="block text-sm font-medium text-slate-700">
                Nome completo
                <input required name="nome" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none" />
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Tipo de Perfil
                <select name="tipo_perfil" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none">
                  <option value="Candidato">Candidato</option>
                  <option value="Empresa">Empresa (Recrutador)</option>
                </select>
              </label>
            </>
          )}

          {mode !== "reset" && (
            <label className="block text-sm font-medium text-slate-700">
              E-mail
              <input required type="email" name="email" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none" />
            </label>
          )}

          {(mode === "login" || mode === "register") && (
            <div>
              <label className="block text-sm font-medium text-slate-700">Palavra-passe</label>
              <input required type="password" name="senha" className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none" />
            </div>
          )}

          {mode === "reset" && (
            <>
              <label className="block text-sm font-medium text-slate-700">
                Token de Recuperação
                <input
                  required
                  name="token"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  placeholder="Cole aqui o token recebido"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 font-mono text-xs text-slate-900 focus:border-sky-500 focus:outline-none"
                />
              </label>
              <label className="block text-sm font-medium text-slate-700">
                Nova Palavra-passe
                <input
                  required
                  type="password"
                  name="nova_senha"
                  placeholder="Mínimo 8 caracteres"
                  className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-slate-900 focus:border-sky-500 focus:outline-none"
                />
              </label>
            </>
          )}

          {error && <p role="alert" className="rounded-md bg-red-50 p-3 text-sm text-red-700 border border-red-200">{error}</p>}

          <button
            disabled={loading}
            className="w-full rounded-md bg-sky-600 py-2.5 text-sm font-bold text-white transition hover:bg-sky-700 disabled:opacity-60"
          >
            {loading ? "A processar…" : mode === "login" ? "Entrar" : mode === "register" ? "Criar conta" : mode === "forgot" ? "Enviar link de recuperação" : "Redefinir palavra-passe"}
          </button>

          {mode === "login" && (
            <div className="text-center">
              <button
                type="button"
                onClick={() => { setMode("forgot"); setError(""); setSuccessMessage(""); }}
                className="text-xs font-semibold text-slate-500 hover:text-sky-700 hover:underline transition"
              >
                Esqueceu-se da palavra-passe?
              </button>
            </div>
          )}
        </form>

        <div className="mt-6 flex flex-col space-y-2 border-t border-slate-100 pt-4 text-sm">
          {mode === "login" && (
            <button
              onClick={() => { setMode("register"); setError(""); setSuccessMessage(""); }}
              className="text-left font-semibold text-sky-700 hover:underline"
            >
              Ainda não tem conta? Registe-se
            </button>
          )}

          {mode !== "login" && (
            <button
              onClick={() => { setMode("login"); setError(""); setSuccessMessage(""); }}
              className="text-left font-semibold text-sky-700 hover:underline"
            >
              Já tem conta? Voltar ao login
            </button>
          )}
        </div>
      </section>
    </main>
  );
}
