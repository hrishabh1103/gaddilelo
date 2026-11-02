import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/context/AuthContext';
import DemoBanner from '@/components/ui/DemoBanner';
import Navbar from '@/components/layout/Navbar';
import Footer from '@/components/layout/Footer';

export const metadata: Metadata = {
  title: 'GaadiLelo.com — Buy Together. Save Together.',
  description: "India's premier vehicle group-buying marketplace. Join forces with buyers in Indore, let authorized dealerships compete, and unlock the lowest transparent on-road price.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col bg-slate-50 text-slate-900 antialiased">
        <AuthProvider>
          <DemoBanner />
          <Navbar />
          <main className="flex-1">
            {children}
          </main>
          <Footer />
        </AuthProvider>
      </body>
    </html>
  );
}

