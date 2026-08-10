import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppLayout } from "@/components/layout/AppLayout";
import { AuthProvider } from "@/contexts/AuthContext";
import { MonitoringProvider } from "@/contexts/MonitoringContext";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "OneForAll AI | Manufacturing Intelligence",
  description: "Manufacturing intelligence that turns operational data into decisions.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <AuthProvider>
          <MonitoringProvider>
            <AppLayout>{children}</AppLayout>
          </MonitoringProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
