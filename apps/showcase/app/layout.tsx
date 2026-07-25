import type { Metadata } from "next";
import "../../../packages/design-tokens/generated/tokens.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Signalroom — Agent Operations",
  description:
    "A human-first mission control for supervising long-running AI agent work.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
