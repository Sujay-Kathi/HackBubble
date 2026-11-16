import React from 'react';
import { useApp } from '../context/AppContext';
import { ArrowLeft } from 'lucide-react';

export const HackathonDetailScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="h-[180px] bg-[#F6E2E9] relative px-4 pt-4">
        <button onClick={() => setCurrentScreen('discover')} className="w-[38px] h-[38px] rounded-[10px] bg-white/80 flex items-center justify-center text-[#2B3A2E]">‹</button>
        <h1 className="mt-6 text-[24px] font-bold text-[#2B3A2E]">ShipIt Sprint 2026</h1>
      </div>
      <div className="px-4 -mt-4 space-y-3">
        <div className="flex flex-wrap gap-1.5">
          {['Online', 'Registration open', 'UX/UI', 'Mobile'].map(t => (
            <span key={t} className="px-2.5 py-1 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-[11px] font-bold">{t}</span>
          ))}
        </div>
        <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-4 space-y-2">
          <div className="flex justify-between text-xs"><span className="text-[#5E6B60]">Dates</span><span className="font-bold text-[#2B3A2E]">12–14 Dec 2026</span></div>
          <div className="flex justify-between text-xs"><span className="text-[#5E6B60]">Deadline</span><span className="font-bold text-[#2B3A2E]">10 Dec 2026</span></div>
          <div className="flex justify-between text-xs"><span className="text-[#5E6B60]">Team size</span><span className="font-bold text-[#2B3A2E]">2-4 Members</span></div>
          <div className="flex justify-between text-xs"><span className="text-[#5E6B60]">Prizes</span><span className="font-bold text-[#2B3A2E]">$25,000</span></div>
        </div>
        <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-4">
          <p className="text-[11px] font-bold text-[#5E6B60] uppercase mb-1">About</p>
          <p className="text-xs text-[#2B3A2E] leading-relaxed">A global 48-hour builder sprint focused on shipping full-stack apps, AI agents, and product design prototypes.</p>
        </div>
        <div className="bg-[#E3EDDF] rounded-[18px] border border-[#EBDDE2] p-3 text-[11px] text-[#5E6B60]">
          Source: Devpost, last verified 2 hours ago
        </div>
      </div>
      <div className="px-4 pb-6 pt-4 space-y-2">
        <button onClick={() => setCurrentScreen('create')} className="w-full py-3 rounded-[14px] bg-[#4F6B52] text-white font-bold text-xs">Create a team</button>
        <div className="flex gap-2">
          <button onClick={() => setCurrentScreen('join-team')} className="flex-1 py-3 rounded-[14px] border border-[#84A282] bg-white text-[#2B3A2E] font-bold text-xs">Join a team</button>
          <button className="flex-1 py-3 rounded-[14px] border border-[#84A282] bg-white text-[#2B3A2E] font-bold text-xs">Register on source</button>
        </div>
      </div>
    </div>
  );
};