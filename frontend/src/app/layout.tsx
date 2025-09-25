import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { Theme } from "@radix-ui/themes";
import "@radix-ui/themes/styles.css";
import { Header } from "@/1_widgets/header";
import "./globals.css";
import { UserProvider } from "@/4_shared/hooks/useUser";

export const metadata: Metadata = {
  title: "Клинические рекомендации",
  description: "Сделано в ШГПУ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <Theme accentColor="blue" radius="large">
          <UserProvider>
            <Header />
            {children}
          </UserProvider>
        </Theme>
      </body>
    </html>
  );
}
