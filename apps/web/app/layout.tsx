import type { Metadata } from "next";
import "../../../packages/design-tokens/generated/tokens.css";
import "../../../packages/design-tokens/generated/direction.css";
import "./globals.css";
import experienceState from "../../../.agentic/experience.json";

export const metadata: Metadata = {
  title: `${experienceState.name} — Product Direction Lab`,
  description: experienceState.promise,
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
