import React, { useState } from 'react';
import api from '../api';
import { Send, CheckCircle, XCircle } from 'lucide-react';

export default function ContextManager() {
  const [scope, setScope] = useState('category');
  const [contextId, setContextId] = useState('demo_123');
  const [version, setVersion] = useState(1);
  const [payloadStr, setPayloadStr] = useState('{\n  "name": "Demo Category"\n}');
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setResponse(null);
    setError(null);
    
    try {
      const parsedPayload = JSON.parse(payloadStr);
      const reqBody = {
        scope,
        context_id: contextId,
        version: Number(version),
        payload: parsedPayload,
        delivered_at: new Date().toISOString()
      };
      
      const res = await api.post('/v1/context', reqBody);
      setResponse(res.data);
    } catch (err) {
      if (err.name === 'SyntaxError') {
        setError('Invalid JSON payload');
      } else if (err.response) {
        setError(err.response.data.detail || JSON.stringify(err.response.data));
        if (err.response.status === 409) {
            setResponse(err.response.data);
        }
      } else {
        setError(err.message);
      }
    }
    setLoading(false);
  };

  const loadSample = (type) => {
    setScope(type);
    setContextId(`sample_${type}_001`);
    setVersion(1);
    const samples = {
      category: { slug: "sample_category", tone: "friendly" },
      merchant: { merchant_id: "m_001", identity: { name: "Sample Store" } },
      customer: { customer_id: "c_001", name: "John Doe" },
      trigger: { trigger_id: "t_001", kind: "dormant_with_vera" }
    };
    setPayloadStr(JSON.stringify(samples[type], null, 2));
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold text-slate-800 mb-6">Context Manager</h1>
      
      <div className="bg-white p-6 rounded-xl border shadow-sm">
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Scope</label>
            <select 
              value={scope} 
              onChange={e => setScope(e.target.value)}
              className="w-full border rounded-md p-2 bg-slate-50 focus:ring-2 ring-primary outline-none"
            >
              <option value="category">Category</option>
              <option value="merchant">Merchant</option>
              <option value="customer">Customer</option>
              <option value="trigger">Trigger</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Context ID</label>
            <input 
              type="text" 
              value={contextId} 
              onChange={e => setContextId(e.target.value)}
              className="w-full border rounded-md p-2 bg-slate-50 focus:ring-2 ring-primary outline-none"
            />
          </div>
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1">Version</label>
          <input 
            type="number" 
            value={version} 
            onChange={e => setVersion(e.target.value)}
            className="w-full border rounded-md p-2 bg-slate-50 focus:ring-2 ring-primary outline-none max-w-[200px]"
          />
        </div>
        
        <div className="mb-4">
          <label className="block text-sm font-medium text-slate-700 mb-1 flex justify-between">
            <span>Payload (JSON)</span>
            <div className="space-x-2 text-xs">
              <button onClick={() => loadSample('category')} className="text-primary hover:underline">Sample Category</button>
              <button onClick={() => loadSample('merchant')} className="text-primary hover:underline">Sample Merchant</button>
              <button onClick={() => loadSample('trigger')} className="text-primary hover:underline">Sample Trigger</button>
            </div>
          </label>
          <textarea 
            value={payloadStr}
            onChange={e => setPayloadStr(e.target.value)}
            className="w-full h-48 border rounded-md p-3 font-mono text-sm bg-slate-800 text-green-400 focus:ring-2 ring-primary outline-none"
          />
        </div>

        <button 
          onClick={handleSubmit} 
          disabled={loading}
          className="flex items-center gap-2 bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? <span className="animate-pulse">Sending...</span> : <><Send className="w-4 h-4" /> Submit Context</>}
        </button>
      </div>

      {(response || error) && (
        <div className={`mt-6 p-4 rounded-xl border ${error ? 'bg-red-50 border-red-200' : 'bg-emerald-50 border-emerald-200'}`}>
          <div className="flex items-center gap-2 mb-2 font-bold">
            {error ? <XCircle className="text-red-500" /> : <CheckCircle className="text-emerald-500" />}
            {error ? 'Error' : 'Response'}
          </div>
          <pre className="text-xs overflow-auto bg-white/50 p-4 rounded border">
            {error ? String(error) : JSON.stringify(response, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
