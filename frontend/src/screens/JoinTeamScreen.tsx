import React, { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { SlidersHorizontal } from 'lucide-react';

const TEAMS = [
  { id: 't1', name: 'Team Golt', hackathon: 'ShipIt Sprint 2026', leader: 'Kenji Sato', roles: ['Frontend × 1', 'Designer × 1', 'ML × 1'], desc: 'Building a tool to help students find hackathons and form teams. Beginner-friendly, 10-15 hrs/week, weekly sync on Discord.', img: 'https://i.pravatar.cc/400?img=12' },
  { id: 't2', name: 'Team Nova', hackathon: 'ShipIt Sprint 2026', leader: 'Priya Shah', roles: ['Backend × 1'], desc: 'AI-powered resume parser for faster hiring. Experienced members preferred.', img: 'https://i.pravatar.cc/400?img=15' },
];

export const JoinTeamScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [index, setIndex] = useState(0);
  const [drag, setDrag] = useState({ x: 0, y: 0, active: false });
  const start = useRef<{ x: number; y: number } | null>(null);

  const onPointerDown = (e: React.PointerEvent) => { start.current = { x: e.clientX, y: e.clientY }; setDrag(d => ({ ...d, active: true })); };
  const onPointerMove = (e: React.PointerEvent) => {
    if (!start.current) return;
    setDrag({ x: e.clientX - start.current.x, y: e.clientY - start.current.y, active: true });
  };
  const onPointerUp = () => {
    if (Math.abs(drag.x) > 120) {
      setIndex(i => i + 1);
    }
    setDrag({ x: 0, y: 0, active: false });
    start.current = null;
  };

  const team = TEAMS[index % TEAMS.length];

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4 flex items-center justify-between">
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">Join a team</h1>
        <button className="w-[38px] h-[38px] rounded-[10px] border border-[#EBDDE2] bg-white flex items-center justify-center text-[#2B3A2E]">
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </div>
      <div className="px-4 mt-2">
        <button className="w-full text-left px-3 py-2 rounded-[12px] border border-[#EBDDE2] bg-white text-xs font-semibold text-[#2B3A2E]">
          ShipIt Sprint 2026 ⌄
        </button>
        <p className="text-[11px] text-[#5E6B60] mt-2">Swipe right to request a role · left to skip</p>
      </div>
      <div className="flex-1 relative px-4 pt-4">
        {/* back cards */}
        <div className="absolute inset-x-8 top-8 h-[70%] rounded-[30px] border-[6px] border-black bg-[#F6E2E9] rotate-[-4deg] opacity-90" />
        <div className="absolute inset-x-8 top-8 h-[70%] rounded-[30px] border-[6px] border-black bg-[#E3EDDF] rotate-[3deg] opacity-90" />
        {/* front card */}
        <div
          onPointerDown={onPointerDown}
          onPointerMove={onPointerMove}
          onPointerUp={onPointerUp}
          onPointerLeave={onPointerUp}
          className="absolute inset-x-4 top-4 h-[78%] rounded-[30px] border-[6px] border-black bg-white overflow-hidden shadow-2xl cursor-grab select-none"
          style={{ transform: `translate(${drag.x}px, ${drag.y}px) rotate(${drag.x / 20}deg)`, transition: drag.active ? 'none' : 'transform 0.3s' }}
        >
          <div className="relative h-[61%]">
            <img src={team.img} alt="" className="w-full h-full object-cover" />
            <div className="absolute top-3 left-3 px-2 py-1 rounded-full bg-white/90 text-[10px] font-bold text-[#2B3A2E]">Online · 12–14 Dec</div>
            <div className="absolute top-3 right-3 flex -space-x-2">
              <img src="https://i.pravatar.cc/40?img=4" className="w-7 h-7 rounded-full border-2 border-white" alt="" />
              <img src="https://i.pravatar.cc/40?img=5" className="w-7 h-7 rounded-full border-2 border-white" alt="" />
            </div>
            <div className="absolute bottom-0 left-0 right-0 h-12 bg-gradient-to-t from-white to-transparent" />
          </div>
          <div className="p-4 space-y-2">
            <h2 className="text-[30px] font-bold text-[#2B3A2E] leading-none">{team.name}</h2>
            <p className="text-[15px] text-[#5E6B60]">{team.hackathon} · Led by {team.leader}</p>
            <div className="flex flex-wrap gap-1.5">
              {team.roles.map(r => <span key={r} className="px-2.5 py-1 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-[11px] font-bold">{r}</span>)}
            </div>
            <p className="text-[15px] text-[#2B3A2E] leading-snug">{team.desc}</p>
          </div>
        </div>
      </div>
      <div className="pb-6 text-center">
        <button onClick={() => setCurrentScreen('discover')} className="text-xs text-[#5E6B60] font-semibold">Back</button>
      </div>
    </div>
  );
};