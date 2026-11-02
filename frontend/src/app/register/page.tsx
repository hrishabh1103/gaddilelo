'use client';

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useRouter, useSearchParams } from 'next/navigation';
import { 
  Car, Building2, User, Lock, Mail, Phone, MapPin, 
  ArrowRight, AlertCircle, CheckCircle2 
} from 'lucide-react';
import { useAuth } from '@/context/AuthContext';
import { apiFetch } from '@/lib/api';
import { City } from '@/types';

function RegisterForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialRole = searchParams.get('role') === 'DEALER' ? 'DEALER' : 'BUYER';

  const { register } = useAuth();

  const [role, setRole] = useState<'BUYER' | 'DEALER'>(initialRole);
  const [cities, setCities] = useState<City[]>([]);
  const [cityId, setCityId] = useState('');

  // Form Fields
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');

  // Dealer-specific fields
  const [dealershipName, setDealershipName] = useState('');
  const [gstin, setGstin] = useState('');
  const [address, setAddress] = useState('');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadCities() {
      try {
        const cts = await apiFetch<City[]>('/catalog/cities');
        setCities(cts || []);
        if (cts?.length > 0) {
          const ind = cts.find(c => c.name.toLowerCase() === 'indore') || cts[0];
          setCityId(ind.id);
        }
      } catch (e) {
        console.error(e);
      }
    }
    loadCities();
  }, []);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const payload: any = {
        role,
        full_name: fullName,
        email,
        phone,
        password,
        city_id: cityId,
      };

      if (role === 'DEALER') {
        payload.dealership_name = dealershipName;
        payload.legal_entity_name = dealershipName;
        payload.gstin = gstin.toUpperCase();
        payload.address = address;
        payload.authorized_brands = ['Tata Motors', 'Maruti Suzuki'];
      }

      await register(payload);

      if (role === 'DEALER') {
        router.push('/dealer/dashboard');
      } else {
        router.push('/dashboard');
      }
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[85vh] flex items-center justify-center px-4 py-12">
      <div className="max-w-lg w-full bg-white p-8 rounded-3xl border border-slate-200/80 shadow-lg space-y-6">
        
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-gradient-to-tr from-brand-600 to-brand-500 rounded-2xl flex items-center justify-center text-white mx-auto shadow-md shadow-brand-500/20">
            <Car className="w-6 h-6" />
          </div>
          <h1 className="text-2xl font-black text-navy-950">Create Your Account</h1>
          <p className="text-xs text-slate-500">Join the vehicle group-buying marketplace in Indore, MP</p>
        </div>

        {/* Role Selector Tabs */}
        <div className="grid grid-cols-2 p-1 bg-slate-100 rounded-2xl">
          <button
            type="button"
            onClick={() => setRole('BUYER')}
            className={`py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              role === 'BUYER'
                ? 'bg-white text-navy-950 shadow-sm'
                : 'text-slate-500 hover:text-navy-900'
            }`}
          >
            <User className="w-3.5 h-3.5" /> Vehicle Buyer
          </button>
          <button
            type="button"
            onClick={() => setRole('DEALER')}
            className={`py-2 rounded-xl text-xs font-bold transition-all flex items-center justify-center gap-1.5 ${
              role === 'DEALER'
                ? 'bg-white text-navy-950 shadow-sm'
                : 'text-slate-500 hover:text-navy-900'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" /> OEM Dealership
          </button>
        </div>

        {error && (
          <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          
          <div className="space-y-1">
            <label className="text-xs font-bold text-slate-700">Full Name / Representative Name *</label>
            <input
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              placeholder="e.g. Rahul Sharma"
              className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Email Address *</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@example.com"
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Mobile Phone *</label>
              <input
                type="tel"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="98260XXXXX"
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">Password (min 6 characters) *</label>
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-bold text-slate-700">City (Pilot Territory) *</label>
              <select
                value={cityId}
                onChange={(e) => setCityId(e.target.value)}
                required
                className="w-full text-xs bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-slate-900 focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                {cities.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}, {c.state}</option>
                ))}
              </select>
            </div>
          </div>

          {/* DEALERSHIP SPECIFIC FIELDS */}
          {role === 'DEALER' && (
            <div className="p-4 bg-blue-50/60 rounded-2xl border border-blue-200 space-y-3">
              <h3 className="font-bold text-xs text-blue-900">Dealership Commercial Credentials</h3>
              
              <div className="space-y-1">
                <label className="text-[11px] font-bold text-slate-700">Authorized Dealership Name *</label>
                <input
                  type="text"
                  required
                  value={dealershipName}
                  onChange={(e) => setDealershipName(e.target.value)}
                  placeholder="e.g. Sanghi Brothers Tata Motors"
                  className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-bold text-slate-700">GSTIN Number (15 Characters) *</label>
                <input
                  type="text"
                  required
                  maxLength={15}
                  value={gstin}
                  onChange={(e) => setGstin(e.target.value)}
                  placeholder="23AABCS1234F1Z1"
                  className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 font-mono uppercase text-slate-900 focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[11px] font-bold text-slate-700">Showroom Address in Indore *</label>
                <input
                  type="text"
                  required
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="e.g. Plot 6, A.B. Road, Indore, MP - 452001"
                  className="w-full text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-900 focus:outline-none"
                />
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-1.5"
          >
            {loading ? 'Creating Account...' : `Register as ${role === 'DEALER' ? 'Dealership' : 'Buyer'}`}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-slate-500">
          Already have an account?{' '}
          <Link href="/login" className="text-brand-600 font-bold hover:underline">
            Sign in
          </Link>
        </div>

      </div>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-sm text-slate-400">Loading register...</div>}>
      <RegisterForm />
    </Suspense>
  );
}
