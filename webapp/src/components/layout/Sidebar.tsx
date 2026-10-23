"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  LayoutDashboard,
  Users,
  FileText,
  Settings,
  LogOut,
  Briefcase,
  ShieldCheck,
  X,
} from "lucide-react";
import { useSidebar } from "./SidebarContext";

interface SidebarProps {
  role: "admin" | "company" | "candidate";
}

type NavItem = {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
};

export function Sidebar({ role }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();
  const { isOpen, close } = useSidebar();

  let navItems: NavItem[] = [];

  if (role === "company") {
    navItems = [
      { name: "Painel de Controlo", href: "/company/dashboard", icon: LayoutDashboard },
      { name: "Minhas Vagas", href: "/company/jobs", icon: Briefcase },
      { name: "Candidatos (ATS)", href: "/company/candidates", icon: Users },
      { name: "Perfil da Empresa", href: "/company/profile", icon: Briefcase },
      { name: "Configurações", href: "/company/settings", icon: Settings },
    ];
  } else if (role === "candidate") {
    navItems = [
      { name: "Procurar Vagas", href: "/candidate/dashboard", icon: LayoutDashboard },
      { name: "Minhas Candidaturas", href: "/candidate/applications", icon: FileText },
      { name: "Meu Perfil", href: "/candidate/profile", icon: Users },
    ];
  } else {
    navItems = [
      { name: "Dashboard Admin", href: "/admin/dashboard", icon: LayoutDashboard },
      { name: "Gestão de Utilizadores", href: "/admin/users", icon: Users },
      { name: "Moderação de Vagas", href: "/admin/moderation", icon: ShieldCheck },
    ];
  }

  function handleLogout() {
    window.localStorage.removeItem("rh-session");
    close();
    router.push("/");
  }

  return (
    <>
      {/* Backdrop escuro translúcido para Mobile / Tablet */}
      {isOpen && (
        <div
          onClick={close}
          className="fixed inset-0 z-40 bg-slate-900/60 backdrop-blur-sm transition-opacity duration-300 lg:hidden"
          aria-hidden="true"
        />
      )}

      {/* Sidebar Lateral */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 flex h-full w-72 flex-col border-r border-slate-200 bg-white shadow-xl transition-transform duration-300 ease-in-out lg:z-30 lg:w-64 lg:shadow-none lg:translate-x-0 ${
          isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
        }`}
      >
        {/* Cabeçalho da Sidebar */}
        <div className="flex h-16 items-center justify-between px-6 border-b border-slate-200">
          <Link href="/" onClick={close} className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-end justify-center gap-0.5 rounded-lg bg-sky-50 px-1.5 py-1.5">
              <span className="h-4 w-1.5 rounded-full bg-sky-600" />
              <span className="h-6 w-1.5 rounded-full bg-sky-500" />
              <span className="h-3.5 w-1.5 rounded-full bg-sky-400" />
            </span>
            <span className="text-xl font-bold tracking-tight text-slate-950">É Salú</span>
          </Link>

          {/* Botão de Fechar para Mobile / Tablet */}
          <button
            type="button"
            onClick={close}
            aria-label="Fechar menu"
            className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 hover:bg-slate-100 hover:text-slate-800 transition lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Links de Navegação */}
        <nav className="flex-1 space-y-1.5 px-3 py-6 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={close}
                className={`flex items-center gap-3 rounded-xl px-3.5 py-2.5 text-sm font-semibold transition-all ${
                  active
                    ? "bg-sky-50 text-sky-700 font-bold shadow-sm"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? "text-sky-600" : "text-slate-400"}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Rodapé / Botão de Logout */}
        <div className="p-4 border-t border-slate-200 bg-slate-50/50">
          <button
            type="button"
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-xl px-3.5 py-2.5 text-left text-sm font-semibold text-slate-600 hover:bg-red-50 hover:text-red-700 transition-colors"
          >
            <LogOut className="h-4 w-4 text-slate-400 group-hover:text-red-600" />
            Sair da Sessão
          </button>
        </div>
      </aside>
    </>
  );
}
