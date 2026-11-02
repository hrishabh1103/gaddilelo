'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { 
  Car, Users, PlusCircle, Bell, User as UserIcon, 
  Menu, X, MapPin, ChevronDown, Shield, Building2, Search,
  Phone, HelpCircle, ArrowRight, Zap, CheckCircle2, LogOut
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { NotificationItem } from '@/types';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [cityModalOpen, setCityModalOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [navSearch, setNavSearch] = useState('');
  const [currentCity, setCurrentCity] = useState('Indore');

  const brandName = process.env.NEXT_PUBLIC_BRAND_NAME || 'GaadiLelo';

  useEffect(() => {
    if (user) {
      loadNotifications();
    } else {
      setNotifications([]);
      setUnreadCount(0);
    }
  }, [user]);

  const loadNotifications = async () => {
    try {
      const data = await apiFetch<NotificationItem[]>('/notifications');
      setNotifications(data || []);
      setUnreadCount(data?.filter(n => !n.is_read).length || 0);
    } catch (e) {
      // ignore
    }
  };

  const markAllRead = async () => {
    try {
      await apiFetch('/notifications/read-all', { method: 'PUT' });
      setUnreadCount(0);
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (e) {
      // ignore
    }
  };

  const handleNavSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (navSearch.trim()) {
      router.push(`/vehicles?search=${encodeURIComponent(navSearch.trim())}`);
    }
  };

  const isActive = (path: string) => pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-white border-b border-slate-200/90 shadow-[0_1px_4px_rgba(0,0,0,0.06)] font-sans">
      
      {/* 1. TOP UTILITY STRIP (CarDekho MNC Style) */}
      <div className="bg-slate-900 text-slate-300 text-[11px] py-1 px-4 sm:px-6 lg:px-8 border-b border-slate-800 hidden md:block">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 font-medium text-slate-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Pilot Live: <strong className="text-white">Indore, MP</strong> — 100% Free & Non-Binding Group Buying
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">Authorized OEM Dealerships Only</span>
          </div>

          <div className="flex items-center gap-5">
            <Link href="/how-it-works" className="hover:text-white transition-colors flex items-center gap-1">
              <HelpCircle className="w-3 h-3 text-slate-400" />
              <span>How Group Buying Works</span>
            </Link>
            <span className="text-slate-700">•</span>
            {user?.role !== 'DEALER' ? (
              <Link href="/register?role=DEALER" className="hover:text-brand-400 transition-colors flex items-center gap-1 text-slate-300 font-medium">
                <Building2 className="w-3 h-3 text-brand-400" />
                <span>For Dealerships (Partner Onboarding)</span>
              </Link>
            ) : (
              <Link href="/dealer/dashboard" className="text-orange-400 font-semibold flex items-center gap-1">
                <Building2 className="w-3 h-3" />
                <span>Dealer Console</span>
              </Link>
            )}
            <span className="text-slate-700">•</span>
            <span className="flex items-center gap-1 text-slate-400">
              <Phone className="w-3 h-3" />
              <span>Indore Desk: 1800-GAADI-LELO</span>
            </span>
          </div>

        </div>
      </div>

      {/* 2. MAIN NAVIGATION BAR */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 sm:h-[72px] gap-4 lg:gap-8">
          
          {/* Logo */}
          <div className="flex items-center gap-3 flex-shrink-0">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-orange-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
                <Car className="w-6 h-6 stroke-[2.2]" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-baseline">
                  <span className="text-2xl font-black tracking-tight text-navy-950 font-sans">
                    GAADI<span className="text-brand-600">LELO</span>
                  </span>
                  <span className="text-xs font-bold text-slate-400 ml-0.5">.COM</span>
                </div>
                <span className="text-[10px] font-semibold text-slate-500 tracking-wider uppercase -mt-1">
                  Buy Together • Save Together
                </span>
              </div>
            </Link>
          </div>

          {/* MNC Search Bar in Header (Desktop) */}
          <div className="hidden lg:flex flex-1 max-w-lg">
            <form onSubmit={handleNavSearch} className="w-full relative">
              <div className="flex items-center bg-slate-50 border border-slate-300 rounded-xl overflow-hidden focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-500/10 focus-within:bg-white transition-all">
                <div className="pl-3.5 text-slate-400">
                  <Search className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={navSearch}
                  onChange={(e) => setNavSearch(e.target.value)}
                  placeholder="Search by vehicle, model, or brand (e.g. Nexon, Creta, Ather)..."
                  className="w-full py-2.5 px-3 text-xs text-slate-800 placeholder-slate-400 bg-transparent focus:outline-none"
                />
                <button
                  type="submit"
                  className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold border-l border-slate-200 transition-colors flex items-center gap-1"
                >
                  <span>Search</span>
                </button>
              </div>
            </form>
          </div>

          {/* City Selector Pill */}
          <div className="relative hidden sm:block flex-shrink-0">
            <button
              onClick={() => setCityModalOpen(!cityModalOpen)}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl text-xs font-semibold text-slate-700 transition-colors"
            >
              <MapPin className="w-3.5 h-3.5 text-brand-500" />
              <span>{currentCity}, MP</span>
              <ChevronDown className="w-3 h-3 text-slate-400" />
            </button>

            {cityModalOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-xl shadow-xl border border-slate-200 p-2 z-50 text-xs">
                <div className="px-3 py-1.5 font-bold text-slate-500 text-[10px] uppercase border-b border-slate-100">
                  Select Buying Location
                </div>
                <button
                  onClick={() => { setCurrentCity('Indore'); setCityModalOpen(false); }}
                  className="w-full text-left px-3 py-2 rounded-lg hover:bg-orange-50 font-medium text-slate-800 flex items-center justify-between mt-1"
                >
                  <span>Indore, Madhya Pradesh</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-1.5 py-0.5 rounded font-bold">Active Pilot</span>
                </button>
                <div className="px-3 py-2 rounded-lg text-slate-400 flex items-center justify-between cursor-not-allowed">
                  <span>Bhopal, Madhya Pradesh</span>
                  <span className="text-[10px] text-slate-400">Coming Soon</span>
                </div>
              </div>
            )}
          </div>

          {/* Right Action Menu: Groups, Notifications, Profile */}
          <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
            
            {/* Start a Group CTA Button */}
            {user?.role !== 'DEALER' && (
              <Link
                href="/groups/create"
                className="hidden sm:inline-flex items-center gap-1.5 px-3.5 py-2 text-xs font-bold rounded-xl bg-brand-500 text-white hover:bg-brand-600 transition-all shadow-sm shadow-brand-500/20"
              >
                <PlusCircle className="w-3.5 h-3.5" />
                <span>Start Buying Group</span>
              </Link>
            )}

            {/* Notification Bell */}
            {user && (
              <div className="relative">
                <button
                  onClick={() => {
                    setNotificationsOpen(!notificationsOpen);
                    if (!notificationsOpen && unreadCount > 0) markAllRead();
                  }}
                  className="p-2 rounded-xl text-slate-600 hover:bg-slate-100 relative transition-colors border border-transparent hover:border-slate-200"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full ring-2 ring-white" />
                  )}
                </button>

                {/* Notifications Dropdown */}
                {notificationsOpen && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-2xl border border-slate-200 py-2 z-50">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100">
                      <span className="font-bold text-xs text-navy-900">Notifications</span>
                      <button onClick={markAllRead} className="text-[11px] text-brand-600 hover:underline">
                        Mark all read
                      </button>
                    </div>
                    <div className="max-h-72 overflow-y-auto divide-y divide-slate-50">
                      {notifications.length === 0 ? (
                        <div className="p-4 text-center text-xs text-slate-400">
                          No notifications yet
                        </div>
                      ) : (
                        notifications.slice(0, 6).map((n) => (
                          <div key={n.id} className={`p-3 text-xs ${!n.is_read ? 'bg-orange-50/50' : ''}`}>
                            <p className="font-bold text-navy-900">{n.title}</p>
                            <p className="text-slate-600 mt-0.5 line-clamp-2">{n.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* User Account / Login State */}
            {user ? (
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 sm:px-3 sm:py-1.5 rounded-xl border border-slate-200 hover:bg-slate-50 transition-all text-xs font-semibold text-slate-800"
                >
                  <div className="w-7 h-7 rounded-lg bg-slate-900 text-white font-bold flex items-center justify-center text-xs">
                    {user.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="hidden md:inline max-w-[100px] truncate">{user.full_name}</span>
                  <ChevronDown className="w-3 h-3 text-slate-400" />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-56 bg-white rounded-2xl shadow-2xl border border-slate-200 py-2 z-50 text-xs">
                    <div className="px-4 py-2 border-b border-slate-100">
                      <p className="font-bold text-navy-900 truncate">{user.full_name}</p>
                      <p className="text-[11px] text-slate-400 truncate">{user.email}</p>
                      <span className="inline-block mt-1 text-[10px] font-bold uppercase bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                        {user.role}
                      </span>
                    </div>

                    <div className="py-1">
                      {user.role === 'BUYER' && (
                        <Link
                          href="/dashboard"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 font-medium text-slate-700"
                        >
                          <Car className="w-4 h-4 text-slate-400" />
                          <span>My Buying Groups</span>
                        </Link>
                      )}

                      {user.role === 'DEALER' && (
                        <Link
                          href="/dealer/dashboard"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 font-medium text-slate-700"
                        >
                          <Building2 className="w-4 h-4 text-slate-400" />
                          <span>Dealer Console</span>
                        </Link>
                      )}

                      {user.role === 'ADMIN' && (
                        <Link
                          href="/admin"
                          onClick={() => setUserMenuOpen(false)}
                          className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 font-medium text-slate-700"
                        >
                          <Shield className="w-4 h-4 text-slate-400" />
                          <span>Admin Console</span>
                        </Link>
                      )}

                      <Link
                        href="/profile"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 font-medium text-slate-700"
                      >
                        <UserIcon className="w-4 h-4 text-slate-400" />
                        <span>Profile & Settings</span>
                      </Link>
                    </div>

                    <div className="border-t border-slate-100 pt-1">
                      <button
                        onClick={() => { setUserMenuOpen(false); logout(); }}
                        className="w-full text-left flex items-center gap-2 px-4 py-2 hover:bg-red-50 text-red-600 font-medium"
                      >
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-3.5 py-2 text-xs font-bold text-slate-700 hover:text-navy-950 hover:bg-slate-100 rounded-xl transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-xs font-bold text-white bg-slate-900 hover:bg-slate-800 rounded-xl transition-all shadow-sm"
                >
                  Register
                </Link>
              </div>
            )}

            {/* Mobile Menu Toggle Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-xl"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>

          </div>

        </div>
      </div>

      {/* 3. SECONDARY CATEGORY NAV STRIP (CarDekho Signature Secondary Menu) */}
      <div className="bg-slate-50 border-t border-slate-200 hidden lg:block text-xs font-semibold text-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center gap-8 h-10">
          <Link
            href="/vehicles"
            className={`hover:text-brand-600 transition-colors py-2 flex items-center gap-1.5 ${
              isActive('/vehicles') ? 'text-brand-600 border-b-2 border-brand-500 font-bold' : ''
            }`}
          >
            <Car className="w-3.5 h-3.5 text-slate-400" />
            <span>ALL VEHICLES</span>
          </Link>

          <Link
            href="/groups"
            className={`hover:text-brand-600 transition-colors py-2 flex items-center gap-1.5 ${
              isActive('/groups') ? 'text-brand-600 border-b-2 border-brand-500 font-bold' : ''
            }`}
          >
            <Users className="w-3.5 h-3.5 text-brand-500" />
            <span>BUYING GROUPS</span>
            <span className="text-[10px] bg-brand-100 text-brand-700 px-1.5 py-0.2 rounded font-bold">LIVE</span>
          </Link>

          <Link
            href="/vehicles?category=electric-vehicle"
            className="hover:text-amber-600 transition-colors py-2 flex items-center gap-1.5 text-slate-700"
          >
            <Zap className="w-3.5 h-3.5 text-amber-500" />
            <span>ELECTRIC VEHICLES</span>
          </Link>

          <Link
            href="/vehicles?category=car"
            className="hover:text-brand-600 transition-colors py-2"
          >
            <span>CARS & SUVS</span>
          </Link>

          <Link
            href="/vehicles?category=two-wheeler"
            className="hover:text-brand-600 transition-colors py-2"
          >
            <span>TWO-WHEELERS</span>
          </Link>

          <Link
            href="/vehicles?category=commercial-vehicle"
            className="hover:text-brand-600 transition-colors py-2"
          >
            <span>COMMERCIAL & FLEETS</span>
          </Link>

          <Link
            href="/how-it-works"
            className="hover:text-brand-600 transition-colors py-2 ml-auto text-slate-500 hover:text-slate-800 font-normal"
          >
            <span>Why Group Buying Saves Money?</span>
          </Link>
        </div>
      </div>

      {/* 4. MOBILE SLIDEOUT MENU */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-slate-200 px-4 pt-3 pb-6 space-y-4 animate-in slide-in-from-top-2">
          
          {/* Mobile Search */}
          <form onSubmit={handleNavSearch} className="w-full">
            <div className="flex items-center bg-slate-50 border border-slate-300 rounded-xl overflow-hidden px-3 py-2 text-xs">
              <Search className="w-4 h-4 text-slate-400 mr-2" />
              <input
                type="text"
                value={navSearch}
                onChange={(e) => setNavSearch(e.target.value)}
                placeholder="Search Nexon, Creta, Brezza..."
                className="w-full bg-transparent focus:outline-none text-slate-800"
              />
            </div>
          </form>

          {/* Links */}
          <div className="space-y-1 text-sm font-semibold text-slate-800">
            <Link
              href="/vehicles"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl hover:bg-slate-50"
            >
              Explore Vehicles & Models
            </Link>
            <Link
              href="/groups"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl hover:bg-slate-50 text-brand-600 font-bold"
            >
              Active Indore Buying Groups
            </Link>
            <Link
              href="/groups/create"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl bg-orange-50 text-brand-700 font-bold"
            >
              + Start a New Buying Group
            </Link>
            <Link
              href="/how-it-works"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl hover:bg-slate-50"
            >
              How It Works
            </Link>
            <Link
              href="/register?role=DEALER"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-xl hover:bg-slate-50 text-blue-700"
            >
              Dealership Partner Portal
            </Link>
          </div>

          {!user && (
            <div className="pt-2 border-t border-slate-100 flex gap-2">
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 py-2 text-center text-xs font-bold rounded-xl border border-slate-200"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                onClick={() => setMobileMenuOpen(false)}
                className="flex-1 py-2 text-center text-xs font-bold rounded-xl bg-slate-900 text-white"
              >
                Register Free
              </Link>
            </div>
          )}

        </div>
      )}

    </header>
  );
}
