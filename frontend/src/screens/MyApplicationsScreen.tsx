import React, { useState } from 'react';
import { useApp } from '../context/AppContext';

export const MyApplicationsScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [tab, setTab] = useState('applications');

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4">
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">My applications</h1>
      </div>
      <div className="px-4 mt-3 flex gap-2">
        <button onClick={() => setTab('applications')} className={`px-3 py-1.5 rounded-full text-xs font-bold ${tab === 'applications' ? 'bg-[#4F6B52] text-white' : 'bg-white border border-[#EBDDE2] text-[#5E6B60]'}`}>Applications</button>
        <button onClick={() => setTab('invitations')} className={`px-3 py-1.5 rounded-full text-xs font-bold ${tab === 'invitations' ? 'bg-[#4F6B52] text-white' : 'bg-white border border-[#EBDDE2] text-[#5E6B60]'}`}>Invitations 2</button>
      </div>
      <div className="flex-1 px-4 mt-3 space-y-3 overflow-y-auto">
        {tab === 'applications' && (
          <>
            <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-bold text-[#2B3A2E]">Team Golt</p>
                  <p className="text-[11px] text-[#5E6B60]">ShipIt Sprint 2026</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-[10px] font-bold">Under review</span>
              </div>
              <p className="text-xs text-[#2B3A2E]"><strong>Role applied:</strong> Frontend Developer</p>
              <button className="text-[11px] text-[#5E6B60] font-semibold">Withdraw</button>
            </div>
            <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 space-y-2">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm font-bold text-[#2B3A2E]">Team Nova</p>
                  <p className="text-[11px] text-[#5E6B60]">ShipIt Sprint 2026</p>
                </div>
                <span className="px-2 py-0.5 rounded-full bg-[#F6E2E9] text-[#2B3A2E] text-[10px] font-bold">Interested</span>
              </div>
            </div>
          </>
        )}
        {tab === 'invitations' && (
          <div className="bg-[#E3EDDF] rounded-[18px] border border-[#EBDDE2] p-4 space-y-3">
            <p className="text-sm font-bold text-[#2B3A2E]">Team Nova invited you</p>
            <p className="text-[11px] text-[#5E6B60]">Frontend Developer · ShipIt Sprint 2026</p>
            <p className="text-[11px] text-[#5E6B60]">Accepting means you are willing to join. The leader makes the final selection.</p>
            <div className="flex gap-2">
              <button className="flex-1 py-2 rounded-[12px] border border-[#EBDDE2] bg-white text-xs font-bold text-[#5E6B60]">Decline</button>
              <button className="flex-1 py-2 rounded-[12px] bg-[#4F6B52] text-white text-xs font-bold">Accept</button>
            </div>
          </div>
        )}
      </div>
      <div className="pb-6 text-center">
        <button onClick={() => setCurrentScreen('discover')} className="text-xs text-[#5E6B60] font-semibold">Back</button>
      </div>
    </div>
  );
};