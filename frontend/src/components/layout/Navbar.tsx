'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { 
  Car, Users, PlusCircle, Bell, User as UserIcon, 
  Menu, X, MapPin, ChevronDown, Shield, LayoutDashboard, Building2
} from 'lucide-react';
import { apiFetch } from '@/lib/api';
import { NotificationItem } from '@/types';

export default function Navbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

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

  const isActive = (path: string) => pathname === path;

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Brand Logo & City Pill */}
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-brand-500 flex items-center justify-center text-white shadow-md shadow-brand-500/20 group-hover:scale-105 transition-transform">
                <Car className="w-6 h-6" />
              </div>
              <div>
                <span className="text-xl font-black tracking-tight text-navy-900">
                  {brandName}<span className="text-brand-500">.com</span>
                </span>
                <span className="block text-[10px] font-semibold text-slate-400 tracking-wider uppercase -mt-1">
                  Buy Together
                </span>
              </div>
            </Link>

            {/* Pilot Market City Badge */}
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 bg-slate-100 hover:bg-slate-200/80 rounded-full text-xs font-medium text-slate-700 transition-colors cursor-pointer border border-slate-200/60">
              <MapPin className="w-3.5 h-3.5 text-brand-500" />
              <span>Indore, MP</span>
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse ml-0.5" />
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center gap-6">
            <Link
              href="/vehicles"
              className={`text-sm font-medium transition-colors ${
                isActive('/vehicles') ? 'text-brand-600 font-semibold' : 'text-slate-600 hover:text-navy-900'
              }`}
            >
              Explore Vehicles
            </Link>

            <Link
              href="/groups"
              className={`text-sm font-medium transition-colors flex items-center gap-1.5 ${
                isActive('/groups') ? 'text-brand-600 font-semibold' : 'text-slate-600 hover:text-navy-900'
              }`}
            >
              <Users className="w-4 h-4 text-brand-500" />
              Buying Groups
            </Link>

            <Link
              href="/how-it-works"
              className={`text-sm font-medium transition-colors ${
                isActive('/how-it-works') ? 'text-brand-600 font-semibold' : 'text-slate-600 hover:text-navy-900'
              }`}
            >
              How It Works
            </Link>

            {/* Role specific portals */}
            {user?.role === 'DEALER' && (
              <Link
                href="/dealer/dashboard"
                className={`text-sm font-semibold flex items-center gap-1.5 px-3 py-1 rounded-lg ${
                  pathname.startsWith('/dealer') ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'text-blue-600 hover:bg-blue-50/50'
                }`}
              >
                <Building2 className="w-4 h-4" />
                Dealer Portal
              </Link>
            )}

            {user?.role === 'ADMIN' && (
              <Link
                href="/admin"
                className={`text-sm font-semibold flex items-center gap-1.5 px-3 py-1 rounded-lg ${
                  pathname.startsWith('/admin') ? 'bg-purple-50 text-purple-700 border border-purple-200' : 'text-purple-600 hover:bg-purple-50/50'
                }`}
              >
                <Shield className="w-4 h-4" />
                Admin Panel
              </Link>
            )}
          </nav>

          {/* Actions & User Section */}
          <div className="flex items-center gap-3">
            {/* Create Group Quick CTA for Buyers */}
            {user?.role !== 'DEALER' && (
              <Link
                href="/groups/create"
                className="hidden lg:inline-flex items-center gap-1.5 px-3.5 py-1.5 text-xs font-semibold rounded-lg bg-navy-900 text-white hover:bg-navy-800 transition-colors shadow-sm"
              >
                <PlusCircle className="w-3.5 h-3.5 text-brand-400" />
                Start Group
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
                  className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 relative transition-colors"
                  aria-label="Notifications"
                >
                  <Bell className="w-5 h-5" />
                  {unreadCount > 0 && (
                    <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-brand-500 rounded-full ring-2 ring-white" />
                  )}
                </button>

                {/* Notifications Dropdown */}
                {notificationsOpen && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                    <div className="flex items-center justify-between px-4 py-2 border-b border-slate-100">
                      <span className="font-semibold text-xs text-navy-900">Notifications</span>
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
                          <div key={n.id} className={`p-3 text-xs ${!n.is_read ? 'bg-orange-50/40' : ''}`}>
                            <p className="font-semibold text-navy-900">{n.title}</p>
                            <p className="text-slate-600 mt-0.5 line-clamp-2">{n.message}</p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* User Profile / Auth State */}
            {user ? (
              <div className="flex items-center gap-2">
                <Link
                  href={user.role === 'DEALER' ? '/dealer/dashboard' : user.role === 'ADMIN' ? '/admin' : '/dashboard'}
                  className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-50 text-xs font-semibold text-navy-900 transition-colors"
                >
                  <div className="w-6 h-6 rounded-full bg-brand-100 text-brand-600 flex items-center justify-center font-bold">
                    {user.full_name?.charAt(0) || 'U'}
                  </div>
                  <span className="hidden sm:inline max-w-[120px] truncate">{user.full_name}</span>
                </Link>

                <button
                  onClick={logout}
                  className="text-xs text-slate-500 hover:text-red-600 font-medium px-2 py-1"
                >
                  Logout
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  href="/login"
                  className="px-3.5 py-1.5 text-xs font-semibold rounded-lg text-navy-900 hover:bg-slate-100 transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-1.5 text-xs font-semibold rounded-lg bg-brand-500 text-white hover:bg-brand-600 transition-colors shadow-sm shadow-brand-500/20"
                >
                  Join Free
                </Link>
              </div>
            )}

            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 bg-white px-4 pt-3 pb-6 space-y-3">
          <Link
            href="/vehicles"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-800 hover:bg-slate-50"
          >
            Explore Vehicles
          </Link>
          <Link
            href="/groups"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-800 hover:bg-slate-50"
          >
            Buying Groups
          </Link>
          <Link
            href="/how-it-works"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-medium text-slate-800 hover:bg-slate-50"
          >
            How It Works
          </Link>
          <Link
            href="/groups/create"
            onClick={() => setMobileMenuOpen(false)}
            className="block px-3 py-2 rounded-lg text-sm font-semibold text-brand-600 hover:bg-orange-50"
          >
            + Start a Buying Group
          </Link>
          {user?.role === 'DEALER' && (
            <Link
              href="/dealer/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-blue-700 bg-blue-50"
            >
              Dealer Portal
            </Link>
          )}
          {user?.role === 'ADMIN' && (
            <Link
              href="/admin"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-sm font-semibold text-purple-700 bg-purple-50"
            >
              Admin Dashboard
            </Link>
          )}
        </div>
      )}
    </header>
  );
}
