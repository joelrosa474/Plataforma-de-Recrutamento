import { Sidebar } from "@/components/layout/Sidebar";
import { RouteGuard } from "@/components/auth/RouteGuard";
import { CompanyTopbar } from "@/components/layout/CompanyTopbar";
import { SidebarProvider } from "@/components/layout/SidebarContext";

export default function CompanyLayout({ children }: { children: React.ReactNode }) {
  return (
    <RouteGuard allowed={["Empresa"]}>
      <SidebarProvider>
        <div className="min-h-screen bg-slate-50 flex flex-col">
          <Sidebar role="company" />
          <div className="lg:pl-64 flex flex-col flex-1 w-full min-w-0 transition-all">
            <CompanyTopbar />
            <main className="p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto flex-1">{children}</main>
          </div>
        </div>
      </SidebarProvider>
    </RouteGuard>
  );
}
