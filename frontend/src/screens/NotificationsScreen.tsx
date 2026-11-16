import React from 'react';
import { useApp } from '../context/AppContext';
import { ArrowLeft } from 'lucide-react';

export const NotificationsScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4 flex items-center justify-between">
        <button onClick={() => setCurrentScreen('home')} className="w-[38px] h-[38px] rounded-[10px] border border-[#EBDDE2] bg-white flex items-center justify-center text-[#2B3A2E]">‹</button>
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">Notifications</h1>
        <button className="text-xs font-bold text-[#4F6B52]">Mark all read</button>
      </div>
      <div className="flex-1 px-4 mt-4 space-y-4 overflow-y-auto">
        <p className="text-[11px] font-bold text-[#5E6B60] uppercase">Today</p>
        {[
          { title: 'Team Golt showed interest in you', time: '2m ago', img: 'https://i.pravatar.cc/40?img=12' },
          { title: 'Arjun accepted your invitation', time: '1h ago', img: 'https://i.pravatar.cc/40?img=22' },
          { title: 'ShipIt Sprint deadline in 3 days', time: '3h ago', img: null },
        ].map((n, i) => (
          <div key={i} className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 flex items-center gap-3">
            {n.img ? <img src={n.img} className="w-9 h-9 rounded-full object-cover" alt="" /> : <div className="w-9 h-9 rounded-full bg-[#E3EDDF] flex items-center justify-center text-[#4F6B52]">⏰</div>}
            <div className="flex-1">
              <p className="text-xs font-bold text-[#2B3A2E]">{n.title}</p>
              <p className="text-[10px] text-[#5E6B60]">{n.time}</p>
            </div>
          </div>
        ))}
        <p className="text-[11px] font-bold text-[#5E6B60] uppercase">Earlier</p>
        {[
          { title: 'Your request is under review', time: '1d ago' },
          { title: 'Profile ready for matching', time: '2d ago' },
        ].map((n, i) => (
          <div key={i} className="bg-white rounded-[18px] border border-[#EBDDE2] p-3 flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-[#E3EDDF] flex items-center justify-center text-[#4F6B52]">✓</div>
            <div className="flex-1">
              <p className="text-xs font-bold text-[#2B3A2E]">{n.title}</p>
              <p className="text-[10px] text-[#5E6B60]">{n.time}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};