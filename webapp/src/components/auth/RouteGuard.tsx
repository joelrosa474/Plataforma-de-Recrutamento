"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, clearSession, getSession, saveSession } from "@/lib/api";

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
    let active = true;
    setAllowedHere(false);

    // A fonte de verdade da sessão e do perfil é o backend; o localStorage só
    // conserva os dados necessários para renderizar a navegação.
    api.myProfile()
      .then((user) => {
        if (!active) return;
        saveSession(undefined, user);
        if (!allowed.includes(user.tipo_perfil as Role)) {
          router.replace(user.tipo_perfil === "Empresa" ? "/company/dashboard" : "/candidate/dashboard");
          return;
        }
        setAllowedHere(true);
      })
      .catch(() => {
        if (!active) return;
        clearSession();
        router.replace(`/auth?next=${encodeURIComponent(pathname)}`);
      });

    return () => {
      active = false;
    };
  }, [allowed, pathname, router]);

  if (!allowedHere) return <div className="grid min-h-screen place-items-center bg-slate-50 text-sm text-slate-600">A verificar sessão…</div>;
  return <>{children}</>;
}
