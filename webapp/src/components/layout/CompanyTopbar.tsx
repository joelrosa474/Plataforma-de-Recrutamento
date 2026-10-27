"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { Menu } from "lucide-react";
import { getSession, SessionUser } from "@/lib/api";
import { NotificationsPanel } from "@/components/notifications/NotificationsPanel";
import { useSidebar } from "./SidebarContext";
import logoSalu from "@/fotos/Salú (2).png";

export function CompanyTopbar() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const { toggle } = useSidebar();

  useEffect(() => {
    const session = getSession();
    if (session) {
      setUser(session.user);
    }
  }, []);

  const initials = user?.nome
    ? user.nome
        .split(" ")
        .slice(0, 2)
        .map((w) => w.charAt(0))
        .join("")
        .toUpperCase()
    : "EM";

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-4 sm:px-6 lg:px-8 justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        {/* Botão Hambúrguer Mobile / Tablet */}
        <button
          type="button"
          onClick={toggle}
          aria-label="Abrir menu de navegação"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors lg:hidden focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <Menu className="h-5 w-5" />
        </button>

        <Link href="/company/dashboard" aria-label="Ir para o painel da empresa" className="lg:hidden">
          <Image src={logoSalu} alt="É Salú" className="h-9 w-auto" />
        </Link>

        <h1 className="hidden text-sm sm:text-base font-bold text-slate-900 truncate lg:block">
          Painel da Empresa
        </h1>
      </div>

      <div className="flex items-center gap-2 sm:gap-4">
        <NotificationsPanel />
        <Link
          href="/company/profile"
          className="flex items-center gap-2.5 rounded-full py-1 pl-1 pr-2 sm:pr-3 hover:bg-slate-50 transition"
          title="Ver perfil da empresa"
        >
          <div className="w-8 h-8 bg-sky-100 text-sky-700 rounded-full flex items-center justify-center text-xs font-bold uppercase shadow-sm">
            {initials}
          </div>
          <span className="hidden md:inline text-xs font-semibold text-slate-700 max-w-[140px] truncate">
            {user?.nome ?? "Empresa"}
          </span>
        </Link>
      </div>
    </header>
  );
}
