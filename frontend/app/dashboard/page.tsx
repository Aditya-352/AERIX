'use client';

import React, { useState, useEffect } from 'react';
import {
  BarChart3, TrendingUp, Layers, Activity, ShieldCheck, RefreshCw,
  Sliders, Calendar, AlertTriangle, FileText, Code, CheckCircle2, MapPin, Database, Filter
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, Legend,
  AreaChart, Area
} from 'recharts';
import { API_BASE_URL } from '@/lib/config';

export default function GovernmentDashboard() {
  const [activeTab, setActiveTab] = useState<'overview' | 'apix' | 'routes' | 'leadtime' | 'airlines' | 'quality' | 'backtest' | 'api' | 'admin'>('overview');

  const [overview, setOverview] = useState<any>(null);
  const [indexSeries, setIndexSeries] = useState<any[]>([]);
  const [routes, setRoutes] = useState<any[]>([]);
  const [leadTime, setLeadTime] = useState<any[]>([]);
  const [heatmap, setHeatmap] = useState<any[]>([]);
  const [airlines, setAirlines] = useState<any[]>([]);
  const [otas, setOtas] = useState<any[]>([]);
  const [quality, setQuality] = useState<any>(null);
  const [backtest, setBacktest] = useState<any>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [timeframe, setTimeframe] = useState<'daily' | 'weekly' | 'monthly'>('daily');

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [
        resOverview, resSeries, resRoutes, resLead, resHeat,
        resAir, resOtas, resQual, resBack, resAlerts
      ] = await Promise.all([
        fetch(`${API_BASE_URL}/api/v1/index/overview`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/index/series`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/routes`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/lead-time`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/heatmap`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/airlines`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/otas`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/data-quality`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/backtest`).then(r => r.json()),
        fetch(`${API_BASE_URL}/api/v1/alerts`).then(r => r.json()),
      ]);

      setOverview(resOverview);
      setIndexSeries(resSeries);
      setRoutes(resRoutes);
      setLeadTime(resLead);
      setHeatmap(resHeat);
      setAirlines(resAir);
      setOtas(resOtas);
      setQuality(resQual);
      setBacktest(resBack);
      setAlerts(resAlerts);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="text-center py-24 space-y-4">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
        <p className="text-sm font-bold text-slate-600">Loading Government Airfare Intelligence Engine...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* TOP GOVERNMENT DASHBOARD HEADER */}
      <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-md text-xs font-bold bg-amber-100 text-amber-800 border border-amber-300 mb-2">
            PROTOTYPE / EXPERIMENTAL AIRFARE PRICE INDEX (APIx)
          </div>
          <h1 className="text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-blue-600" />
            Government Airfare Intelligence Dashboard
          </h1>
          <p className="text-xs text-slate-600 font-medium mt-1">
            Augmenting transportation-price measurement with real-time Indian airline & OTA observations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAllData}
            className="px-3.5 py-2 rounded-xl text-xs font-bold bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition-colors flex items-center gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Re-sync Pipeline
          </button>
        </div>
      </div>

      {/* DASHBOARD TAB NAVIGATION */}
      <div className="flex overflow-x-auto gap-2 border-b border-slate-200 pb-2">
        {[
          { id: 'overview', label: 'Overview', icon: Activity },
          { id: 'apix', label: 'Airfare Index (APIx)', icon: TrendingUp },
          { id: 'routes', label: 'Route Basket & Heatmap', icon: MapPin },
          { id: 'leadtime', label: 'Lead-Time Elasticity', icon: Sliders },
          { id: 'airlines', label: 'Airline & OTA Analytics', icon: Layers },
          { id: 'quality', label: 'Data Quality (94%)', icon: ShieldCheck },
          { id: 'backtest', label: '30-Day Backtesting', icon: Database },
          { id: 'api', label: 'API & Methodology', icon: Code },
          { id: 'admin', label: 'Admin & Scraping Jobs', icon: Sliders },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all flex items-center gap-2 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                  : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* SYSTEM ALERTS BANNER */}
      {alerts.length > 0 && (
        <div className="bg-amber-50 border border-amber-300 rounded-xl p-3 flex items-center justify-between gap-3 text-xs shadow-sm">
          <div className="flex items-center gap-2 text-amber-900 font-bold">
            <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0" />
            <span>{alerts[0].title}: {alerts[0].message}</span>
          </div>
          <span className="text-[10px] text-slate-500 font-semibold">{alerts[0].timestamp}</span>
        </div>
      )}

      {/* TAB CONTENT 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* TOP KPI CARDS */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Current APIx Index</span>
              <p className="text-3xl font-black text-slate-900">{overview?.current_apix}</p>
              <span className="text-[10px] text-slate-500 font-semibold">Base Period: Jan 2026 = 100</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Daily Change</span>
              <p className="text-2xl font-black text-emerald-600">+{overview?.daily_change}%</p>
              <span className="text-[10px] text-slate-500 font-semibold">Over last 24 hours</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Weekly Change</span>
              <p className="text-2xl font-black text-blue-600">+{overview?.weekly_change}%</p>
              <span className="text-[10px] text-slate-500 font-semibold">7-day rolling movement</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Monthly Change</span>
              <p className="text-2xl font-black text-amber-600">+{overview?.monthly_change}%</p>
              <span className="text-[10px] text-slate-500 font-semibold">30-day cumulative</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Routes Tracked</span>
              <p className="text-2xl font-black text-slate-900">{overview?.routes_tracked}</p>
              <span className="text-[10px] text-slate-500 font-semibold">Domestic city pairs</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-2xl p-4 space-y-1 shadow-sm">
              <span className="text-xs font-bold text-slate-500 uppercase">Data Quality Score</span>
              <p className="text-2xl font-black text-emerald-600">{overview?.data_quality_score}%</p>
              <span className="text-[10px] text-slate-500 font-semibold">Completeness & Outliers</span>
            </div>
          </div>

          {/* MAIN INDEX TREND GRAPH */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-black text-slate-900">High-Frequency Airfare Price Index (APIx) Movement</h3>
                <p className="text-xs text-slate-600 font-medium">Weighted Laspeyres aggregation across 10 top Indian domestic routes.</p>
              </div>

              <div className="flex items-center gap-1 bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
                {(['daily', 'weekly', 'monthly'] as const).map(tf => (
                  <button
                    key={tf}
                    onClick={() => setTimeframe(tf)}
                    className={`px-3 py-1 rounded-lg font-bold uppercase transition-colors ${
                      timeframe === tf ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={indexSeries}>
                  <defs>
                    <linearGradient id="apixGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25}/>
                      <stop offset="95%" stopColor="#2563eb" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="period" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} domain={['dataMin - 2', 'dataMax + 2']} />
                  <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '12px', fontSize: '12px', color: '#0f172a', fontWeight: 600 }} />
                  <Area type="monotone" dataKey="index_value" stroke="#2563eb" strokeWidth={3} fillOpacity={1} fill="url(#apixGrad)" name="APIx Index Point" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: APIX DETAIL */}
      {activeTab === 'apix' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <h3 className="text-xl font-black text-slate-900">Airfare Price Index (APIx) Time Series</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-700">
              <thead className="bg-slate-100 text-slate-700 uppercase text-[10px] font-extrabold border-b border-slate-200">
                <tr>
                  <th className="p-3">Observation Date</th>
                  <th className="p-3">APIx Index Point</th>
                  <th className="p-3">Daily Change %</th>
                  <th className="p-3">Weekly Change %</th>
                  <th className="p-3">Monthly Change %</th>
                  <th className="p-3">Routes Included</th>
                  <th className="p-3">Observations</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 font-mono">
                {indexSeries.slice().reverse().map((pt, idx) => (
                  <tr key={idx} className="hover:bg-slate-50">
                    <td className="p-3 font-bold text-slate-900">{pt.period}</td>
                    <td className="p-3 text-blue-700 font-extrabold">{pt.index_value}</td>
                    <td className={`p-3 font-bold ${pt.daily_change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {pt.daily_change_pct >= 0 ? '+' : ''}{pt.daily_change_pct}%
                    </td>
                    <td className={`p-3 font-bold ${pt.weekly_change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {pt.weekly_change_pct >= 0 ? '+' : ''}{pt.weekly_change_pct}%
                    </td>
                    <td className={`p-3 font-bold ${pt.monthly_change_pct >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {pt.monthly_change_pct >= 0 ? '+' : ''}{pt.monthly_change_pct}%
                    </td>
                    <td className="p-3 text-slate-600">{pt.total_routes}</td>
                    <td className="p-3 text-slate-600">{pt.total_observations}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB CONTENT 3: ROUTES & HEATMAP */}
      {activeTab === 'routes' && (
        <div className="space-y-6">
          {/* ROUTE HEATMAP GRID */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-black text-slate-900">Geographic Airfare Movement Heatmap</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
              {heatmap.map((h) => (
                <div
                  key={h.route_id}
                  className={`p-4 rounded-xl border flex flex-col justify-between space-y-2 shadow-sm ${
                    h.intensity === 'HIGH_INCREASE'
                      ? 'bg-rose-50 border-rose-200 text-rose-800'
                      : h.intensity === 'MODERATE_INCREASE'
                      ? 'bg-amber-50 border-amber-200 text-amber-800'
                      : 'bg-emerald-50 border-emerald-200 text-emerald-800'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-black text-sm text-slate-900">{h.route_id}</span>
                    <span className="text-[10px] font-mono bg-white px-2 py-0.5 rounded border border-slate-300 font-bold text-slate-700">
                      Wt: {(h.traffic_weight * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div>
                    <p className="text-xl font-black text-slate-900">₹{h.current_avg_fare.toLocaleString()}</p>
                    <p className="text-xs font-bold mt-0.5">
                      {h.change_pct >= 0 ? '+' : ''}{h.change_pct}% over 7d
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* REPRESENTATIVE ROUTE BASKET TABLE */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-black text-slate-900">Representative Route Basket & Passenger Traffic Weighting</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs text-left text-slate-700">
                <thead className="bg-slate-100 text-slate-700 uppercase text-[10px] font-extrabold border-b border-slate-200">
                  <tr>
                    <th className="p-3">Route ID</th>
                    <th className="p-3">Origin</th>
                    <th className="p-3">Destination</th>
                    <th className="p-3">Annual Passenger Traffic</th>
                    <th className="p-3">Traffic Share %</th>
                    <th className="p-3">Index Weight ($w_i$)</th>
                    <th className="p-3">Average Fare</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 font-mono">
                  {routes.map((r) => (
                    <tr key={r.route_id} className="hover:bg-slate-50">
                      <td className="p-3 font-extrabold text-slate-900">{r.route_id}</td>
                      <td className="p-3 text-slate-700 font-medium">{r.origin_name} ({r.origin})</td>
                      <td className="p-3 text-slate-700 font-medium">{r.destination_name} ({r.destination})</td>
                      <td className="p-3 text-slate-600">{r.passenger_traffic_annual.toLocaleString()}</td>
                      <td className="p-3 text-blue-700 font-bold">{r.traffic_share}%</td>
                      <td className="p-3 text-emerald-700 font-bold">{r.weight}</td>
                      <td className="p-3 text-slate-900 font-extrabold">₹{r.avg_fare.toLocaleString()}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 4: LEAD TIME ELASTICITY */}
      {activeTab === 'leadtime' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <div>
            <h3 className="text-lg font-black text-slate-900">Lead-Time Elasticity Curve (T+1 to T+45)</h3>
            <p className="text-xs text-slate-600 font-medium mt-1">
              Demonstrating dynamic advance-booking fare escalation across major domestic airlines.
            </p>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={leadTime}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="lead_time" stroke="#64748b" tick={{ fontSize: 12, fontWeight: 600 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12, fontWeight: 600 }} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '12px', fontSize: '12px', color: '#0f172a', fontWeight: 600 }} />
                <Legend />
                <Line type="monotone" dataKey="avg_fare" stroke="#0f172a" strokeWidth={3} name="Overall Route Average" />
                <Line type="monotone" dataKey="indigo_fare" stroke="#2563eb" strokeWidth={2.5} name="IndiGo" />
                <Line type="monotone" dataKey="airindia_fare" stroke="#dc2626" strokeWidth={2.5} name="Air India" />
                <Line type="monotone" dataKey="akasa_fare" stroke="#059669" strokeWidth={2.5} name="Akasa Air" />
                <Line type="monotone" dataKey="spicejet_fare" stroke="#d97706" strokeWidth={2.5} name="SpiceJet" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* TAB CONTENT 5: AIRLINES & OTAS */}
      {activeTab === 'airlines' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AIRLINE ANALYTICS */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-black text-slate-900">Airline Fare & Volatility Analytics</h3>
            <div className="space-y-3">
              {airlines.map((a) => (
                <div key={a.code} className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{a.airline_name} ({a.code})</h4>
                    <p className="text-xs text-slate-600 font-medium mt-0.5">Avg Fare: ₹{a.avg_fare.toLocaleString()}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                      a.volatility === 'Low' ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' :
                      a.volatility === 'Medium' ? 'bg-amber-100 text-amber-800 border border-amber-300' :
                      'bg-rose-100 text-rose-800 border border-rose-300'
                    }`}>
                      {a.volatility} Volatility ({a.volatility_score}%)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* OTA ANALYTICS */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-4 shadow-sm">
            <h3 className="text-lg font-black text-slate-900">OTA Provider Price Discrepancy Matrix</h3>
            <div className="space-y-3">
              {otas.map((o) => (
                <div key={o.provider_name} className="bg-slate-50 p-4 rounded-xl border border-slate-200 flex items-center justify-between">
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{o.provider_name}</h4>
                    <p className="text-xs text-slate-600 font-medium mt-0.5">Avg Fees: ₹{o.fee_avg}</p>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-bold text-blue-700">
                      {o.avg_price_diff_pct >= 0 ? '+' : ''}{o.avg_price_diff_pct}% vs Direct
                    </span>
                    <span className="block text-[10px] text-slate-500 font-semibold">Consistency Score: {o.fare_consistency_score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 6: DATA QUALITY */}
      {activeTab === 'quality' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-black text-slate-900">Data Quality & Statistical Integrity Dashboard</h3>
              <p className="text-xs text-slate-600 font-medium mt-1">Auditing collection completeness, duplicate records, and outlier rates.</p>
            </div>
            <div className="px-4 py-2 rounded-xl bg-emerald-100 border border-emerald-300 text-emerald-800 font-black text-lg">
              Overall Quality: {quality?.overall_score}%
            </div>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-600 font-semibold">Completeness</span>
              <p className="text-2xl font-black text-slate-900">{quality?.completeness}%</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-600 font-semibold">Duplicate Rate</span>
              <p className="text-2xl font-black text-amber-600">{quality?.duplicate_rate}%</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-600 font-semibold">Missing Fare Rate</span>
              <p className="text-2xl font-black text-emerald-600">{quality?.missing_fare_rate}%</p>
            </div>
            <div className="bg-slate-50 p-4 rounded-xl border border-slate-200">
              <span className="text-xs text-slate-600 font-semibold">IQR Outlier Rate</span>
              <p className="text-2xl font-black text-blue-600">{quality?.outlier_rate}%</p>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 7: 30-DAY BACKTESTING */}
      {activeTab === 'backtest' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h3 className="text-xl font-black text-slate-900">30-Day Benchmark Backtesting & Validation</h3>
              <p className="text-xs text-slate-600 font-medium mt-1">
                Comparing computed APIx against benchmark reference transportation price series.
              </p>
            </div>
            <div className="flex items-center gap-3 text-xs font-mono">
              <div className="bg-emerald-50 px-3 py-1.5 rounded-lg border border-emerald-200 text-emerald-800 font-bold">
                Pearson R = {backtest?.pearson_correlation}
              </div>
              <div className="bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200 text-blue-800 font-bold">
                MAE = {backtest?.mae}
              </div>
              <div className="bg-amber-50 px-3 py-1.5 rounded-lg border border-amber-200 text-amber-800 font-bold">
                RMSE = {backtest?.rmse}
              </div>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={backtest?.data_points}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11, fontWeight: 600 }} domain={['dataMin - 2', 'dataMax + 2']} />
                <Tooltip contentStyle={{ backgroundColor: '#ffffff', borderColor: '#cbd5e1', borderRadius: '12px', fontSize: '12px', color: '#0f172a', fontWeight: 600 }} />
                <Legend />
                <Line type="monotone" dataKey="apix" stroke="#2563eb" strokeWidth={3} name="AEROVA APIx" />
                <Line type="monotone" dataKey="benchmark" stroke="#059669" strokeWidth={2.5} strokeDasharray="5 5" name="Benchmark Reference" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* TAB CONTENT 8: API & METHODOLOGY */}
      {activeTab === 'api' && (
        <div className="bg-white border border-slate-200 rounded-2xl p-6 space-y-6 shadow-sm">
          <h3 className="text-xl font-black text-slate-900">API Documentation & Index Methodology</h3>

          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-2 text-xs font-mono">
            <p className="text-blue-700 font-bold">// Airfare Price Index Formula</p>
            <p className="text-slate-800 font-semibold">
              Index_t = ( Σ( weight_i × normalized_price_i,t ) / Σ( weight_i × normalized_price_i,base ) ) × 100
            </p>
            <p className="text-slate-500">// Base Period: January 2026 = 100.0</p>
          </div>

          <div className="space-y-3 text-xs">
            <p className="font-bold text-slate-900">Available REST API Endpoints:</p>
            <div className="space-y-2">
              <code className="block p-2.5 bg-slate-50 rounded border border-slate-200 text-blue-700 font-bold">
                GET {API_BASE_URL}/api/v1/index/series
              </code>
              <code className="block p-2.5 bg-slate-50 rounded border border-slate-200 text-blue-700 font-bold">
                GET {API_BASE_URL}/api/v1/lead-time?route_id=DEL-BOM
              </code>
              <code className="block p-2.5 bg-slate-50 rounded border border-slate-200 text-blue-700 font-bold">
                GET {API_BASE_URL}/api/v1/backtest
              </code>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
