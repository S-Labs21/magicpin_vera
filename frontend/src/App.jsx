import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Database, PlayCircle, MessageSquare, Info, Server } from 'lucide-react';

import Overview from './pages/Overview';
import ContextManager from './pages/ContextManager';
import TickSimulator from './pages/TickSimulator';
import ReplySimulator from './pages/ReplySimulator';
import Help from './pages/Help';

function Sidebar() {
  const location = useLocation();
  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Overview' },
    { path: '/context', icon: Database, label: 'Context Manager' },
    { path: '/tick', icon: PlayCircle, label: 'Tick Simulator' },
    { path: '/reply', icon: MessageSquare, label: 'Reply Simulator' },
    { path: '/help', icon: Info, label: 'Deployment & Help' }
  ];

  return (
    <div className="w-64 bg-white border-r h-screen fixed top-0 left-0 flex flex-col">
      <div className="p-6 border-b flex items-center gap-3">
        <Server className="w-6 h-6 text-primary" />
        <h1 className="font-bold text-xl tracking-tight text-slate-800">Vera Dashboard</h1>
      </div>
      <nav className="flex-1 p-4 space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
              location.pathname === item.path
                ? 'bg-primary/10 text-primary font-medium'
                : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </Link>
        ))}
      </nav>
      <div className="p-4 border-t text-xs text-slate-500">
        <p>Magicpin AI Challenge</p>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 ml-64 p-8 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/dashboard" element={<Overview />} />
            <Route path="/context" element={<ContextManager />} />
            <Route path="/tick" element={<TickSimulator />} />
            <Route path="/reply" element={<ReplySimulator />} />
            <Route path="/help" element={<Help />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
