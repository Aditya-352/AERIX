'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Plane, Search, BarChart3, ShieldCheck, ArrowRight, TrendingUp, Calendar, Users, Briefcase, Activity, Layers, CheckCircle2 } from 'lucide-react';

const CITIES = [
  { code: 'DEL', name: 'New Delhi', city: 'Delhi' },
  { code: 'BOM', name: 'Chhatrapati Shivaji Maharaj Int', city: 'Mumbai' },
  { code: 'BLR', name: 'Kempegowda International', city: 'Bengaluru' },
  { code: 'MAA', name: 'Chennai International', city: 'Chennai' },
  { code: 'HYD', name: 'Rajiv Gandhi International', city: 'Hyderabad' },
  { code: 'CCU', name: 'Netaji Subhash Chandra Bose', city: 'Kolkata' }
];

export default function LandingPage() {
  const router = useRouter();
  const [fromCity, setFromCity] = useState('DEL');
  const [toCity, setToCity] = useState('BOM');
  const [depDate, setDepDate] = useState('2026-09-15');
  const [adults, setAdults] = useState(1);
  const [cabin, setCabin] = useState('Economy');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    router.push(`/search?from=${fromCity}&to=${toCity}&departure=${depDate}&adults=${adults}&cabin=${cabin.toLowerCase()}`);
  };

  return (
    <div className="space-y-12 py-2">
      {/* HERO SECTION */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-blue-50/80 via-slate-50 to-white border border-slate-200 p-8 lg:p-12 shadow-sm">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200">
            <Activity className="w-3.5 h-3.5 text-blue-600" />
            Government-Grade High-Frequency Airfare Intelligence Platform
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-slate-900 tracking-tight leading-tight">
            India's Airfare. <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-600">
              Measured in Real Time.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed font-medium">
            Track, compare and analyze airfare movements across India's major airlines, representative routes and booking platforms using our Real-Time Airfare Price Index (APIx).
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link
              href="/dashboard"
              className="px-6 py-3.5 rounded-xl font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-600/25 transition-all flex items-center gap-2"
            >
              <BarChart3 className="w-5 h-5" />
              Explore Airfare Data (APIx)
            </Link>
            <Link
              href="/search"
              className="px-6 py-3.5 rounded-xl font-bold bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 shadow-sm transition-all flex items-center gap-2"
            >
              <Plane className="w-5 h-5 text-blue-600" />
              Compare Flights
            </Link>
          </div>
        </div>

        {/* HERO FLIGHT SEARCH BOX */}
        <div className="mt-10 max-w-5xl mx-auto bg-white border border-slate-200 rounded-2xl p-6 shadow-xl">
          <form onSubmit={handleSearchSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {/* FROM */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                  <Plane className="w-3.5 h-3.5 -rotate-45 text-blue-600" /> From
                </label>
                <select
                  value={fromCity}
                  onChange={(e) => setFromCity(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white focus:outline-none"
                >
                  {CITIES.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.city} ({c.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* TO */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                  <Plane className="w-3.5 h-3.5 rotate-45 text-blue-600" /> To
                </label>
                <select
                  value={toCity}
                  onChange={(e) => setToCity(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white focus:outline-none"
                >
                  {CITIES.map((c) => (
                    <option key={c.code} value={c.code}>
                      {c.city} ({c.code})
                    </option>
                  ))}
                </select>
              </div>

              {/* DATE */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-blue-600" /> Departure
                </label>
                <input
                  type="date"
                  value={depDate}
                  onChange={(e) => setDepDate(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white focus:outline-none"
                />
              </div>

              {/* TRAVELLERS */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                  <Users className="w-3.5 h-3.5 text-blue-600" /> Passengers
                </label>
                <select
                  value={adults}
                  onChange={(e) => setAdults(Number(e.target.value))}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white focus:outline-none"
                >
                  <option value={1}>1 Adult</option>
                  <option value={2}>2 Adults</option>
                  <option value={3}>3 Adults</option>
                  <option value={4}>4 Adults</option>
                </select>
              </div>

              {/* CABIN */}
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1">
                  <Briefcase className="w-3.5 h-3.5 text-blue-600" /> Cabin Class
                </label>
                <select
                  value={cabin}
                  onChange={(e) => setCabin(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2.5 text-sm text-slate-900 font-semibold focus:ring-2 focus:ring-blue-600 focus:bg-white focus:outline-none"
                >
                  <option value="Economy">Economy</option>
                  <option value="Premium Economy">Premium Economy</option>
                  <option value="Business">Business</option>
                  <option value="First">First</option>
                </select>
              </div>
            </div>

            <button
              type="submit"
              className="w-full mt-2 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-black text-sm rounded-xl shadow-lg shadow-blue-600/20 transition-all flex items-center justify-center gap-2"
            >
              <Search className="w-4 h-4" />
              Search Flights & Compare Multi-Provider Fares
            </button>
          </form>
        </div>
      </section>

      {/* TRUST INDICATORS BAR */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-center shadow-sm">
          <p className="text-3xl font-black text-slate-900">50+</p>
          <p className="text-xs text-slate-500 font-bold uppercase mt-1">Routes Monitored</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-center shadow-sm">
          <p className="text-3xl font-black text-blue-600">5+ Airlines</p>
          <p className="text-xs text-slate-500 font-bold uppercase mt-1">IndiGo, AI, Akasa, SG, IX</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-center shadow-sm">
          <p className="text-3xl font-black text-emerald-600">41,800+</p>
          <p className="text-xs text-slate-500 font-bold uppercase mt-1">Observations Monitored</p>
        </div>
        <div className="bg-white border border-slate-200 rounded-2xl p-5 text-center shadow-sm">
          <p className="text-3xl font-black text-amber-600">94.0%</p>
          <p className="text-xs text-slate-500 font-bold uppercase mt-1">Data Quality Score</p>
        </div>
      </section>

      {/* DUAL LAYER ARCHITECTURE OVERVIEW */}
      <section className="space-y-6">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-2xl sm:text-3xl font-black text-slate-900">Dual-Layer Architecture</h2>
          <p className="text-sm text-slate-600 mt-2 font-medium">
            Engineered to serve consumer price transparency alongside high-frequency economic price measurement.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* CONSUMER LAYER CARD */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm hover:border-blue-300 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Plane className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-slate-900">1. Consumer Comparison Layer</h3>
            <p className="text-sm text-slate-600 leading-relaxed font-medium">
              Compare real-time flight offers across major Indian airlines (IndiGo, Air India, Akasa) and OTAs (MakeMyTrip, Goibibo, ixigo, Yatra). Expose itemized base fare, taxes, and convenience fees with lead-time elasticity curves (T+1 to T+45).
            </p>
            <ul className="space-y-2 text-xs font-semibold text-slate-700">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                Multi-OTA Provider Comparison Matrix
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                Itemized Base Fare + Taxes + Fees Breakdown
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-blue-600" />
                Cheapest & Airline Direct Price Badges
              </li>
            </ul>
            <Link
              href="/search"
              className="inline-flex items-center gap-1.5 text-sm font-bold text-blue-600 hover:text-blue-700 pt-2"
            >
              Launch Consumer Flight Search <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* GOVERNMENT LAYER CARD */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm hover:border-cyan-300 transition-colors">
            <div className="w-12 h-12 rounded-xl bg-cyan-50 border border-cyan-200 flex items-center justify-center text-cyan-700">
              <BarChart3 className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-slate-900">2. Government Intelligence Layer</h3>
            <p className="text-sm text-slate-600 leading-relaxed font-medium">
              High-frequency airfare intelligence engine calculating a weighted Real-Time Airfare Price Index (APIx). Supports Laspeyres weighting, route heatmaps, 30-day benchmark backtesting, and automated quality metrics.
            </p>
            <ul className="space-y-2 text-xs font-semibold text-slate-700">
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                Weighted Airfare Price Index (APIx Base Jan 2026 = 100)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                Lead-Time Elasticity Curves (T+1 to T+45)
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-cyan-600" />
                30-Day Benchmark Backtesting (MAE, RMSE, Pearson R)
              </li>
            </ul>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-1.5 text-sm font-bold text-cyan-700 hover:text-cyan-800 pt-2"
            >
              Open Government Dashboard <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
