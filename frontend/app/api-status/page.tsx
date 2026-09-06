'use client';
import {useEffect, useState} from 'react';
import {DatabaseZap, ShieldCheck, Radio, Play, CheckCircle, AlertCircle, RefreshCw} from 'lucide-react';
const API = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function ApiStatus() {
  const [sources, setSources] = useState<any[]>([]);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [testResult, setTestResult] = useState<any>(null);
  const [collecting, setCollecting] = useState(false);
  const [selectedSource, setSelectedSource] = useState('INDIGO_PUBLIC_ROUTE');

  const loadData = () => {
    Promise.all([
      fetch(`${API}/api/v1/collection/sources`).then(r => r.json()),
      fetch(`${API}/api/v1/collection/recent?limit=30`).then(r => r.json())
    ]).then(([a, b]) => {
      setSources(a);
      setRecent(b);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  };

  useEffect(() => { loadData(); }, []);

  const runTestCollection = () => {
    setCollecting(true);
    setTestResult(null);
    fetch(`${API}/api/v1/collection/collect?source_id=${selectedSource}&origin=DEL&destination=BOM&travel_date=2026-09-20`, {method: 'POST'})
      .then(r => r.json())
      .then(res => {
        setTestResult(res);
        setCollecting(false);
        loadData();
      })
      .catch(err => {
        setTestResult({error: String(err)});
        setCollecting(false);
      });
  };

  if (loading) return <main className="max-w-6xl mx-auto p-8 font-medium text-slate-600">Loading source registry & audit log…</main>;

  const airlines = sources.filter(x => x.source_type === 'AIRLINE_DIRECT');
  const otas = sources.filter(x => x.source_type === 'OTA');

  const badge = (s: string) =>
    s === 'LIVE_PUBLIC_ADAPTER' ? 'bg-emerald-100 text-emerald-800 border-emerald-300' :
    s === 'AUTHORIZED_FEED_REQUIRED' ? 'bg-amber-100 text-amber-900 border-amber-300' :
    'bg-slate-100 text-slate-700 border-slate-300';

  const auditBadge = (s: string) =>
    s === 'SUCCESS' ? 'bg-emerald-100 text-emerald-800' :
    s === 'BLOCKED' ? 'bg-rose-100 text-rose-800' :
    s === 'NO_DATA' ? 'bg-amber-100 text-amber-900' :
    'bg-slate-100 text-slate-700';

  const liveRouteCount = new Set(recent.filter(x => x.collection_status === 'SUCCESS').map(x => `${x.origin}-${x.destination}`)).size;

  return (
    <main className="max-w-6xl mx-auto p-4 sm:p-8 space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-black text-slate-900">Data Source Registry &amp; Ingestion</h1>
          <p className="text-sm text-slate-600 mt-1">Collection status, compliance posture, provenance and live audit outcomes.</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={selectedSource}
            onChange={e => setSelectedSource(e.target.value)}
            className="border rounded-xl px-3 py-2 text-xs font-bold bg-white text-slate-800 focus:outline-blue-600"
          >
            {sources.map(s => (
              <option key={s.source_id} value={s.source_id}>{s.source_name} ({s.status})</option>
            ))}
          </select>
          <button
            onClick={runTestCollection}
            disabled={collecting}
            className="bg-blue-600 hover:bg-blue-700 text-white rounded-xl px-4 py-2 font-bold text-xs flex items-center gap-2 transition-colors shrink-0 disabled:opacity-50"
          >
            {collecting ? <RefreshCw size={14} className="animate-spin"/> : <Play size={14}/>}
            {collecting ? 'Running Scraper…' : 'Test Scrape'}
          </button>
        </div>
      </div>

      {testResult && (
        <div className="bg-white border rounded-2xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 font-bold text-sm text-slate-900">
              {testResult.error || testResult.collection_status === 'FAILED' || testResult.collection_status === 'BLOCKED' ? (
                <AlertCircle className="text-rose-600" size={16}/>
              ) : (
                <CheckCircle className="text-emerald-600" size={16}/>
              )}
              Collector Execution Result: {testResult.source_id}
            </div>
            <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold border ${badge(testResult.collection_status)}`}>
              {testResult.collection_status || 'DONE'}
            </span>
          </div>
          <pre className="text-xs bg-slate-900 text-slate-100 p-4 rounded-xl overflow-auto font-mono max-h-48">
            {JSON.stringify(testResult, null, 2)}
          </pre>
        </div>
      )}

      {/* Metric Summary Cards */}
      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border rounded-2xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Airlines Enabled / Total</div>
          <div className="text-2xl font-black mt-1 text-slate-900">{airlines.filter(x => x.status === 'LIVE_PUBLIC_ADAPTER').length} / {airlines.length}</div>
          <div className="text-xs text-slate-500 mt-1 truncate">
            {airlines.filter(x => x.status === 'LIVE_PUBLIC_ADAPTER').map(x => x.source_name).join(', ') || 'None'}
          </div>
        </div>
        <div className="bg-white border rounded-2xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">OTAs Enabled / Total</div>
          <div className="text-2xl font-black mt-1 text-slate-900">{otas.filter(x => x.status === 'LIVE_PUBLIC_ADAPTER').length} / {otas.length}</div>
          <div className="text-xs text-slate-500 mt-1 truncate">
            {otas.filter(x => x.status === 'LIVE_PUBLIC_ADAPTER').map(x => x.source_name).join(', ') || 'None'}
          </div>
        </div>
        <div className="bg-white border rounded-2xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Configured Routes</div>
          <div className="text-2xl font-black mt-1 text-slate-900">20</div>
          <div className="text-xs text-slate-500 mt-1">Pilot Route Basket</div>
        </div>
        <div className="bg-white border rounded-2xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Live Verified Fares</div>
          <div className="text-2xl font-black mt-1 text-blue-600">{recent.filter(x => x.collection_status === 'SUCCESS' && x.total_fare > 0).length}</div>
          <div className="text-xs text-slate-500 mt-1">{liveRouteCount} active live route(s)</div>
        </div>
      </section>

      {/* Sources Grid: All 11 SIH-scoped sources */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-900 flex items-center gap-2">
            <Radio size={18} className="text-blue-600"/> All 11 SIH-Scoped Sources ({sources.length})
          </h2>
          <span className="text-xs text-slate-500">5 Airlines · 6 OTAs</span>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {sources.map(x => (
            <div key={x.source_id} className="bg-white border shadow-sm rounded-2xl p-5 flex flex-col justify-between hover:border-slate-300 transition-colors">
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-black text-base text-slate-900">{x.source_name}</div>
                    <div className="text-xs text-slate-500 mt-0.5">{x.source_type} · {x.source_granularity} · Parser v{x.parser_version}</div>
                  </div>
                  <div className="text-right">
                    <span className="block text-[9px] text-slate-400 font-semibold uppercase">Adapter Status</span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border ${badge(x.status)}`}>
                      {x.status}
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs mt-3 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                  <span>Robots.txt: <b className="text-slate-800">{x.robots_status}</b></span>
                  <span>Authorization: <b className="text-slate-800">{x.authorization_status}</b></span>
                  <span>Live Verified Obs: <b className="text-blue-600">{x.live_observations}</b></span>
                  <span>Last Success: <b className="text-slate-700">{x.last_success || 'N/A'}</b></span>
                </div>
              </div>
              <div className="mt-3 pt-3 border-t text-xs text-slate-600 flex items-center gap-1.5">
                <ShieldCheck size={14} className="text-emerald-600 shrink-0"/>
                <span className="truncate">{x.policy}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Collection Audit Log */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-black text-slate-900 flex items-center gap-2">
            <DatabaseZap size={18} className="text-indigo-600"/> Collection Audit Log ({recent.length} recent events)
          </h2>
          <span className="text-xs text-slate-500 font-mono">Failed/blocked events retained for governance auditability</span>
        </div>
        {recent.length === 0 ? (
          <div className="bg-white border rounded-2xl p-6 text-center text-slate-500 text-sm">
            No audit records stored yet. Run a collection test above to record an audit trail.
          </div>
        ) : (
          <div className="bg-white border shadow-sm rounded-2xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full text-xs">
                <thead className="bg-slate-50 border-b text-slate-500 uppercase font-semibold">
                  <tr>
                    <th className="py-2.5 px-4 text-left">Status</th>
                    <th className="py-2.5 px-4 text-left">Source</th>
                    <th className="py-2.5 px-4 text-left">Route</th>
                    <th className="py-2.5 px-4 text-left">Travel Date</th>
                    <th className="py-2.5 px-4 text-left">Total Fare</th>
                    <th className="py-2.5 px-4 text-left">Reason / Error</th>
                    <th className="py-2.5 px-4 text-left">Collected At</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-mono">
                  {recent.map((r: any) => {
                    const st = r.collection_status === 'ERROR' ? 'FAILED' : (r.collection_status || 'UNKNOWN');
                    return (
                      <tr key={r.id} className="hover:bg-slate-50">
                        <td className="py-2.5 px-4">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${auditBadge(st)}`}>
                            {st}
                          </span>
                        </td>
                        <td className="py-2.5 px-4 font-bold text-slate-800">{r.source_name || r.source_id}</td>
                        <td className="py-2.5 px-4 font-bold text-slate-700">{r.origin}-{r.destination}</td>
                        <td className="py-2.5 px-4 text-slate-600">{r.travel_date}</td>
                        <td className="py-2.5 px-4 font-bold text-blue-600">
                          {r.total_fare && Number(r.total_fare) > 0 ? `₹${Number(r.total_fare).toLocaleString()}` : '—'}
                        </td>
                        <td className="py-2.5 px-4 text-slate-500 max-w-xs truncate font-sans text-[11px]" title={r.error || ''}>
                          {r.error || '—'}
                        </td>
                        <td className="py-2.5 px-4 text-slate-400 text-[11px]">{r.collected_at}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

