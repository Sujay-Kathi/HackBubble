import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { Check } from 'lucide-react';

export const ShortlistFinalizeScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [tab, setTab] = useState('accepted');
  const [selected, setSelected] = useState(['a', 'b']);
  const toggle = (id: string) => setSelected(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4 flex items-center justify-between">
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">Finalize team</h1>
      </div>
      <div className="px-4 mt-3 flex gap-2">
        {['Invited 2', 'Accepted 3', 'Declined 1'].map(t => (
          <button key={t} onClick={() => setTab(t.split(' ')[0].toLowerCase())}
            className={`px-3 py-1.5 rounded-full text-xs font-bold ${tab === t.split(' ')[0].toLowerCase() ? 'bg-[#4F6B52] text-white' : 'bg-white border border-[#EBDDE2] text-[#5E6B60]'}`}>
            {t}
          </button>
        ))}
      </div>
      <p className="px-4 mt-2 text-[11px] text-[#5E6B60]">Accepted means willing to join. Select who becomes a member (2 spots left).</p>
      <div className="flex-1 px-4 mt-3 space-y-2 overflow-y-auto">
        {[
          { id: 'a', name: 'Arjun Mehta', role: 'Frontend Developer', checked: true },
          { id: 'b', name: 'Sara Lin', role: 'Designer', checked: true },
          { id: 'c', name: 'Dev Patel', role: 'ML Engineer', checked: false },
        ].map(c => (
          <div key={c.id} className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 flex items-center gap-3">
            <button onClick={() => toggle(c.id)} className={`w-5 h-5 rounded-[6px] border-2 flex items-center justify-center ${selected.includes(c.id) ? 'bg-[#4F6B52] border-[#4F6B52]' : 'border-[#EBDDE2]'}`}>
              {selected.includes(c.id) && <Check className="w-3 h-3 text-white" />}
            </button>
            <img src={`https://i.pravatar.cc/40?img=${c.id === 'a' ? 22 : c.id === 'b' ? 25 : 30}`} className="w-10 h-10 rounded-[12px] object-cover" alt="" />
            <div className="flex-1">
              <p className="text-xs font-bold text-[#2B3A2E]">{c.name}</p>
              <p className="text-[10px] text-[#5E6B60]">{c.role}</p>
            </div>
            {c.id === 'c' && <span className="px-2 py-0.5 rounded-full bg-[#F6E2E9] text-[#2B3A2E] text-[10px] font-bold">Invited · Waiting</span>}
          </div>
        ))}
        <div className="bg-[#E3EDDF] rounded-[18px] p-3 text-[11px] text-[#5E6B60]">
          Finalizing notifies selected candidates and updates My Teams.
        </div>
      </div>
      <div className="px-4 pb-6 pt-3">
        <button onClick={() => setCurrentScreen('my-teams')} className="w-full py-3 rounded-[14px] bg-[#4F6B52] text-white font-bold text-xs">
          Finalize team ({selected.length} selected)
        </button>
      </div>
    </div>
  );
};