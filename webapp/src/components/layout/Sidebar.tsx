"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, Users, FileText, Settings, LogOut, Briefcase, ShieldCheck } from "lucide-react";

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
    router.push("/");
  }

  return (
    <aside className="fixed left-0 top-0 z-30 flex h-screen w-64 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-16 items-center px-6 border-b border-slate-200">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="flex h-8 w-8 items-end justify-center gap-0.5 rounded-lg bg-sky-50 px-1.5 py-1.5">
            <span className="h-4 w-1.5 rounded-full bg-sky-600" />
            <span className="h-6 w-1.5 rounded-full bg-sky-500" />
            <span className="h-3.5 w-1.5 rounded-full bg-sky-400" />
          </span>
          <span className="text-xl font-bold tracking-tight text-slate-950">É Salú</span>
        </Link>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-6">
        {navItems.map((item) => {
          const Icon = item.icon;
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3.5 py-2.5 text-sm font-semibold transition-colors ${
                active
                  ? "bg-sky-50 text-sky-700 font-bold"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
              }`}
            >
              <Icon className={`h-4 w-4 ${active ? "text-sky-600" : "text-slate-400"}`} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-200">
        <button
          type="button"
          onClick={handleLogout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-sm font-semibold text-slate-600 hover:bg-red-50 hover:text-red-700 transition-colors"
        >
          <LogOut className="h-4 w-4 text-slate-400 group-hover:text-red-600" />
          Sair
        </button>
      </div>
    </aside>
  );
}
