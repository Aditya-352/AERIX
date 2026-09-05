'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Plane, BarChart3, ShieldCheck, Activity } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="border-b border-slate-200 bg-white/95 backdrop-blur-md sticky top-0 z-50 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                <Plane className="w-5 h-5 -rotate-45" />
              </div>
              <div>
                <span className="text-xl font-black tracking-tight text-slate-900">
                  AEROVA
                </span>
                <span className="block text-[10px] text-blue-600 font-bold tracking-wider uppercase">
                  India Airfare Price Intelligence
                </span>
              </div>
            </Link>
          </div>

          <div className="flex items-center gap-1 sm:gap-3">
            <Link
              href="/"
              className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                pathname === '/'
                  ? 'bg-blue-50 text-blue-600 border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              Home
            </Link>

            <Link
              href="/search"
              className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                pathname === '/search'
                  ? 'bg-blue-50 text-blue-600 border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Plane className="w-4 h-4 text-blue-600" />
              Consumer Search
            </Link>

            <Link
              href="/dashboard"
              className={`px-3.5 py-2 rounded-xl text-sm font-semibold transition-colors flex items-center gap-1.5 ${
                pathname === '/dashboard'
                  ? 'bg-blue-50 text-blue-600 border border-blue-200'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <BarChart3 className="w-4 h-4 text-blue-600" />
              Gov Analytics
            </Link>

            <div className="hidden lg:flex items-center gap-2 pl-4 border-l border-slate-200">
              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                APIx 114.7 (+0.8%)
              </span>
              <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                <ShieldCheck className="w-3.5 h-3.5" />
                Data Quality 94%
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
