'use client';

import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { Plane, Filter, ArrowUpDown, ChevronDown, ChevronUp, CheckCircle, ExternalLink, Clock, AlertCircle, ShieldCheck } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { API_BASE_URL } from '@/lib/config';

interface FareBreakdown {
  base_fare: number;
  taxes: number;
  airport_fee: number;
  convenience_fee: number;
  total_fare: number;
}

interface ProviderOffer {
  provider_id: string;
  provider_name: string;
  is_direct: boolean;
  base_fare: number;
  taxes: number;
  fees: number;
  total_fare: number;
  currency: string;
  last_checked_minutes_ago: number;
  is_cheapest: boolean;
  is_best_value: boolean;
  breakdown: FareBreakdown;
}

interface FlightCard {
  flight_id: string;
  airline_code: string;
  airline_name: string;
  flight_number: string;
  origin: string;
  destination: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  stops: number;
  stops_text: string;
  cabin_class: string;
  cheapest_fare: number;
  offers: ProviderOffer[];
}

export default function SearchPage() {
  const searchParams = useSearchParams();
  const origin = searchParams.get('from') || 'DEL';
  const destination = searchParams.get('to') || 'BOM';
  const departureDate = searchParams.get('departure') || '2026-09-15';
  const adults = searchParams.get('adults') || '1';
  const cabin = searchParams.get('cabin') || 'economy';

  const [flights, setFlights] = useState<FlightCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('cheapest');
  const [selectedAirline, setSelectedAirline] = useState('all');
  const [expandedFlightId, setExpandedFlightId] = useState<string | null>(null);
  const [expandedBreakdownId, setExpandedBreakdownId] = useState<string | null>(null);

  useEffect(() => {
    fetchFlights();
  }, [origin, destination, departureDate]);

  const fetchFlights = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/search?origin=${origin}&destination=${destination}&departure_date=${departureDate}`);
      const data = await res.json();
      setFlights(data.flights || []);
    } catch (err) {
      console.error('Error fetching flights:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredFlights = flights.filter(f => {
    if (selectedAirline !== 'all' && f.airline_name !== selectedAirline) return false;
    return true;
  }).sort((a, b) => {
    if (sortBy === 'cheapest') return a.cheapest_fare - b.cheapest_fare;
    if (sortBy === 'earliest') return a.departure_time.localeCompare(b.departure_time);
    return 0;
  });

  const leadTimeMockData = [
    { name: 'T+45', price: Math.round(flights[0]?.cheapest_fare * 0.85 || 4700) },
    { name: 'T+30', price: Math.round(flights[0]?.cheapest_fare * 0.94 || 5100) },
    { name: 'T+15', price: Math.round(flights[0]?.cheapest_fare * 1.08 || 5900) },
    { name: 'T+7', price: Math.round(flights[0]?.cheapest_fare * 1.25 || 6900) },
    { name: 'T+1', price: Math.round(flights[0]?.cheapest_fare * 1.50 || 8200) },
  ];

  return (
    <div className="space-y-6">
      {/* HEADER BAR */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <span className="text-2xl font-black text-slate-900">{origin}</span>
            <Plane className="w-5 h-5 text-blue-600 rotate-90" />
            <span className="text-2xl font-black text-slate-900">{destination}</span>
            <span className="px-3 py-0.5 rounded-full text-xs font-bold bg-blue-100 text-blue-800 border border-blue-200 uppercase">
              {cabin}
            </span>
          </div>
          <p className="text-xs text-slate-600 font-medium mt-1">
            {departureDate} • {adults} Adult • Non-stop
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-sm font-bold text-slate-700">
            {filteredFlights.length} Flights Available
          </span>
          <button
            onClick={fetchFlights}
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-200 transition-colors"
          >
            Refresh Offers
          </button>
        </div>
      </div>

      {/* SORTING & FILTERS ROW */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
        <div className="flex items-center gap-3">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-bold text-slate-700 uppercase">Airline Filter:</span>
          <select
            value={selectedAirline}
            onChange={(e) => setSelectedAirline(e.target.value)}
            className="bg-slate-50 border border-slate-300 rounded-lg px-3 py-1.5 text-xs text-slate-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <option value="all">All Airlines</option>
            <option value="IndiGo">IndiGo</option>
            <option value="Air India">Air India</option>
            <option value="Akasa Air">Akasa Air</option>
            <option value="SpiceJet">SpiceJet</option>
          </select>
        </div>

        <div className="flex items-center gap-3">
          <ArrowUpDown className="w-4 h-4 text-slate-500" />
          <span className="text-xs font-bold text-slate-700 uppercase">Sort By:</span>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setSortBy('cheapest')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                sortBy === 'cheapest' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Cheapest
            </button>
            <button
              onClick={() => setSortBy('earliest')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-colors ${
                sortBy === 'earliest' ? 'bg-blue-600 text-white' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              Earliest Departure
            </button>
          </div>
        </div>
      </div>

      {/* LEAD-TIME ELASTICITY BANNER */}
      <div className="bg-gradient-to-r from-blue-50 via-slate-50 to-white border border-blue-200 rounded-2xl p-5 grid grid-cols-1 lg:grid-cols-3 gap-6 items-center shadow-sm">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-700">
            <Clock className="w-3.5 h-3.5" /> Lead-Time Price Elasticity
          </div>
          <h4 className="text-base font-black text-slate-900">Booking Timing vs Price Curve</h4>
          <p className="text-xs text-slate-600 font-medium">Average price progression from 45 days out down to 1 day before departure.</p>
        </div>
        <div className="h-20 lg:col-span-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={leadTimeMockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 10, fontWeight: 600 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 10, fontWeight: 600 }} domain={['dataMin - 500', 'dataMax + 500']} />
              <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '8px', fontSize: '12px', color: '#0f172a', fontWeight: 600 }} />
              <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2.5} dot={{ r: 4, fill: '#2563eb' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* FLIGHT LISTINGS */}
      {loading ? (
        <div className="text-center py-16 space-y-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-sm font-bold text-slate-600">Fetching multi-provider live fare offers...</p>
        </div>
      ) : filteredFlights.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-2xl p-12 text-center space-y-3 shadow-sm">
          <AlertCircle className="w-10 h-10 text-amber-500 mx-auto" />
          <h3 className="text-lg font-black text-slate-900">No Flights Found</h3>
          <p className="text-xs text-slate-600">Try modifying your departure date or airport routes.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredFlights.map((flight) => {
            const isExpanded = expandedFlightId === flight.flight_id;
            const cheapestOffer = flight.offers.find(o => o.is_cheapest) || flight.offers[0];

            return (
              <div key={flight.flight_id} className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm hover:border-slate-300 transition-colors">
                {/* MAIN CARD BODY */}
                <div className="p-6 grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
                  {/* AIRLINE & FLIGHT NO */}
                  <div className="flex items-center gap-3">
                    <div className="w-11 h-11 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center font-black text-blue-700 text-sm">
                      {flight.airline_code}
                    </div>
                    <div>
                      <h4 className="text-base font-black text-slate-900">{flight.airline_name}</h4>
                      <p className="text-xs font-mono font-semibold text-slate-500">{flight.flight_number}</p>
                    </div>
                  </div>

                  {/* ROUTE & TIME */}
                  <div className="flex items-center gap-4 text-center md:text-left justify-center md:justify-start">
                    <div>
                      <p className="text-xl font-black text-slate-900">{flight.departure_time}</p>
                      <p className="text-xs font-bold text-slate-500">{flight.origin}</p>
                    </div>

                    <div className="flex flex-col items-center">
                      <span className="text-[11px] font-bold text-blue-600">{flight.duration}</span>
                      <div className="w-20 h-0.5 bg-slate-300 relative my-1">
                        <div className="w-2.5 h-2.5 rounded-full bg-blue-600 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"></div>
                      </div>
                      <span className="text-[10px] text-slate-500 font-semibold">{flight.stops_text}</span>
                    </div>

                    <div>
                      <p className="text-xl font-black text-slate-900">{flight.arrival_time}</p>
                      <p className="text-xs font-bold text-slate-500">{flight.destination}</p>
                    </div>
                  </div>

                  {/* CHEAPEST FARE DISPLAY */}
                  <div className="text-center md:text-right">
                    <p className="text-xs font-bold text-slate-500 uppercase">Starting Fare</p>
                    <p className="text-2xl font-black text-emerald-600">₹{flight.cheapest_fare.toLocaleString()}</p>
                    <p className="text-[10px] text-slate-500 font-semibold mt-0.5">at {cheapestOffer?.provider_name}</p>
                  </div>

                  {/* CTA BUTTON */}
                  <div className="flex flex-col items-stretch md:items-end justify-center gap-2">
                    <button
                      onClick={() => setExpandedFlightId(isExpanded ? null : flight.flight_id)}
                      className="px-5 py-2.5 rounded-xl font-bold text-xs bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-600/20 transition-all flex items-center justify-center gap-1.5"
                    >
                      Compare Prices ({flight.offers.length} Providers)
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                    <span className="text-[10px] text-slate-500 font-semibold flex items-center gap-1 justify-center md:justify-end">
                      <Clock className="w-3 h-3 text-emerald-600" /> Price checked 2 min ago
                    </span>
                  </div>
                </div>

                {/* EXPANDED MULTI-PROVIDER COMPARISON MATRIX */}
                {isExpanded && (
                  <div className="border-t border-slate-200 bg-slate-50/80 p-6 space-y-6">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-slate-900 flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-blue-600" />
                        Multi-Provider Price Comparison for {flight.airline_name} {flight.flight_number}
                      </h4>
                      <span className="text-xs font-medium text-slate-600">All prices include mandatory base fare, taxes & fees</span>
                    </div>

                    {/* OFFERS LIST */}
                    <div className="grid grid-cols-1 gap-3">
                      {flight.offers.map((offer) => {
                        const isBreakdownOpen = expandedBreakdownId === `${flight.flight_id}_${offer.provider_id}`;

                        return (
                          <div key={offer.provider_id} className="bg-white border border-slate-200 rounded-xl p-4 space-y-3 shadow-sm">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                              <div className="flex items-center gap-3">
                                <span className="font-bold text-slate-900 text-sm">{offer.provider_name}</span>

                                {offer.is_cheapest && (
                                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-emerald-100 text-emerald-800 border border-emerald-300 uppercase">
                                    CHEAPEST
                                  </span>
                                )}
                                {offer.is_direct && (
                                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-black bg-blue-100 text-blue-800 border border-blue-300 uppercase">
                                    AIRLINE DIRECT
                                  </span>
                                )}
                              </div>

                              <div className="flex items-center gap-4">
                                <div className="text-right">
                                  <span className="text-lg font-black text-slate-900">₹{offer.total_fare.toLocaleString()}</span>
                                  <span className="block text-[10px] text-slate-500 font-semibold">Total fare</span>
                                </div>

                                <button
                                  onClick={() => setExpandedBreakdownId(isBreakdownOpen ? null : `${flight.flight_id}_${offer.provider_id}`)}
                                  className="text-xs font-semibold text-blue-600 hover:text-blue-800 underline"
                                >
                                  {isBreakdownOpen ? 'Hide Breakdown' : 'Fare Breakdown'}
                                </button>

                                <button
                                  onClick={() => alert(`Redirecting to ${offer.provider_name} booking portal...`)}
                                  className="px-4 py-2 rounded-lg text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white transition-colors flex items-center gap-1"
                                >
                                  Book at {offer.provider_name} <ExternalLink className="w-3 h-3" />
                                </button>
                              </div>
                            </div>

                            {/* ITEMIZED FARE BREAKDOWN SECTION */}
                            {isBreakdownOpen && (
                              <div className="mt-3 p-3.5 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5 font-mono text-slate-700">
                                <div className="flex justify-between">
                                  <span>Base Fare</span>
                                  <span className="font-semibold">₹{offer.breakdown.base_fare.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-slate-600">
                                  <span>Taxes & GST</span>
                                  <span>₹{offer.breakdown.taxes.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-slate-600">
                                  <span>Airport User Development Fee</span>
                                  <span>₹{offer.breakdown.airport_fee.toLocaleString()}</span>
                                </div>
                                <div className="flex justify-between text-slate-600">
                                  <span>Convenience Fee</span>
                                  <span>₹{offer.breakdown.convenience_fee.toLocaleString()}</span>
                                </div>
                                <div className="pt-1.5 border-t border-slate-300 flex justify-between font-bold text-slate-900 text-sm">
                                  <span>Total Payable</span>
                                  <span className="text-emerald-700">₹{offer.breakdown.total_fare.toLocaleString()}</span>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
