import React from 'react';
import { BookOpen, Server, Code, Play } from 'lucide-react';

export default function Help() {
  return (
    <div className="max-w-4xl space-y-8">
      <h1 className="text-3xl font-bold text-slate-800">Deployment & Help</h1>
      
      <div className="bg-white p-6 rounded-xl border shadow-sm">
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4 border-b pb-2"><BookOpen className="text-primary" /> Challenge Endpoints</h2>
        <p className="text-slate-600 mb-4 text-sm">
          This system is fully compliant with the Magicpin Vera Challenge. The core endpoints expected by the judge simulator are live at:
        </p>
        <ul className="list-disc list-inside space-y-2 text-sm font-mono text-slate-700 bg-slate-50 p-4 rounded border">
          <li>GET  /v1/healthz</li>
          <li>GET  /v1/metadata</li>
          <li>POST /v1/context</li>
          <li>POST /v1/tick</li>
          <li>POST /v1/reply</li>
        </ul>
      </div>

      <div className="bg-white p-6 rounded-xl border shadow-sm">
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4 border-b pb-2"><Play className="text-emerald-500" /> How to Test</h2>
        <div className="space-y-4 text-sm text-slate-600">
          <p>
            <strong>1. Context Manager:</strong> Push arbitrary context to the server. The server stores it in-memory. If the version is older than current, it correctly returns a 409 conflict.
          </p>
          <p>
            <strong>2. Tick Simulator:</strong> Triggers the core message composition engine. It looks up the triggers, fetches matching merchants/categories, applies the appropriate strategy logic, and generates a tailored message.
          </p>
          <p>
            <strong>3. Reply Simulator:</strong> Simulates a merchant or customer replying. It runs intent classification to identify positive/negative signals or WhatsApp auto-replies to decide whether to wait, end, or continue sending.
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border shadow-sm">
        <h2 className="text-xl font-bold flex items-center gap-2 mb-4 border-b pb-2"><Server className="text-indigo-500" /> Deployment Architecture</h2>
        <p className="text-slate-600 mb-4 text-sm">
          The app uses a unified FastAPI backend that serves the `/v1` JSON endpoints for the judge and static files for this React frontend.
        </p>
        <div className="bg-slate-900 text-green-400 p-4 rounded font-mono text-sm overflow-auto">
          # Start Backend<br/>
          pip install -r requirements.txt<br/>
          uvicorn main:app --host 0.0.0.0 --port 8080<br/>
          <br/>
          # Build Frontend<br/>
          cd frontend<br/>
          npm install<br/>
          npm run build<br/>
        </div>
      </div>
    </div>
  );
}
