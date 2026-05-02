import React, { useState, useEffect } from 'react';
import api from '../api';
import { Activity, Clock, Database, Tag, Users, ShieldAlert, Cpu } from 'lucide-react';

export default function Overview() {
  const [health, setHealth] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const [hRes, mRes] = await Promise.all([
        api.get('/v1/healthz'),
        api.get('/v1/metadata')
      ]);
      setHealth(hRes.data);
      setMetadata(mRes.data);
    } catch (error) {
      console.error("Error fetching overview stats", error);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading) return <div className="text-slate-500 flex items-center gap-2"><Activity className="animate-spin" /> Loading stats...</div>;

  return (
    <div className="max-w-5xl space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-slate-800">System Overview</h1>
        <button onClick={fetchStats} className="bg-white border px-4 py-2 rounded-lg shadow-sm hover:bg-slate-50 text-sm font-medium">
          Refresh Stats
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-xl border shadow-sm flex flex-col gap-2">
          <div className="flex items-center gap-2 text-slate-500">
            <Activity className="w-5 h-5 text-emerald-500" /> Server Status
          </div>
          <div className="text-2xl font-bold uppercase">{health?.status || 'Unknown'}</div>
        </div>
        <div className="bg-white p-6 rounded-xl border shadow-sm flex flex-col gap-2">
          <div className="flex items-center gap-2 text-slate-500">
            <Clock className="w-5 h-5 text-blue-500" /> Uptime
          </div>
          <div className="text-2xl font-bold">{health?.uptime_seconds || 0}s</div>
        </div>
        <div className="bg-white p-6 rounded-xl border shadow-sm flex flex-col gap-2">
          <div className="flex items-center gap-2 text-slate-500">
            <Database className="w-5 h-5 text-indigo-500" /> Total Contexts
          </div>
          <div className="text-2xl font-bold">
            {Object.values(health?.contexts_loaded || {}).reduce((a, b) => a + b, 0)}
          </div>
        </div>
      </div>

      <h2 className="text-xl font-bold text-slate-800 border-b pb-2">Context Breakdown</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(health?.contexts_loaded || {}).map(([key, value]) => (
          <div key={key} className="bg-white p-4 rounded-lg border flex items-center justify-between">
            <span className="capitalize font-medium text-slate-600">{key}</span>
            <span className="font-bold text-lg bg-slate-100 px-3 py-1 rounded-md">{value}</span>
          </div>
        ))}
      </div>

      {metadata && (
        <>
          <h2 className="text-xl font-bold text-slate-800 border-b pb-2 mt-8">Bot Metadata</h2>
          <div className="bg-white p-6 rounded-xl border shadow-sm">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span className="text-slate-500 text-sm block">Team Name</span>
                <span className="font-medium">{metadata.team_name}</span>
              </div>
              <div>
                <span className="text-slate-500 text-sm block">Model</span>
                <span className="font-medium">{metadata.model}</span>
              </div>
              <div>
                <span className="text-slate-500 text-sm block">Version</span>
                <span className="font-medium">{metadata.version}</span>
              </div>
              <div>
                <span className="text-slate-500 text-sm block">Approach</span>
                <span className="font-medium">{metadata.approach}</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
