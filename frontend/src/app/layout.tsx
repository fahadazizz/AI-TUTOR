import type { Metadata } from "next";
import "./globals.css";
import "katex/dist/katex.min.css"; // Ensure KaTeX styles are globally available

export const metadata: Metadata = {
  title: "AI Tutor — Mathematics",
  description: "A beautifully designed, deeply engaging mathematics tutor.",
};

export const viewport = {
  themeColor: "#151515",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
