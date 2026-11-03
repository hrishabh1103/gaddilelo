import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Car } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center px-4 text-center">
      <div className="w-16 h-16 rounded-3xl bg-orange-50 text-brand-600 flex items-center justify-center mb-6 shadow-sm">
        <Car className="w-8 h-8" />
      </div>
      <span className="text-xs font-black uppercase tracking-widest text-brand-600 mb-2">404 — Road Ends Here</span>
      <h1 className="text-3xl sm:text-4xl font-black text-navy-950 mb-3">Vehicle or Page Not Found</h1>
      <p className="text-sm text-slate-500 max-w-md mb-8">
        The vehicle, group, or page you are looking for has been moved or is no longer active in the Indore pilot catalogue.
      </p>
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="px-5 py-2.5 bg-navy-950 hover:bg-navy-900 text-white font-bold text-xs rounded-xl shadow-sm transition-colors flex items-center gap-2"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Home
        </Link>
        <Link
          href="/vehicles"
          className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl shadow-sm transition-colors"
        >
          Browse All Vehicles
        </Link>
      </div>
    </div>
  );
}

