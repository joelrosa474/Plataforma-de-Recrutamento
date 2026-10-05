import { Sidebar } from "@/components/layout/Sidebar";
import { RouteGuard } from "@/components/auth/RouteGuard";
import { CompanyTopbar } from "@/components/layout/CompanyTopbar";

export default function CompanyLayout({ children }: { children: React.ReactNode }) {
  return (
    <RouteGuard allowed={["Empresa"]}>
      <div className="min-h-screen bg-slate-50">
        <Sidebar role="company" />
        <div className="pl-64">
          <CompanyTopbar />
          <main className="p-8 max-w-7xl">{children}</main>
        </div>
      </div>
    </RouteGuard>
  );
}
