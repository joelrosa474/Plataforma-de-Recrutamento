import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "É Salú - Plataforma de Recrutamento RH",
  description: "A principal plataforma de recrutamento e gestão de talentos de Angola",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#0284c7",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-AO">
      <body className="font-sans antialiased text-slate-900 bg-slate-50 selection:bg-sky-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
