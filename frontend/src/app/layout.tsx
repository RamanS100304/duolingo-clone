import type { Metadata, Viewport } from "next";
import { ToastProvider } from "@/components/ui";
import { UserProvider } from "@/lib/user-context";
import "./globals.css";

export const metadata: Metadata = { title: "lingua - learn English", description: "A Duolingo-style English course for Hindi speakers" };
export const viewport: Viewport = { width: "device-width", initialScale: 1 };

// Runs before first paint so the saved theme is applied without a flash.
const themeScript = `try{var t=localStorage.getItem('theme');if(t==='dark'||(!t&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.dataset.theme='dark'}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head><script dangerouslySetInnerHTML={{ __html: themeScript }} /></head>
      <body>
        <UserProvider>
          <ToastProvider>{children}</ToastProvider>
        </UserProvider>
      </body>
    </html>
  );
}
