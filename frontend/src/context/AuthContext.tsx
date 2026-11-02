'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole } from '@/types';
import { apiFetch } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (payload: any) => Promise<void>;
  logout: () => void;
  quickLoginDemo: (role: UserRole) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check saved session on mount
    const savedToken = localStorage.getItem('gaadilelo_token');
    const savedUser = localStorage.getItem('gaadilelo_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('gaadilelo_token');
        localStorage.removeItem('gaadilelo_user');
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      setToken(res.access_token);
      setUser(res.user);
      localStorage.setItem('gaadilelo_token', res.access_token);
      localStorage.setItem('gaadilelo_user', JSON.stringify(res.user));
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (payload: any) => {
    setIsLoading(true);
    try {
      const res = await apiFetch('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      });

      setToken(res.access_token);
      setUser(res.user);
      localStorage.setItem('gaadilelo_token', res.access_token);
      localStorage.setItem('gaadilelo_user', JSON.stringify(res.user));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('gaadilelo_token');
    localStorage.removeItem('gaadilelo_user');
  };

  const quickLoginDemo = async (role: UserRole) => {
    let email = 'rahul.sharma@gmail.com';
    let password = 'Buyer@123';

    if (role === 'DEALER') {
      email = 'sales@sanghimotors.com';
      password = 'Dealer@123';
    } else if (role === 'ADMIN') {
      email = 'admin@gaadilelo.com';
      password = 'Admin@123';
    }

    await login(email, password);
  };

  const refreshUser = async () => {
    if (!token) return;
    try {
      const me = await apiFetch('/auth/me');
      const updatedUser: User = {
        id: me.id,
        email: me.email,
        phone: me.phone,
        role: me.role,
        full_name: me.profile?.full_name || me.email,
        is_verified: me.is_verified,
        city_id: me.profile?.city_id,
        dealer: me.dealer,
      };
      setUser(updatedUser);
      localStorage.setItem('gaadilelo_user', JSON.stringify(updatedUser));
    } catch (e) {
      console.error('Failed to refresh user:', e);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        quickLoginDemo,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
