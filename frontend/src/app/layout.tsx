import type { Metadata, Viewport } from 'next';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import DemoBanner from '@/components/ui/DemoBanner';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

export const metadata: Metadata = {
  title: 'GaadiLelo.com — Buy Together. Save Together.',
  description: "India's premier vehicle group-buying marketplace. Join forces with buyers in Indore, let authorized dealerships compete, and unlock the lowest transparent on-road price.",
  icons: {
    icon: '/icon.svg',
    shortcut: '/icon.svg',
    apple: '/icon.svg',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="w-full max-w-full overflow-x-hidden">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased w-full max-w-full overflow-x-hidden selection:bg-brand-500 selection:text-white">
        <AuthProvider>
          <DemoBanner />
          <Navbar />
          <main className="flex-1 w-full max-w-full overflow-x-hidden">
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}

