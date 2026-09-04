import type { Metadata } from "next";
import "./globals.css";
import "katex/dist/katex.min.css"; // Ensure KaTeX styles are globally available

export const metadata: Metadata = {
  title: "AI Tutor — Mathematics",
  description: "A beautifully designed, deeply engaging mathematics tutor.",
  themeColor: "#151515",
  viewport: "width=device-width, initial-scale=1, maximum-scale=1",
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
