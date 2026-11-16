import React from 'react';
import { useApp } from '../context/AppContext';
import { ArrowLeft, FileText, CheckCircle2 } from 'lucide-react';

export const ResumeReviewScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4 flex items-center justify-between">
        <button onClick={() => setCurrentScreen('profile')} className="w-[38px] h-[38px] rounded-[10px] border border-[#EBDDE2] bg-white flex items-center justify-center text-[#2B3A2E]">‹</button>
        <span className="text-[12px] font-bold text-[#5E6B60] bg-[#E3EDDF] px-2 py-1 rounded-full">Step 2 of 3</span>
      </div>
      <div className="h-1.5 mx-4 mt-3 bg-[#E3EDDF] rounded-full overflow-hidden">
        <div className="h-full w-2/3 bg-[#4F6B52] rounded-full" />
      </div>
      <div className="flex-1 px-4 pt-4 space-y-3 overflow-y-auto">
        <div className="bg-[#E3EDDF] rounded-[18px] p-3 flex items-center gap-3 border border-[#EBDDE2]">
          <div className="w-10 h-10 rounded-[10px] bg-white flex items-center justify-center"><FileText className="w-5 h-5 text-[#4F6B52]" /></div>
          <div className="flex-1">
            <p className="text-xs font-bold text-[#2B3A2E]">resume.pdf</p>
            <p className="text-[10px] text-[#5E6B60]">Parsed · 2 fields need checking</p>
          </div>
        </div>
        <p className="text-[11px] text-[#5E6B60]">AI-extracted details are a draft. Please confirm or edit.</p>
        <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 space-y-2">
          <p className="text-[11px] font-bold text-[#5E6B60] uppercase">Name & Summary</p>
          <p className="text-sm font-bold text-[#2B3A2E]">Alex Rivera</p>
          <p className="text-xs text-[#5E6B60]">Full-stack developer with React & FastAPI experience.</p>
        </div>
        <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 space-y-2">
          <p className="text-[11px] font-bold text-[#5E6B60] uppercase">Skills</p>
          <div className="flex flex-wrap gap-1.5">
            <span className="px-3 py-1 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-xs font-bold">React</span>
            <span className="px-3 py-1 rounded-full bg-[#F6E2E9] text-[#2B3A2E] text-xs font-bold">Check: React?</span>
            <span className="px-3 py-1 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-xs font-bold">FastAPI</span>
          </div>
        </div>
        <div className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 space-y-2">
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded-full bg-[#F6E2E9] text-[#2B3A2E] text-[10px] font-bold">Needs review</span>
            <p className="text-xs font-bold text-[#2B3A2E]">ShipIt Dashboard</p>
          </div>
          <p className="text-[11px] text-[#5E6B60]">React, Tailwind, FastAPI</p>
        </div>
      </div>
      <div className="px-4 pb-6 pt-3 space-y-2">
        <button onClick={() => setCurrentScreen('profile')} className="w-full py-3 rounded-[14px] bg-[#4F6B52] text-white font-bold text-xs">Confirm details</button>
        <button className="w-full py-3 rounded-[14px] border border-[#84A282] text-[#2B3A2E] font-bold text-xs bg-white">Re-upload resume</button>
      </div>
    </div>
  );
};