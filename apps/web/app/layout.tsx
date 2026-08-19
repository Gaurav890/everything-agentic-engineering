import type { Metadata } from "next";
import "../../../packages/design-tokens/generated/tokens.css";
import "../../../packages/design-tokens/generated/direction.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "Mara Voss — Portfolio Direction Lab",
  description: "Compare, approve, and compile a product-specific portfolio direction.",
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
