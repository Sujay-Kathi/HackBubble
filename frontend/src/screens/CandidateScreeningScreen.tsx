import React, { useState, useRef } from 'react';
import { useApp } from '../context/AppContext';
import { SlidersHorizontal } from 'lucide-react';

const CANDS = [
  { id: 'c1', name: 'Arjun Mehta, 21', role: 'Frontend Developer · Strong match', skills: ['Flutter', 'Dart', 'Figma', 'Firebase'], desc: 'Built a campus event app used by 2k students. Won 2nd at HackX. Available 15 hrs/week. Strong Figma-to-code. Gap: no React yet.', img: 'https://i.pravatar.cc/400?img=22' },
];

export const CandidateScreeningScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [index, setIndex] = useState(0);
  const [drag, setDrag] = useState({ x: 0, y: 0, active: false });
  const start = useRef<{ x: number; y: number } | null>(null);
  const onDown = (e: React.PointerEvent) => { start.current = { x: e.clientX, y: e.clientY }; setDrag(d => ({ ...d, active: true })); };
  const onMove = (e: React.PointerEvent) => { if (!start.current) return; setDrag({ x: e.clientX - start.current.x, y: e.clientY - start.current.y, active: true }); };
  const onUp = () => { if (Math.abs(drag.x) > 120) setIndex(i => i + 1); setDrag({ x: 0, y: 0, active: false }); start.current = null; };
  const c = CANDS[index % CANDS.length];

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4 flex items-center justify-between">
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">Frontend Developer</h1>
        <button className="w-[38px] h-[38px] rounded-[10px] border border-[#EBDDE2] bg-white flex items-center justify-center text-[#2B3A2E]">
          <SlidersHorizontal className="w-4 h-4" />
        </button>
      </div>
      <p className="px-4 text-[11px] text-[#5E6B60] mt-1">Swipe a card to review · 4 candidates left</p>
      <div className="flex-1 relative px-4 pt-4">
        <div className="absolute inset-x-8 top-8 h-[70%] rounded-[30px] border-[6px] border-black bg-[#F6E2E9] rotate-[-4deg]" />
        <div className="absolute inset-x-8 top-8 h-[70%] rounded-[30px] border-[6px] border-black bg-[#E3EDDF] rotate-[3deg]" />
        <div
          onPointerDown={onDown} onPointerMove={onMove} onPointerUp={onUp} onPointerLeave={onUp}
          className="absolute inset-x-4 top-4 h-[78%] rounded-[30px] border-[6px] border-black bg-white overflow-hidden shadow-2xl cursor-grab select-none"
          style={{ transform: `translate(${drag.x}px, ${drag.y}px) rotate(${drag.x / 20}deg)`, transition: drag.active ? 'none' : 'transform 0.3s' }}
        >
          <div className="relative h-[61%]">
            <img src={c.img} alt="" className="w-full h-full object-cover" />
          </div>
          <div className="p-4 space-y-2">
            <h2 className="text-[30px] font-bold text-[#2B3A2E] leading-none">{c.name}</h2>
            <p className="text-[15px] text-[#5E6B60]">{c.role}</p>
            <div className="flex flex-wrap gap-1.5">
              {c.skills.map(s => <span key={s} className="px-2.5 py-1 rounded-full bg-[#E3EDDF] text-[#4F6B52] text-[11px] font-bold">{s}</span>)}
            </div>
            <p className="text-[15px] text-[#2B3A2E] leading-snug">{c.desc}</p>
          </div>
        </div>
      </div>
      <div className="pb-6 text-center">
        <button onClick={() => setCurrentScreen('my-teams')} className="text-xs text-[#5E6B60] font-semibold">Back</button>
      </div>
    </div>
  );
};