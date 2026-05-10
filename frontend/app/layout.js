// app/layout.js
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Footer from "../components/Footer";
import BottomNav from "../components/BottomNav";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: "Om-Rani",
  description:
    "Find the best value. Compare live gold rates and making charges across India's leading jewelry brands.",
};

export const viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  themeColor: '#f59e0b',
  viewportFit: 'cover',
};

// Yeh line sabse important hai Next.js ke liye!
export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#f59e0b" />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased transition-colors duration-600 ease-in-out`}>
        {children}
        <BottomNav />
        <Footer />
      </body>
    </html>
  );
}