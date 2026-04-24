import type { Metadata } from "next";
import { JetBrains_Mono, Poppins } from "next/font/google";

import "./globals.css";

const fontSans = Poppins({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sans",
});

const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

export const metadata: Metadata = {
  title: "MedAssist AI",
  description: "AI-powered symptom guidance with medical knowledge retrieval",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${fontSans.variable} ${fontMono.variable}`}>
        {children}
      </body>
    </html>
  );
}
