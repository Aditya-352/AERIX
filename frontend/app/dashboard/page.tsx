'use client';
import {useEffect,useState} from 'react';
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer,BarChart,Bar,CartesianGrid} from 'recharts';
const API=process.env.NEXT_PUBLIC_API_BASE||'http://localhost:8000';

export default function Dashboard(){
  const [d,setD]=useState<any>();
  const [err,setErr]=useState('');
  const load=()=>fetch(`${API}/api/v1/government/overview`).then(r=>r.json()).then(setD).catch(e=>setErr(String(e)));
  useEffect(()=>{load()},[]);

  if(err)return <div className="bg-white border rounded-2xl p-6">Backend unavailable: {err}</div>;
  if(!d)return <div className="p-8 font-medium text-slate-600">Loading government analytics…</div>;

  const synthetic=d.data_mode==='SYNTHETIC_DEMO';

  return (
    <main className="space-y-6">
      <div className="rounded-2xl border-2 border-amber-300 bg-amber-50 p-5">
        <div className="text-xs uppercase font-black tracking-wider text-amber-800">Data Status</div>
        <div className="text-2xl font-black mt-1">{synthetic?'DEMO / SYNTHETIC':'LIVE VERIFIED DATA'}</div>
        <p className="text-sm mt-2">AEROVA is an experimental airfare intelligence system and does not replace official CPI statistics.</p>

        {d.live_verified_observations === 0 && (
          <div className="mt-4 bg-amber-200/90 border border-amber-400 text-amber-950 font-black px-4 py-3 rounded-xl text-xs uppercase tracking-wider flex items-center gap-2 shadow-sm">
            <span>⚠️</span>
            <span>NO VERIFIED LIVE AIRFARE DATA IS CURRENTLY CONTRIBUTING TO APIx. ALL METRICS REFLECT ILLUSTRATIVE SYNTHETIC RESEARCH SERIES.</span>
          </div>
        )}

        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3 mt-4 text-sm">
          <Metric label="Live verified observations" value={d.live_verified_observations}/>
          <Metric label="Synthetic observations" value={d.total_synthetic_observations?.toLocaleString()}/>
          <Metric label="Live routes" value={d.live_routes_count}/>
          <Metric label="Enabled sources" value={`${d.enabled_sources_count} / ${d.total_sources_count}`}/>
        </div>
        <div className="mt-3 text-xs font-bold">Official benchmark: {d.official_benchmark_availability?'AVAILABLE':'NOT AVAILABLE — VERIFIED TMU EXPORT REQUIRED'}</div>
      </div>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card title={synthetic?'Experimental APIx':'APIx'} value={d.index_latest?.index_value??'—'} sub={d.index_latest?`${d.index_latest.daily_change_pct>=0?'+':''}${d.index_latest.daily_change_pct}% daily movement`:''}/>
        <Card title="Current indexed observations" value={d.current_indexed_observations??0} sub={`${d.synthetic_routes_count} configured pilot routes`}/>
        <Card title={synthetic?'Demo Data Quality':'Live Data Quality'} value={synthetic?`${d.quality.overall_score}%`:'N/A'} sub={synthetic?`Live Data Quality: N/A · Completeness ${d.quality.completeness}%`:'Awaiting verified live sample'}/>
        <Card title="Fare anomalies" value={d.anomalies?.length||0} sub={synthetic?'Synthetic Anomaly Screening (MAD 3.5×)':'Live Anomaly Screening'}/>
      </section>

      <section className="bg-white border rounded-2xl p-5">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h2 className="font-black">APIx 90-Day Airfare Movement</h2>
            <p className="text-xs text-slate-500 mt-1">{synthetic?'Illustrative synthetic research series (methodological reference base: 2024=100).':'Verified live observation series.'}</p>
          </div>
          <button onClick={load} className="text-xs font-bold border px-3 py-2 rounded-lg hover:bg-slate-50 transition-colors">Refresh</button>
        </div>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={d.index_series}>
              <CartesianGrid strokeDasharray="3 3"/>
              <XAxis dataKey="period"/>
              <YAxis/>
              <Tooltip/>
              <Line type="monotone" dataKey="index_value" strokeWidth={3} dot={false}/>
            </LineChart>
          </ResponsiveContainer>
        </div>
      </section>

      <div className="grid lg:grid-cols-2 gap-6">
        <section className="bg-white border rounded-2xl p-5">
          <h2 className="font-black mb-1">Lead-Time Booking Window Elasticity</h2>
          <p className="text-xs text-slate-500 mb-3">T+1, T+7, T+15, T+30 and T+45 booking horizons derived from travel date minus collection date.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={d.lead_time}>
                <XAxis dataKey="lead_time"/>
                <YAxis/>
                <Tooltip/>
                <Bar dataKey="avg_fare"/>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="bg-white border rounded-2xl p-5">
          <h2 className="font-black mb-1">Illustrative / Synthetic Fare Decomposition</h2>
          <p className="text-xs text-amber-700 mb-3">Prototype model; not an official government fare-component statistic.</p>
          <div className="space-y-3 text-sm">
            <Row k="Base airfare" v="Illustrative"/>
            <Row k="Taxes" v="Illustrative"/>
            <Row k="Airport / UDF" v="Modelled"/>
            <Row k="Convenience / booking fee" v="Modelled"/>
          </div>
        </section>
      </div>

      <section className="bg-white border rounded-2xl p-5">
        <h2 className="font-black mb-1">Pilot Route Basket — DGCA-Informed Structure</h2>
        <p className="text-xs text-slate-500 mb-3">Pilot Traffic Weight · replace with verified DGCA export before policy-grade release.</p>
        <div className="overflow-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2">Route</th>
                <th>Current avg</th>
                <th>Prior avg</th>
                <th>Change</th>
                <th>Pilot Traffic Weight</th>
              </tr>
            </thead>
            <tbody>
              {d.heatmap.map((x:any)=>(
                <tr key={x.route_id} className="border-b">
                  <td className="py-2 font-bold">{x.route_id}</td>
                  <td>₹{x.current_avg_fare.toLocaleString()}</td>
                  <td>₹{x.prev_avg_fare.toLocaleString()}</td>
                  <td>{x.change_pct}%</td>
                  <td>{(x.traffic_weight*100).toFixed(2)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <div className="grid lg:grid-cols-2 gap-6">
        <section className="bg-white border rounded-2xl p-5">
          <h2 className="font-black mb-4">Source Comparison (Airlines / OTAs)</h2>
          <div className="space-y-2">
            {d.source_comparison.map((x:any)=>(
              <div key={x.source_id} className="flex justify-between text-sm border-b py-2">
                <span className="font-bold text-slate-800">{x.source_id}</span>
                <span>₹{x.avg_fare?.toLocaleString?.()||'N/A'} · {x.observations} obs</span>
              </div>
            ))}
          </div>
        </section>

        <section className="bg-white border rounded-2xl p-5">
          <h2 className="font-black mb-4">Statistical Quality &amp; Provenance Audit</h2>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <Metric label="Completeness" value={`${d.quality.completeness}%`}/>
            <Metric label="Duplicate rate" value={`${d.quality.duplicate_rate}%`}/>
            <Metric label="Outlier rate" value={`${d.quality.outlier_rate}%`}/>
            <Metric label="Missing fare rate" value={`${d.quality.missing_fare_rate}%`}/>
          </div>
          <div className="mt-4 bg-slate-50 border rounded-xl p-3 text-xs text-slate-600 font-mono">
            <b>Scoring Formula:</b> {d.quality.scoring_explanation || "Score = 100 - 3.0×(Missing Rate) - 0.5×(Duplicate Rate) - 1.2×(Outlier Rate)"}
          </div>
        </section>
      </div>

      <div className="bg-slate-900 text-white rounded-2xl p-5">
        <h2 className="font-black">Benchmark &amp; Publication Boundary</h2>
        <p className="text-sm text-slate-300 mt-2">{d.benchmark_status}. No synthetic benchmark comparison is permitted. Use the Backtest page to load a verified DGCA TMU export.</p>
      </div>
    </main>
  );
}

function Metric({label,value}:{label:string,value:any}){
  return <div className="bg-white/60 border rounded-xl p-3"><div className="text-xs text-slate-500">{label}</div><div className="font-black mt-1">{value}</div></div>;
}

function Card({title,value,sub}:{title:string,value:any,sub:string}){
  return <div className="bg-white border rounded-2xl p-5"><div className="text-xs uppercase font-bold text-slate-500">{title}</div><div className="text-3xl font-black mt-1">{value}</div><div className="text-xs text-slate-500 mt-1">{sub}</div></div>;
}

function Row({k,v}:{k:string,v:string}){
  return <div className="flex justify-between border-b pb-2"><span>{k}</span><b>{v}</b></div>;
}
