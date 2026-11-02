'use client';

import React from 'react';
import { useAuth } from '@/context/AuthContext';
import { Shield, UserCheck, Building2, LogOut } from 'lucide-react';

export default function DemoBanner() {
  const { user, quickLoginDemo, logout } = useAuth();

  return (
    <div className="bg-navy-900 border-b border-navy-800 text-xs text-navy-300 py-1.5 px-4">
      <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-brand-500/20 text-brand-400 border border-brand-500/30">
            PILOT: INDORE, MP
          </span>
          <span className="hidden sm:inline text-navy-400">
            Active Persona: <strong className="text-white">{user ? `${user.full_name} (${user.role})` : 'Guest Visitor'}</strong>
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-navy-400 hidden md:inline">Quick Switch Demo Persona:</span>
          <button
            onClick={() => quickLoginDemo('BUYER')}
            className={`px-2 py-0.5 rounded font-medium transition-colors flex items-center gap-1 ${
              user?.role === 'BUYER'
                ? 'bg-brand-500 text-white'
                : 'bg-navy-800 hover:bg-navy-700 text-navy-200'
            }`}
          >
            <UserCheck className="w-3 h-3" /> Buyer (Rahul)
          </button>
          <button
            onClick={() => quickLoginDemo('DEALER')}
            className={`px-2 py-0.5 rounded font-medium transition-colors flex items-center gap-1 ${
              user?.role === 'DEALER'
                ? 'bg-blue-600 text-white'
                : 'bg-navy-800 hover:bg-navy-700 text-navy-200'
            }`}
          >
            <Building2 className="w-3 h-3" /> Dealer (Sanghi)
          </button>
          <button
            onClick={() => quickLoginDemo('ADMIN')}
            className={`px-2 py-0.5 rounded font-medium transition-colors flex items-center gap-1 ${
              user?.role === 'ADMIN'
                ? 'bg-purple-600 text-white'
                : 'bg-navy-800 hover:bg-navy-700 text-navy-200'
            }`}
          >
            <Shield className="w-3 h-3" /> Admin (Ops)
          </button>

          {user && (
            <button
              onClick={logout}
              className="text-navy-400 hover:text-red-400 ml-1 p-0.5"
              title="Sign Out"
            >
              <LogOut className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

