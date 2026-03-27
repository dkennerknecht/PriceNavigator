import type { Metadata } from "next";
import { Space_Grotesk, Work_Sans } from "next/font/google";
import Link from "next/link";

import "./globals.css";

const headingFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-heading",
});

const bodyFont = Work_Sans({
  subsets: ["latin"],
  variable: "--font-body",
});

export const metadata: Metadata = {
  title: "PriceNavigator",
  description: "Produktaufnahme, Angebote und Einkaufslisten mit deterministischer Optimierung.",
};

const navigation = [
  { href: "/", label: "Dashboard" },
  { href: "/products", label: "Produkte" },
  { href: "/product-sources", label: "Quellen" },
  { href: "/offers", label: "Angebote" },
  { href: "/shops", label: "Shops" },
  { href: "/shopping-lists", label: "Einkaufslisten" },
];

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="de">
      <body className={`${headingFont.variable} ${bodyFont.variable}`}>
        <div className="app-shell">
          <header className="topbar">
            <Link href="/" className="brandmark">
              <span className="brand-badge">PN</span>
              <div>
                <strong>PriceNavigator</strong>
                <small>Produkterfassung, Offers und Shop-Penalty</small>
              </div>
            </Link>
            <nav className="nav-links">
              {navigation.map((item) => (
                <Link key={item.href} href={item.href}>
                  {item.label}
                </Link>
              ))}
            </nav>
          </header>
          <main className="page-shell">{children}</main>
        </div>
      </body>
    </html>
  );
}

