"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { api, clearSession, getSession, saveSession } from "@/lib/api";

type Role = "Candidato" | "Empresa" | "Administrador";

export function RouteGuard({ allowed, children }: { allowed: Role[]; children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [allowedHere, setAllowedHere] = useState(false);
  const allowedKey = allowed.join(",");

  useEffect(() => {
    const session = getSession();
    if (!session) {
      router.replace(`/auth?next=${encodeURIComponent(pathname)}`);
      return;
    }
    let active = true;
    setAllowedHere(false);

    // A fonte de verdade da sessão e do perfil é o backend; o localStorage
    // conserva os dados necessários para o cliente e para a navegação.
    api.myProfile()
      .then((user) => {
        if (!active) return;
        saveSession(session.token, user);
        if (!allowed.includes(user.tipo_perfil as Role)) {
          const dest =
            user.tipo_perfil === "Empresa"
              ? "/company/dashboard"
              : user.tipo_perfil === "Administrador"
              ? "/admin/dashboard"
              : "/candidate/dashboard";
          router.replace(dest);
          return;
        }
        setAllowedHere(true);
      })
      .catch((err) => {
        if (!active) return;
        // Se a sessão local existe e confere com a role permitida, mantém o acesso caso haja instabilidade de rede ou cold start
        if (session.user && allowed.includes(session.user.tipo_perfil as Role) && err?.code === "network_error") {
          setAllowedHere(true);
          return;
        }
        clearSession();
        router.replace(`/auth?next=${encodeURIComponent(pathname)}`);
      });

    return () => {
      active = false;
    };
  }, [allowedKey, pathname, router]);

  if (!allowedHere) return <div className="grid min-h-screen place-items-center bg-slate-50 text-sm text-slate-600">A verificar sessão…</div>;
  return <>{children}</>;
}
