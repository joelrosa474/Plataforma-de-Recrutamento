"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { getSession } from "@/lib/api";

type Role = "Candidato" | "Empresa" | "Administrador";

export function RouteGuard({ allowed, children }: { allowed: Role[]; children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [allowedHere, setAllowedHere] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.replace(`/auth?next=${encodeURIComponent(pathname)}`);
      return;
    }
    if (!allowed.includes(session.user.tipo_perfil as Role)) {
      router.replace(session.user.tipo_perfil === "Empresa" ? "/company/dashboard" : "/candidate/dashboard");
      return;
    }
    setAllowedHere(true);
  }, [allowed, pathname, router]);

  if (!allowedHere) return <div className="grid min-h-screen place-items-center bg-slate-50 text-sm text-slate-600">A verificar sessão…</div>;
  return <>{children}</>;
}
