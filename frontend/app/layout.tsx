export const metadata = {
  title: "AutoOps",
  description: "Unified multi-agent platform - day 1 skeleton",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}