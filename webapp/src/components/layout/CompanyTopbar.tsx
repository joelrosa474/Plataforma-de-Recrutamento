"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getSession, SessionUser } from "@/lib/api";
import { NotificationsPanel } from "@/components/notifications/NotificationsPanel";

export function CompanyTopbar() {
  const [user, setUser] = useState<SessionUser | null>(null);

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
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-8 justify-between sticky top-0 z-20">
      <h1 className="text-base font-bold text-slate-900">Painel da Empresa</h1>
      <div className="flex items-center gap-4">
        <NotificationsPanel />
        <Link
          href="/company/profile"
          className="flex items-center gap-2.5 rounded-full py-1 pl-1 pr-3 hover:bg-slate-50 transition"
          title="Ver perfil da empresa"
        >
          <div className="w-8 h-8 bg-sky-100 text-sky-700 rounded-full flex items-center justify-center text-xs font-bold uppercase shadow-sm">
            {initials}
          </div>
          <span className="hidden sm:inline text-xs font-semibold text-slate-700 max-w-[140px] truncate">
            {user?.nome ?? "Empresa"}
          </span>
        </Link>
      </div>
    </header>
  );
}
