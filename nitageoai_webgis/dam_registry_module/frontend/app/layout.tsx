import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NITA AI Dam Registry",
  description: "Dam registry module for NITA AI Dam Safety Intelligence Platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

