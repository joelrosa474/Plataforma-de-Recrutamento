import type { Metadata, Viewport } from "next";
import "./globals.css";
import { ThemeToggle } from "@/components/layout/ThemeToggle";

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
    <html lang="pt-AO" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: "(function(){try{var t=localStorage.getItem('rh-theme');var d=t?t==='dark':window.matchMedia('(prefers-color-scheme: dark)').matches;document.documentElement.classList.toggle('dark',d);document.documentElement.style.colorScheme=d?'dark':'light'}catch(e){}})()",
          }}
        />
      </head>
      <body className="font-sans antialiased bg-background text-foreground selection:bg-sky-500 selection:text-white">
        {children}
        <ThemeToggle />
      </body>
    </html>
  );
}
