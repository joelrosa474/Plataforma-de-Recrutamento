import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "É Salú",
  description: "A principal plataforma de recrutamento de Angola",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
