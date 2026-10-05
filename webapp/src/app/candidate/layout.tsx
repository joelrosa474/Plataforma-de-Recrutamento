import { RouteGuard } from "@/components/auth/RouteGuard";
import { CandidateHeader } from "@/components/layout/CandidateHeader";

export default function CandidateLayout({ children }: { children: React.ReactNode }) {
  return (
    <RouteGuard allowed={["Candidato"]}>
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <CandidateHeader />
        <main className="flex-1 pb-16">{children}</main>
      </div>
    </RouteGuard>
  );
}
