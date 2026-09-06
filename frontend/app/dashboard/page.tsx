'use client';
import {useEffect,useState} from 'react';
import {LineChart,Line,XAxis,YAxis,Tooltip,ResponsiveContainer,BarChart,Bar,CartesianGrid} from 'recharts';
import {ShieldCheck,DatabaseZap,TrendingUp,AlertTriangle,RefreshCw} from 'lucide-react';
const API=process.env.NEXT_PUBLIC_API_BASE||'http://localhost:8000';
export default function Dashboard(){
 const [d,setD]=useState<any>(null); const [err,setErr]=useState('');
 const load=()=>fetch(`${API}/api/v1/government/overview`).then(r=>r.json()).then(setD).catch(e=>setErr(String(e)));
 useEffect(()=>{load()},[]);
 if(err)return <main className="p-8"><div className="rounded-2xl border p-6 bg-white">Backend unavailable: {err}</div></main>;
 if(!d)return <main className="p-8">Loading government analytics…</main>;
 return <main className="max-w-7xl mx-auto p-4 sm:p-8 space-y-6">
  <div className={`rounded-2xl border p-4 ${d.data_mode==='LIVE'?'bg-emerald-50 border-emerald-200':'bg-amber-50 border-amber-200'}`}><div className="font-black">{d.data_mode==='LIVE'?'LIVE COLLECTION':'SYNTHETIC DEMO / RESEARCH MODE'}</div><div className="text-xs mt-1">No synthetic values are presented as official observations. Use the release checklist before policy publication.</div></div>
  <section className="grid grid-cols-2 lg:grid-cols-4 gap-4">
   <Card icon={<TrendingUp/>} title="APIx" value={d.index_latest?d.index_latest.index_value:'—'} sub={d.index_latest?`${d.index_latest.daily_change_pct>=0?'+':''}${d.index_latest.daily_change_pct}% today`:''}/>
   <Card icon={<DatabaseZap/>} title="Observations" value={d.index_latest?.total_observations??0} sub={`Mode: ${d.data_mode}`}/>
   <Card icon={<ShieldCheck/>} title="Quality" value={`${d.quality.overall_score}%`} sub={`Completeness ${d.quality.completeness}%`}/>
   <Card icon={<AlertTriangle/>} title="Anomalies" value={d.anomalies.length} sub="Robust MAD screen"/>
  </section>
  <section className="bg-white border rounded-2xl p-5"><div className="flex justify-between items-center mb-4"><h2 className="font-black">APIx trend</h2><button onClick={load} className="text-xs font-bold flex items-center gap-1"><RefreshCw size={14}/>Refresh</button></div><div className="h-72"><ResponsiveContainer width="100%" height="100%"><LineChart data={d.index_series}><CartesianGrid strokeDasharray="3 3"/><XAxis dataKey="period"/><YAxis/><Tooltip/><Line type="monotone" dataKey="index_value" strokeWidth={3} dot={false}/></LineChart></ResponsiveContainer></div></section>
  <div className="grid lg:grid-cols-2 gap-6">
   <section className="bg-white border rounded-2xl p-5"><h2 className="font-black mb-4">Lead-time elasticity</h2><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={d.lead_time}><XAxis dataKey="lead_time"/><YAxis/><Tooltip/><Bar dataKey="avg_fare"/></BarChart></ResponsiveContainer></div></section>
   <section className="bg-white border rounded-2xl p-5"><h2 className="font-black mb-4">Source comparison</h2><div className="space-y-2">{d.source_comparison.map((x:any)=><div key={x.source_id} className="flex justify-between text-sm border-b py-2"><span>{x.source_id}</span><span>₹{x.avg_fare.toLocaleString()} · {x.observations} obs</span></div>)}</div></section>
  </div>
  <section className="bg-white border rounded-2xl p-5"><h2 className="font-black mb-4">Route heatmap table</h2><div className="overflow-auto"><table className="min-w-full text-sm"><thead><tr className="text-left border-b"><th className="py-2">Route</th><th>Current</th><th>Previous</th><th>Change</th><th>Weight</th></tr></thead><tbody>{d.heatmap.map((x:any)=><tr key={x.route_id} className="border-b"><td className="py-2 font-bold">{x.route_id}</td><td>₹{x.current_avg_fare.toLocaleString()}</td><td>₹{x.prev_avg_fare.toLocaleString()}</td><td>{x.change_pct}%</td><td>{(x.traffic_weight*100).toFixed(2)}%</td></tr>)}</tbody></table></div></section>
  <p className="text-xs text-slate-500">Methodology v{d.index_latest?.methodology_version||'2.0'} · Current CPI series base year is 2024=100; APIx is an experimental high-frequency airfare index, not a replacement for official CPI.</p>
 </main>
}
function Card({icon,title,value,sub}:{icon:any,title:string,value:any,sub:string}){return <div className="bg-white border rounded-2xl p-5"><div className="text-blue-600">{icon}</div><div className="text-xs uppercase font-bold text-slate-500 mt-2">{title}</div><div className="text-3xl font-black mt-1">{value}</div><div className="text-xs text-slate-500 mt-1">{sub}</div></div>}
