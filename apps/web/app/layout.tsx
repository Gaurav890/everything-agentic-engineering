import type { Metadata } from "next";
import "../../../packages/design-tokens/generated/tokens.css";
import "../../../packages/design-tokens/generated/direction.css";
import "./globals.css";
import experienceState from "../../../.agentic/experience.json";
import {getProjectBrief} from "./project-brief.server";

export function generateMetadata(): Metadata {
  let brief;
  try {
    brief = getProjectBrief();
  } catch {
    // The page error boundary explains recovery without exposing context data.
    return {title: "Project workspace — needs attention"};
  }
  return {
    title: brief ? `${brief.name} — Project workspace` : `${experienceState.name} — Product Direction Lab`,
    description: brief?.promise ?? experienceState.promise,
  };
}

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
