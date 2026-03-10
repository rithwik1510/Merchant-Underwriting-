import type { Metadata } from "next";
import { Outfit, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopBar } from "@/components/layout/TopBar";
import { PageTransition } from "@/components/layout/PageTransition";
import { TooltipProvider } from "@/components/ui/tooltip";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  weight: ["400", "500", "600", "700", "800", "900"],
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-jakarta",
  weight: ["300", "400", "500", "600", "700", "800"],
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
  weight: ["400", "500", "600", "700"],
});

export const metadata: Metadata = {
  title: "GrabOn Underwriting Engine",
  description: "Merchant credit and insurance underwriting - Internal Operations",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `(() => {
              try {
                const saved = localStorage.getItem("grabon-theme");
                const theme = saved === "light" ? "light" : "dark";
                document.documentElement.classList.toggle("dark", theme === "dark");
              } catch (_) {
                document.documentElement.classList.add("dark");
              }
            })();`,
          }}
        />
      </head>
      <body
        className={`${outfit.variable} ${jakarta.variable} ${jetbrains.variable} antialiased`}
      >
        <TooltipProvider>
          <div className="flex min-h-screen bg-surface-base">
            <Sidebar />
            <div className="ml-72 flex min-h-screen flex-1 flex-col">
              <TopBar />
              <main className="flex-1 overflow-y-auto">
                <PageTransition>{children}</PageTransition>
              </main>
            </div>
          </div>
        </TooltipProvider>
      </body>
    </html>
  );
}
