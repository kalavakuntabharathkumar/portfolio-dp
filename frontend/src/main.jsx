import React from 'react';
import { createRoot } from 'react-dom/client';
import { QueryClient, QueryClientProvider, useQuery } from '@tanstack/react-query';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import './style.css';

const client = new QueryClient();
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function getKpis() {
  const response = await fetch(`${API}/kpis`);
  if (!response.ok) throw new Error('Unable to load KPI data');
  return response.json();
}

function Dashboard() {
  const { data, isLoading, error, refetch } = useQuery({ queryKey: ['kpis'], queryFn: getKpis, refetchInterval: 30000 });
  if (isLoading) return <main><h1>PulseBoard</h1><p>Loading portfolio data…</p></main>;
  if (error) return <main><h1>PulseBoard</h1><p>{error.message}</p><button onClick={() => refetch()}>Retry</button></main>;
  const status = Object.entries(data.by_status || {}).map(([name, value]) => ({ name, value }));
  return <main><header><div><h1>PulseBoard</h1><p>Portfolio operations dashboard</p></div><button onClick={() => refetch()}>Refresh</button></header>
    <section className="cards"><article><span>Records</span><strong>{data.records}</strong></article><article><span>Total value</span><strong>{data.total_value.toLocaleString()}</strong></article><article><span>Average value</span><strong>{data.avg_value.toLocaleString(undefined, {maximumFractionDigits: 0})}</strong></article></section>
    <section className="panel"><h2>Portfolio by status</h2><ResponsiveContainer width="100%" height={300}><BarChart data={status}><XAxis dataKey="name"/><YAxis/><Tooltip/><Bar dataKey="value"/></BarChart></ResponsiveContainer></section>
  </main>;
}

createRoot(document.getElementById('root')).render(<QueryClientProvider client={client}><Dashboard /></QueryClientProvider>);
