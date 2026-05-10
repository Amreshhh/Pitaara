// app/layout.js
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Footer from "../components/Footer";

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

// Yeh line sabse important hai Next.js ke liye!
export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased transition-colors duration-600 ease-in-out`}>
        {children}
        <Footer />
      </body>
    </html>
  );
}