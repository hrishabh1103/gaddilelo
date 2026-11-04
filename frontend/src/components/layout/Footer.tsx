import React from 'react';
import Link from 'next/link';
import { Car, ShieldCheck, MapPin, Phone, Mail, Award, CheckCircle2, ChevronRight } from 'lucide-react';

export default function Footer() {
  const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || 'GaadiLelo';

  return (
    <footer className="bg-navy-950 text-slate-400 text-xs border-t border-navy-800 font-sans w-full max-w-full overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16 space-y-12">
        
        {/* Main Footer Links Columns */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-12">
          
          {/* Brand Column */}
          <div className="lg:col-span-2 space-y-4">
            <Link href="/" className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 to-orange-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20">
                <Car className="w-5 h-5 stroke-[2.2]" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-baseline">
                  <span className="text-xl font-black tracking-tight text-white">
                    GAADI<span className="text-brand-500">LELO</span>
                  </span>
                  <span className="text-xs font-bold text-slate-500 ml-0.5">.COM</span>
                </div>
                <span className="text-[10px] font-semibold text-slate-400 tracking-wider uppercase -mt-0.5">
                  Buy Together • Save Together
                </span>
              </div>
            </Link>

            <p className="text-xs leading-relaxed text-slate-400 max-w-sm">
              India&apos;s pioneering group-buying platform for passenger and commercial vehicles. 
              By aggregating authentic buyer demand into local cohorts, authorized OEM dealerships compete 
              to provide their sharpest on-road pricing with 100% price transparency.
            </p>

            <div className="pt-1 space-y-2">
              <div className="flex items-center gap-2 text-xs text-brand-400">
                <MapPin className="w-4 h-4 flex-shrink-0" />
                <span>Pilot Market: Indore, Madhya Pradesh (Expansion Ready)</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Phone className="w-4 h-4 flex-shrink-0" />
                <span>Toll-Free Helpline: 1800-GAADI-LELO (Mon-Sat, 9AM-8PM)</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-slate-400">
                <Mail className="w-4 h-4 flex-shrink-0" />
                <span>Partner Inquiries: dealerships@gaadilelo.com</span>
              </div>
            </div>
          </div>

          {/* Vehicle Categories */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Vehicle Segments</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/vehicles?category=car" className="hover:text-white transition-colors">Passenger Cars & SUVs</Link></li>
              <li><Link href="/vehicles?category=electric-vehicle" className="hover:text-white transition-colors">Electric Vehicles (EVs)</Link></li>
              <li><Link href="/vehicles?category=two-wheeler" className="hover:text-white transition-colors">Two-Wheelers & Scooters</Link></li>
              <li><Link href="/vehicles?category=commercial-vehicle" className="hover:text-white transition-colors">Commercial Pickups & LCVs</Link></li>
              <li><Link href="/vehicles?category=three-wheeler" className="hover:text-white transition-colors">Three-Wheelers</Link></li>
            </ul>
          </div>

          {/* Platform Links */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Group Buying</h4>
            <ul className="space-y-2 text-xs">
              <li><Link href="/groups" className="hover:text-white transition-colors">Active Indore Cohorts</Link></li>
              <li><Link href="/groups/create" className="hover:text-white transition-colors">Start a Buying Group</Link></li>
              <li><Link href="/how-it-works" className="hover:text-white transition-colors">How Bidding Works</Link></li>
              <li><Link href="/register?role=DEALER" className="hover:text-brand-400 transition-colors">Dealership Partner Portal</Link></li>
              <li><Link href="/login" className="hover:text-white transition-colors">Customer Login</Link></li>
            </ul>
          </div>

          {/* Trustmarks & Commitments */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">Buyer Guarantees</h4>
            <ul className="space-y-2 text-xs">
              <li className="flex items-start gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Verified OEM Dealerships</span>
              </li>
              <li className="flex items-start gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Strict PII Contact Privacy</span>
              </li>
              <li className="flex items-start gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Zero Mandatory Handling Fees</span>
              </li>
              <li className="flex items-start gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>100% Non-Binding ₹0 Intent</span>
              </li>
              <li className="flex items-start gap-1.5 text-slate-300">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0 mt-0.5" />
                <span>Direct Showroom Handover</span>
              </li>
            </ul>
          </div>

        </div>

        {/* CarDekho Enterprise Directory Strip */}
        <div className="pt-8 border-t border-navy-800 grid grid-cols-1 md:grid-cols-2 gap-6 text-[11px] text-slate-400">
          <div>
            <span className="font-bold text-slate-300 uppercase block mb-1">Popular Brands in Indore:</span>
            <p className="leading-relaxed">
              Tata Motors Showrooms Indore • Hyundai Dealerships Indore • Maruti Suzuki Arena/Nexa • Mahindra & Mahindra Indore • Ather Energy Experience Center • Ola Electric Hub • TVS Motor Dealerships • Ashok Leyland Light Commercial
            </p>
          </div>
          <div>
            <span className="font-bold text-slate-300 uppercase block mb-1">Top Active Buying Cohorts:</span>
            <p className="leading-relaxed">
              Tata Nexon Creative Plus Petrol • Hyundai Creta EX • Maruti Brezza Smart Hybrid • Ather 450X Long Range EV • Mahindra Scorpio-N Z8 • Ashok Leyland Bada Dost SCV
            </p>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-6 border-t border-navy-800 flex flex-col sm:flex-row items-center justify-between text-slate-500 gap-4 text-[11px]">
          <p>© {new Date().getFullYear()} {brandName}.com. All rights reserved. Indian Automotive Technology & Group Demand Engine.</p>
          <div className="flex items-center gap-4">
            <span className="bg-navy-900 px-2.5 py-1 rounded border border-navy-800 text-slate-400">
              Indore Pilot Release (v1.2)
            </span>
          </div>
        </div>

      </div>
    </footer>
  );
}
