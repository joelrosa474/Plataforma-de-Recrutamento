"use client";

import { Menu } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useSidebar } from "./SidebarContext";
import logoSalu from "@/fotos/Salú (2).png";

export function AdminTopbar() {
  const { toggle } = useSidebar();

  return (
    <header className="h-16 bg-white border-b border-slate-200 flex items-center px-4 sm:px-6 lg:px-8 justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={toggle}
          aria-label="Abrir menu de navegação"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition-colors lg:hidden focus:outline-none focus:ring-2 focus:ring-sky-500"
        >
          <Menu className="h-5 w-5" />
        </button>

        <Link href="/admin/dashboard" aria-label="Ir para o painel do administrador" className="lg:hidden">
          <Image src={logoSalu} alt="É Salú" className="h-9 w-auto" />
        </Link>

        <h1 className="hidden text-sm sm:text-base font-bold text-slate-900 truncate lg:block">
          Painel do Administrador
        </h1>
      </div>

      <div className="flex items-center gap-3">
        <span className="hidden sm:inline-block text-xs font-semibold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
          Super Admin
        </span>
        <div className="w-8 h-8 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center font-bold text-xs shadow-sm">
          AD
        </div>
      </div>
    </header>
  );
}
