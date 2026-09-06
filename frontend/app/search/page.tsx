'use client';
import {useState, useEffect} from 'react';
import {Search,ChevronDown,ChevronUp,ShieldCheck,Plane,Calendar,Tag} from 'lucide-react';
const API=process.env.NEXT_PUBLIC_API_BASE||'http://localhost:8000';

const PRESETS = [
  {o:'DEL', d:'BOM', l:'Delhi → Mumbai'},
  {o:'DEL', d:'BLR', l:'Delhi → Bengaluru'},
  {o:'BOM', d:'BLR', l:'Mumbai → Bengaluru'},
  {o:'DEL', d:'HYD', l:'Delhi → Hyderabad'},
  {o:'BOM', d:'CCU', l:'Mumbai → Kolkata'}
];

export default function SearchPage(){
 const [origin,setOrigin]=useState('DEL'),[destination,setDestination]=useState('BOM'),[date,setDate]=useState('2026-09-20'),[data,setData]=useState<any>(null),[open,setOpen]=useState(''),[loading,setLoading]=useState(false);
 
 const runSearch=(orig: string, dest: string, d: string)=>{
   setLoading(true);
   fetch(`${API}/api/v1/search?origin=${orig}&destination=${dest}&departure_date=${d}`)
     .then(r=>r.json())
     .then(d=>{ setData(d); setLoading(false); })
     .catch(()=>{ setLoading(false); });
 };

 const submit=(e?:any)=>{
   e?.preventDefault?.();
   runSearch(origin, destination, date);
 };

 useEffect(()=>{
   runSearch(origin, destination, date);
 },[]);

 const selectPreset=(orig: string, dest: string)=>{
   setOrigin(orig);
   setDestination(dest);
   runSearch(orig, dest, date);
 };

 return <main className="max-w-6xl mx-auto p-4 sm:p-8 space-y-6">
   <div className="space-y-2">
     <h1 className="text-3xl font-black text-slate-900">Consumer Fare Comparison</h1>
     <p className="text-sm text-slate-600">Cross-airline and multi-provider domestic flight price transparency with full fare component breakdown.</p>
   </div>

   <div className="flex flex-wrap gap-2 items-center">
     <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Popular routes:</span>
     {PRESETS.map(p=>(
       <button key={p.l} onClick={()=>selectPreset(p.o, p.d)} className={`text-xs px-3 py-1.5 rounded-full border transition-colors ${origin===p.o && destination===p.d ? 'bg-blue-600 text-white border-blue-600 font-bold' : 'bg-white hover:bg-slate-100 text-slate-700'}`}>
         {p.l}
       </button>
     ))}
   </div>

   <form onSubmit={submit} className="bg-white border shadow-sm rounded-2xl p-5 grid sm:grid-cols-4 gap-3">
     <div>
       <label className="block text-xs font-bold text-slate-500 mb-1">Origin (IATA)</label>
       <input value={origin} onChange={e=>setOrigin(e.target.value.toUpperCase())} placeholder="DEL" className="w-full border rounded-xl px-3 py-2 font-mono font-bold text-slate-800 focus:outline-blue-600"/>
     </div>
     <div>
       <label className="block text-xs font-bold text-slate-500 mb-1">Destination (IATA)</label>
       <input value={destination} onChange={e=>setDestination(e.target.value.toUpperCase())} placeholder="BOM" className="w-full border rounded-xl px-3 py-2 font-mono font-bold text-slate-800 focus:outline-blue-600"/>
     </div>
     <div>
       <label className="block text-xs font-bold text-slate-500 mb-1">Departure Date</label>
       <input type="date" value={date} onChange={e=>setDate(e.target.value)} className="w-full border rounded-xl px-3 py-2 font-mono text-slate-800 focus:outline-blue-600"/>
     </div>
     <div className="flex items-end">
       <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white rounded-xl py-2.5 font-bold flex gap-2 items-center justify-center transition-colors">
         <Search size={16}/>{loading ? 'Searching…' : 'Compare Fares'}
       </button>
     </div>
   </form>

   {data&&<>
     <div className={`rounded-2xl border p-4 flex items-start gap-3 ${data.data_mode==='LIVE'?'bg-emerald-50 border-emerald-200 text-emerald-950':'bg-amber-50 border-amber-200 text-amber-950'}`}>
       <ShieldCheck className={data.data_mode==='LIVE'?'text-emerald-600 mt-0.5':'text-amber-600 mt-0.5'} size={20}/>
       <div className="text-xs leading-relaxed">
         <div>Data Mode: <b className="uppercase tracking-wider">{data.data_mode}</b> · Found {data.total_flights} flight options for {data.origin} → {data.destination} on {data.travel_date}</div>
         <div className="text-slate-600 mt-0.5">{data.data_mode==='LIVE' ? 'Real-time observation acquired via verified public collection.' : 'Deterministic synthetic demo data for testing; clearly distinguished and not official government statistics.'}</div>
       </div>
     </div>

     <div className="space-y-4">
       {data.flights.map((f:any)=><div key={f.flight_id} className="bg-white border shadow-sm rounded-2xl p-5 hover:border-slate-300 transition-colors">
         <div className="grid md:grid-cols-4 gap-4 items-center">
           <div>
             <div className="font-black text-lg text-slate-900">{f.airline_name}</div>
             <div className="text-xs font-mono text-slate-500">{f.flight_number} · {f.cabin_class || 'Economy'}</div>
           </div>
           <div>
             <div className="font-bold text-slate-800 flex items-center gap-1.5"><Plane size={15} className="text-blue-600 rotate-45"/> {f.origin} → {f.destination}</div>
             <div className="text-xs text-slate-500 mt-0.5">{f.departure_time} – {f.arrival_time} · {f.duration} · {f.stops_text || (f.stops === 0 ? 'Non-stop' : `${f.stops} stop`)}</div>
           </div>
           <div>
             <div className="text-xs text-slate-500 font-semibold">{data.data_mode==='LIVE'?'Observed fare':'Synthetic starting estimate'}</div>
             <div className="text-2xl font-black text-blue-600">₹{f.cheapest_fare.toLocaleString()}</div>
             <span className={`inline-flex mt-1 px-2 py-0.5 rounded-full text-[10px] font-black ${data.data_mode==='LIVE'?'bg-emerald-100 text-emerald-800':'bg-amber-100 text-amber-900 border border-amber-300'}`}>
               {data.data_mode==='LIVE'?'LIVE VERIFIED FARE':'DEMO FARE'}
             </span>
           </div>
           <button onClick={()=>setOpen(open===f.flight_id?'':f.flight_id)} className="border border-slate-300 hover:bg-slate-50 rounded-xl px-4 py-2.5 font-bold text-sm flex items-center justify-center gap-2 transition-colors">
             Compare {f.offers?.length || 0} Offers {open===f.flight_id?<ChevronUp size={16}/>:<ChevronDown size={16}/>}
           </button>
         </div>

         {open===f.flight_id&&<div className="mt-5 pt-4 border-t space-y-3">
           <div className="text-xs font-bold uppercase tracking-wider text-slate-500">Provider Price Comparison & Breakdown</div>
           <div className="grid gap-2.5">
             {f.offers.map((o:any)=><div key={o.provider_id} className={`border rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 ${o.is_cheapest ? 'bg-emerald-50/50 border-emerald-300' : 'bg-slate-50/50'}`}>
               <div>
                 <div className="flex items-center gap-2">
                   <span className="font-bold text-slate-900">{o.provider_name}</span>
                   {o.is_direct && <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-bold">Direct Airline</span>}
                   {o.is_cheapest && <span className="text-[10px] bg-emerald-600 text-white px-2 py-0.5 rounded-full font-bold">Cheapest</span>}
                   <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${o.source_status==='LIVE_VERIFIED'?'bg-emerald-100 text-emerald-800':'bg-amber-100 text-amber-800'}`}>{o.source_status}</span>
                 </div>
                 <div className="text-xs text-slate-500 flex gap-1.5 items-center mt-1">
                   <ShieldCheck size={12}/> {o.last_checked_minutes_ago !== null && o.last_checked_minutes_ago !== undefined ? `Observed ${o.last_checked_minutes_ago}m ago` : 'Simulated prototype estimate'}
                 </div>
               </div>
               <div className="sm:text-right">
                 <div className="text-xl font-black text-slate-900">₹{o.total_fare.toLocaleString()}</div>
                 <div className="text-xs text-slate-500 mt-0.5">
                   Base ₹{o.breakdown.base_fare.toLocaleString()} · Taxes ₹{o.breakdown.taxes.toLocaleString()} · Airport ₹{(o.breakdown.airport_fee||0).toLocaleString()} · Convenience ₹{(o.breakdown.convenience_fee||0).toLocaleString()}
                 </div>
               </div>
             </div>)}
           </div>
         </div>}
       </div>)}
     </div>
   </>}
 </main>;
}
