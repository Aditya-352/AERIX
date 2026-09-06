'use client';
import {useEffect,useState} from 'react';
const API=process.env.NEXT_PUBLIC_API_BASE||'http://localhost:8000';
export default function ApiStatus(){const [d,setD]=useState<any>();useEffect(()=>{fetch(`${API}/api/v1/collection/sources`).then(r=>r.json()).then(setD)},[]);return <main className="max-w-5xl mx-auto p-6 sm:p-10"><h1 className="text-3xl font-black mb-5">Data Source Registry</h1><div className="space-y-3">{(d||[]).map((x:any)=><div key={x.source_id} className="bg-white border rounded-2xl p-5"><div className="font-black">{x.source_name} · {x.source_id}</div><div className="text-xs text-slate-500 mt-1">{x.source_type} · {x.source_granularity} · parser {x.parser_version}</div><div className="text-xs mt-2">{x.policy}</div></div>)}</div></main>}
