"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { usePathname, useRouter } from "next/navigation";
import { Briefcase, FileText, User, LogOut, Menu, X } from "lucide-react";
import { getSession, SessionUser } from "@/lib/api";
import { NotificationsPanel } from "@/components/notifications/NotificationsPanel";
import logoSalu from "@/fotos/Salú (2).png";

export function CandidateHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<SessionUser | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (session) {
      setUser(session.user);
    }
  }, []);

  // Fecha o menu móvel ao trocar de rota
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  function handleLogout() {
    window.localStorage.removeItem("rh-session");
    setMobileMenuOpen(false);
    router.push("/");
  }

  const navItems = [
    { name: "Procurar Vagas", href: "/candidate/dashboard", icon: Briefcase },
    { name: "Minhas Candidaturas", href: "/candidate/applications", icon: FileText },
    { name: "Meu Perfil", href: "/candidate/profile", icon: User },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-md shadow-sm">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-4 sm:gap-8">
          {/* Botão Hambúrguer Mobile */}
          <button
            type="button"
            onClick={() => setMobileMenuOpen((prev) => !prev)}
            aria-label={mobileMenuOpen ? "Fechar menu" : "Abrir menu"}
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors md:hidden focus:outline-none focus:ring-2 focus:ring-sky-500"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>

          <Link href="/" className="flex items-center gap-2.5 sm:gap-3" aria-label="Página inicial">
            <Image src={logoSalu} alt="Salú" priority className="h-11 w-auto sm:h-14" />
          </Link>

          {/* Navegação Desktop */}
          <nav className="hidden items-center gap-1 md:flex">
            {navItems.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center gap-2 rounded-lg px-3.5 py-2 text-sm font-semibold transition-colors ${
                    active
                      ? "bg-sky-50 text-sky-700"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-2 sm:gap-4">
          <NotificationsPanel />

          {user && (
            <Link
              href="/candidate/profile"
              className="hidden items-center gap-2 rounded-full bg-slate-100 py-1 pl-1 pr-3 text-xs font-semibold text-slate-700 hover:bg-slate-200/70 sm:inline-flex"
            >
              <span className="flex h-7 w-7 items-center justify-center rounded-full bg-sky-600 text-xs font-bold text-white uppercase">
                {user.nome ? user.nome.charAt(0) : "C"}
              </span>
              <span className="max-w-[120px] truncate">{user.nome}</span>
            </Link>
          )}

          <button
            type="button"
            onClick={handleLogout}
            className="hidden sm:inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-red-50 hover:text-red-700 hover:border-red-200"
            title="Terminar sessão"
          >
            <LogOut className="h-4 w-4" />
            <span>Sair</span>
          </button>
        </div>
      </div>

      {/* Menu Drawer Mobile para Candidatos */}
      {mobileMenuOpen && (
        <div className="border-t border-slate-200 bg-white px-4 py-4 shadow-xl md:hidden transition-all duration-200 animate-in slide-in-from-top-2">
          {user && (
            <div className="mb-4 flex items-center gap-3 border-b border-slate-100 pb-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-full bg-sky-600 text-sm font-bold text-white uppercase">
                {user.nome ? user.nome.charAt(0) : "C"}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-bold text-slate-900 truncate">{user.nome}</p>
                <p className="text-xs text-slate-500 truncate">{user.email}</p>
              </div>
            </div>
          )}

          <nav className="space-y-1">
            {navItems.map((item) => {
              const active = pathname === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-colors ${
                    active
                      ? "bg-sky-50 text-sky-700 font-bold"
                      : "text-slate-700 hover:bg-slate-50"
                  }`}
                >
                  <Icon className={`h-5 w-5 ${active ? "text-sky-600" : "text-slate-400"}`} />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          <div className="mt-4 border-t border-slate-100 pt-3">
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-left text-sm font-semibold text-red-600 hover:bg-red-50 transition"
            >
              <LogOut className="h-5 w-5" />
              Sair da Conta
            </button>
          </div>
        </div>
      )}
    </header>
  );
}
