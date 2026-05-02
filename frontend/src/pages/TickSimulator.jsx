import React, { useState, useEffect } from 'react';
import api from '../api';
import { Play, Copy, RefreshCw, Zap } from 'lucide-react';

export default function TickSimulator() {
  const [triggersStr, setTriggersStr] = useState('t_001, t_002');
  const [actions, setActions] = useState([]);
  const [rawResponse, setRawResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [availableTriggers, setAvailableTriggers] = useState([]);

  useEffect(() => {
    // Fetch available triggers for convenience
    api.get('/debug/triggers').then(res => {
      setAvailableTriggers(res.data);
    }).catch(console.error);
  }, []);

  const handleRunTick = async () => {
    setLoading(true);
    setActions([]);
    setRawResponse(null);
    try {
      const triggerList = triggersStr.split(',').map(s => s.trim()).filter(Boolean);
      const res = await api.post('/v1/tick', {
        now: new Date().toISOString(),
        available_triggers: triggerList
      });
      setActions(res.data.actions || []);
      setRawResponse(res.data);
    } catch (err) {
      console.error(err);
      setRawResponse({ error: err.response?.data || err.message });
    }
    setLoading(false);
  };

  const loadAllStored = () => {
    setTriggersStr(availableTriggers.join(', '));
  };

  return (
    <div className="max-w-5xl">
      <h1 className="text-3xl font-bold text-slate-800 mb-6">Tick Simulator</h1>
      
      <div className="bg-white p-6 rounded-xl border shadow-sm mb-8">
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1 flex justify-between">
            <span>Available Triggers (Comma separated)</span>
            <button onClick={loadAllStored} className="text-primary text-xs hover:underline flex items-center gap-1">
              <RefreshCw className="w-3 h-3" /> Load Stored Triggers
            </button>
          </label>
          <input 
            type="text" 
            value={triggersStr} 
            onChange={e => setTriggersStr(e.target.value)}
            className="w-full border rounded-md p-3 bg-slate-50 focus:ring-2 ring-primary outline-none"
            placeholder="trg_001, trg_002"
          />
        </div>

        <button 
          onClick={handleRunTick} 
          disabled={loading}
          className="flex items-center gap-2 bg-slate-800 text-white px-6 py-2 rounded-lg font-medium hover:bg-slate-700 disabled:opacity-50 transition-colors"
        >
          {loading ? <span className="animate-pulse">Processing...</span> : <><Play className="w-4 h-4 fill-current" /> Run Tick</>}
        </button>
      </div>

      {actions.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Zap className="text-amber-500" /> Generated Actions ({actions.length})
          </h2>
          <div className="grid gap-4">
            {actions.map((act, i) => (
              <div key={i} className="bg-white border rounded-xl overflow-hidden shadow-sm">
                <div className="bg-slate-50 border-b px-4 py-2 flex justify-between text-xs text-slate-500">
                  <span>Trigger: {act.trigger_id}</span>
                  <span>Conv: {act.conversation_id}</span>
                </div>
                <div className="p-4 grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <div className="text-xs text-slate-400 mb-1">Message Body</div>
                    <div className="bg-green-50 text-green-900 p-3 rounded-lg border border-green-100 whitespace-pre-wrap font-medium">
                      {act.body}
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div>
                      <div className="text-xs text-slate-400">CTA</div>
                      <div className="font-medium text-sm">{act.cta}</div>
                    </div>
                    <div>
                      <div className="text-xs text-slate-400">Rationale</div>
                      <div className="text-sm italic text-slate-600">{act.rationale}</div>
                    </div>
                    <div className="flex gap-4">
                      <div>
                        <div className="text-xs text-slate-400">Send As</div>
                        <div className="text-sm bg-slate-100 px-2 rounded">{act.send_as}</div>
                      </div>
                      <div>
                        <div className="text-xs text-slate-400">Merchant ID</div>
                        <div className="text-sm">{act.merchant_id}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {rawResponse && (
        <div className="mt-6 bg-slate-900 rounded-xl overflow-hidden">
          <div className="flex justify-between items-center px-4 py-2 bg-slate-800 border-b border-slate-700">
            <span className="text-slate-300 text-sm font-mono">Raw Response JSON</span>
            <button 
              onClick={() => navigator.clipboard.writeText(JSON.stringify(rawResponse, null, 2))}
              className="text-slate-400 hover:text-white"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
          <pre className="p-4 text-xs text-green-400 overflow-auto max-h-96">
            {JSON.stringify(rawResponse, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
