import "./globals.css";

export const metadata = {
  title: "AutoOps | Unified business automation",
  description: "A unified multi-agent platform for business operations.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <html lang="en"><body>{children}</body></html>;
}