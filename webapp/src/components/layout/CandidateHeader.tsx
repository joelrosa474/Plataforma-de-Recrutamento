"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Briefcase, FileText, User, LogOut } from "lucide-react";
import { getSession, SessionUser } from "@/lib/api";
import { NotificationsPanel } from "@/components/notifications/NotificationsPanel";

export function CandidateHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<SessionUser | null>(null);

  useEffect(() => {
    const session = getSession();
    if (session) {
      setUser(session.user);
    }
  }, []);

  function handleLogout() {
    window.localStorage.removeItem("rh-session");
    router.push("/");
  }

  const navItems = [
    { name: "Procurar Vagas", href: "/candidate/dashboard", icon: Briefcase },
    { name: "Minhas Candidaturas", href: "/candidate/applications", icon: FileText },
    { name: "Meu Perfil", href: "/candidate/profile", icon: User },
  ];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white shadow-sm">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-3" aria-label="Página inicial">
            <span className="flex h-10 w-10 items-end justify-center gap-1 rounded-lg bg-sky-50 px-2 py-2">
              <span className="h-6 w-2 rounded-full bg-sky-600" />
              <span className="h-8 w-2 rounded-full bg-sky-500" />
              <span className="h-5 w-2 rounded-full bg-sky-400" />
            </span>
            <span className="text-2xl font-bold tracking-tight text-slate-950">É Salú</span>
          </Link>

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

        <div className="flex items-center gap-4">
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
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-600 shadow-sm transition hover:bg-red-50 hover:text-red-700 hover:border-red-200"
            title="Terminar sessão"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline">Sair</span>
          </button>
        </div>
      </div>
    </header>
  );
}
