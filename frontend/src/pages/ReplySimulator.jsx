import React, { useState } from 'react';
import api from '../api';
import { MessageSquare, User, Bot, AlertTriangle } from 'lucide-react';

export default function ReplySimulator() {
  const [conversationId, setConversationId] = useState('conv_123');
  const [merchantId, setMerchantId] = useState('m_001');
  const [role, setRole] = useState('merchant');
  const [message, setMessage] = useState('Yes, sounds good');
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    try {
      const res = await api.post('/v1/reply', {
        conversation_id: conversationId,
        merchant_id: merchantId,
        from_role: role,
        message,
        received_at: new Date().toISOString(),
        turn_number: 2
      });
      setResponse(res.data);
    } catch (err) {
      console.error(err);
      setResponse({ error: err.response?.data || err.message });
    }
    setLoading(false);
  };

  const loadSample = (type) => {
    if (type === 'positive') setMessage('Yes, let us do it.');
    if (type === 'negative') setMessage('Stop messaging me.');
    if (type === 'auto') setMessage('Thank you for contacting us. We will get back to you shortly.');
    if (type === 'question') setMessage('What are the charges for this?');
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-3xl font-bold text-slate-800 mb-6">Reply Simulator</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl border shadow-sm h-fit">
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Conversation ID</label>
              <input type="text" value={conversationId} onChange={e => setConversationId(e.target.value)} className="w-full border rounded-md p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Merchant ID</label>
              <input type="text" value={merchantId} onChange={e => setMerchantId(e.target.value)} className="w-full border rounded-md p-2" />
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">From Role</label>
            <select value={role} onChange={e => setRole(e.target.value)} className="w-full border rounded-md p-2">
              <option value="merchant">Merchant</option>
              <option value="customer">Customer</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 mb-1 flex justify-between">
              Message
              <div className="space-x-2 text-xs">
                <button onClick={() => loadSample('positive')} className="text-emerald-600 hover:underline">Positive</button>
                <button onClick={() => loadSample('negative')} className="text-red-600 hover:underline">Negative</button>
                <button onClick={() => loadSample('auto')} className="text-slate-600 hover:underline">Auto-Reply</button>
              </div>
            </label>
            <textarea 
              value={message} 
              onChange={e => setMessage(e.target.value)}
              className="w-full h-24 border rounded-md p-3 focus:ring-2 ring-primary outline-none"
            />
          </div>

          <button 
            onClick={handleSend} 
            disabled={loading}
            className="w-full flex justify-center items-center gap-2 bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? 'Sending...' : 'Send Reply'}
          </button>
        </div>

        <div>
          <h3 className="font-bold text-slate-800 mb-4 flex items-center gap-2"><Bot className="w-5 h-5 text-indigo-500"/> Bot Action Decision</h3>
          
          {response ? (
            response.error ? (
              <div className="bg-red-50 text-red-700 p-4 rounded-xl border border-red-200">
                <AlertTriangle className="mb-2" />
                <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(response.error, null, 2)}</pre>
              </div>
            ) : (
              <div className="bg-white border rounded-xl shadow-sm overflow-hidden">
                <div className={`p-4 border-b flex items-center justify-between font-bold text-white uppercase ${
                  response.action === 'send' ? 'bg-emerald-500' : 
                  response.action === 'end' ? 'bg-red-500' : 'bg-amber-500'
                }`}>
                  Action: {response.action}
                  {response.action === 'wait' && <span className="text-xs normal-case opacity-90">{response.wait_seconds} seconds</span>}
                </div>
                <div className="p-4 space-y-4">
                  {response.body && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">Body</div>
                      <div className="bg-slate-50 p-3 rounded border text-sm">{response.body}</div>
                    </div>
                  )}
                  {response.cta && response.cta !== 'none' && (
                    <div>
                      <div className="text-xs text-slate-500 mb-1">CTA</div>
                      <div className="text-sm font-medium">{response.cta}</div>
                    </div>
                  )}
                  <div>
                    <div className="text-xs text-slate-500 mb-1">Rationale</div>
                    <div className="text-sm italic text-slate-600">{response.rationale}</div>
                  </div>
                </div>
              </div>
            )
          ) : (
            <div className="h-64 border-2 border-dashed border-slate-200 rounded-xl flex items-center justify-center text-slate-400">
              Send a reply to see the bot's decision
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
