import { Sidebar } from "@/components/layout/Sidebar";
import { RouteGuard } from "@/components/auth/RouteGuard";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <RouteGuard allowed={["Administrador"]}><div className="min-h-screen bg-slate-50">
      <Sidebar role="admin" />
      <div className="pl-64">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-8 justify-between">
          <h1 className="text-lg font-semibold text-slate-800">Painel do Administrador</h1>
          <div className="w-8 h-8 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center font-bold">
            AD
          </div>
        </header>
        <main className="p-8">{children}</main>
      </div>
    </div></RouteGuard>
  );
}
