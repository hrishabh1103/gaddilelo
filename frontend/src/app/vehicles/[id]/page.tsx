'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { 
  Car, ShieldCheck, Zap, Users, ArrowRight, CheckCircle2, 
  MapPin, Sparkles, ChevronRight, Fuel, Gauge, Award, Info
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { VehicleVariant, BuyingGroup } from '@/types';

export default function VehicleDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = params?.id as string;

  const [vehicle, setVehicle] = useState<any>(null);
  const [selectedVariant, setSelectedVariant] = useState<VehicleVariant | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadVehicle() {
      try {
        const data = await apiFetch(`/catalog/models/${id}`);
        setVehicle(data);
        if (data?.variants?.length > 0) {
          setSelectedVariant(data.variants[0]);
        }
      } catch (err) {
        console.error('Failed to load vehicle:', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadVehicle();
  }, [id]);

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-400">
        Loading vehicle details...
      </div>
    );
  }

  if (!vehicle) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center text-sm text-slate-500">
        Vehicle not found. <Link href="/vehicles" className="text-brand-600 underline">Browse catalogue</Link>
      </div>
    );
  }

  const formatPrice = (p: number) => {
    return `₹${p.toLocaleString('en-IN')}`;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <Link href="/" className="hover:text-navy-900">Home</Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <Link href="/vehicles" className="hover:text-navy-900">Vehicles</Link>
        <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
        <span className="text-navy-950 font-semibold">{vehicle.brand.name} {vehicle.name}</span>
      </div>

      {/* Vehicle Hero Grid: Gallery & Main Specs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Gallery / Main Photo */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-slate-100 rounded-3xl overflow-hidden border border-slate-200/80 h-80 sm:h-96 relative">
            <img
              src={vehicle.image_url || 'https://images.unsplash.com/photo-1549399542-7e3f8b79c341?w=800'}
              alt={vehicle.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4 bg-white/95 backdrop-blur-md px-3 py-1 rounded-full text-xs font-bold text-navy-900 shadow-sm">
              {vehicle.brand.name}
            </div>
            <div className="absolute bottom-4 right-4 bg-navy-950/80 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-medium">
              Pilot City: Indore, MP
            </div>
          </div>
        </div>

        {/* Specifications & Variant Picker */}
        <div className="lg:col-span-5 flex flex-col justify-between space-y-6 bg-white p-6 rounded-3xl border border-slate-200 shadow-sm">
          <div className="space-y-4">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-brand-600">
                {vehicle.brand.category_name} • {vehicle.body_type}
              </span>
              <h1 className="text-2xl sm:text-3xl font-black text-navy-950 mt-1">
                {vehicle.brand.name} {vehicle.name}
              </h1>
            </div>

            {/* Select Variant */}
            <div className="space-y-2 pt-2">
              <label className="text-xs font-bold text-slate-700">Select Variant:</label>
              <div className="grid grid-cols-1 gap-2 max-h-48 overflow-y-auto pr-1">
                {vehicle.variants.map((v: VehicleVariant) => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedVariant(v)}
                    className={`p-3 rounded-xl text-left border transition-all text-xs flex items-center justify-between ${
                      selectedVariant?.id === v.id
                        ? 'border-brand-500 bg-orange-50/70 text-navy-950 font-semibold ring-1 ring-brand-500/20'
                        : 'border-slate-200 hover:border-slate-300 text-slate-700 bg-slate-50'
                    }`}
                  >
                    <div>
                      <div className="font-bold">{v.name}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {v.fuel_type} • {v.transmission} • {v.engine_cc_or_battery_kwh || 'Standard'}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-navy-900">{formatPrice(v.reference_ex_showroom)}</div>
                      <div className="text-[10px] text-slate-400">Ex-showroom ref</div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Active Variant Specs Details */}
            {selectedVariant && (
              <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/80 space-y-2 text-xs">
                <div className="font-bold text-navy-900 border-b border-slate-200/60 pb-1.5 flex items-center justify-between">
                  <span>Selected Variant Specifications</span>
                  <span className="text-brand-600 font-semibold">{selectedVariant.fuel_type}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-slate-600 pt-1">
                  <div>Transmission: <strong className="text-navy-900">{selectedVariant.transmission}</strong></div>
                  <div>Capacity: <strong className="text-navy-900">{selectedVariant.seating_capacity || 5} Seats</strong></div>
                  <div>Displacement / Battery: <strong className="text-navy-900">{selectedVariant.engine_cc_or_battery_kwh || 'N/A'}</strong></div>
                  <div>City Benchmark: <strong className="text-navy-900">Indore, MP</strong></div>
                </div>
              </div>
            )}
          </div>

          {/* Action CTAs */}
          <div className="space-y-2 pt-2">
            <Link
              href={`/groups/create?variant_id=${selectedVariant?.id || ''}`}
              className="w-full py-3 bg-brand-500 hover:bg-brand-600 text-white font-bold text-xs rounded-xl shadow-md shadow-brand-500/20 transition-all flex items-center justify-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Start a Buying Group for this Variant
            </Link>
            <p className="text-[11px] text-center text-slate-400">
              Pooling 5+ buyers unlocks verified bulk OEM discounts in Indore.
            </p>
          </div>
        </div>

      </div>

      {/* Available Buying Groups for this Vehicle */}
      <div className="space-y-4 pt-6 border-t border-slate-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-navy-950">Active Buying Cohorts for this Vehicle</h2>
            <p className="text-xs text-slate-500 mt-0.5">Join an ongoing local group to fast-track bidding and delivery</p>
          </div>
          <Link
            href={`/groups/create?model_id=${vehicle.id}`}
            className="text-xs font-semibold text-brand-600 hover:underline flex items-center gap-1"
          >
            + Create New Cohort
          </Link>
        </div>

        {vehicle.active_groups?.length === 0 ? (
          <div className="p-8 bg-white rounded-2xl border border-slate-200 text-center space-y-3">
            <Users className="w-8 h-8 text-slate-300 mx-auto" />
            <p className="text-sm font-semibold text-navy-900">No active groups for this vehicle yet.</p>
            <p className="text-xs text-slate-400 max-w-sm mx-auto">
              Be the cohort initiator! Start a group in Indore and invite friends or let fellow buyers join.
            </p>
            <Link
              href={`/groups/create?variant_id=${selectedVariant?.id || ''}`}
              className="inline-block px-4 py-2 bg-navy-900 hover:bg-navy-800 text-white text-xs font-semibold rounded-xl"
            >
              Create Group Now
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {vehicle.active_groups.map((g: any) => (
              <div
                key={g.id}
                className="p-5 bg-white rounded-2xl border border-slate-200 shadow-sm flex flex-col justify-between space-y-3 hover:border-brand-300 transition-colors"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="text-[10px] font-mono text-slate-400">{g.group_code}</span>
                    <h4 className="font-bold text-sm text-navy-950 mt-0.5">{g.variant_name}</h4>
                    <span className="text-xs text-slate-500">{g.city_name}</span>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-brand-100 text-brand-700">
                    {g.status}
                  </span>
                </div>

                <div className="space-y-1.5 pt-2 border-t border-slate-100 text-xs">
                  <div className="flex justify-between text-slate-600">
                    <span>Members Pooled:</span>
                    <strong className="text-navy-900">{g.current_members_count} / {g.target_members}</strong>
                  </div>
                  <div className="flex justify-between text-slate-600">
                    <span>Timeline:</span>
                    <span>{g.target_purchase_timeline.replace(/_/g, ' ')}</span>
                  </div>
                </div>

                <Link
                  href={`/groups/${g.id}`}
                  className="w-full py-2 bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs rounded-xl text-center transition-colors block"
                >
                  Join or View Group
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
