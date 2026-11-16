import React from 'react';
import { useApp } from '../../context/AppContext';
import { Wifi, BatteryMedium, Signal, Sparkles } from 'lucide-react';

interface DeviceFrameProps {
  children: React.ReactNode;
}

export const DeviceFrame: React.FC<DeviceFrameProps> = ({ children }) => {
  const { isMobileFrame } = useApp();

  if (!isMobileFrame) {
    // Fullscreen responsive view
    return (
      <div className="min-h-screen bg-bubble-cream text-bubble-ink flex flex-col max-w-5xl mx-auto border-x border-bubble-cream-border/60 shadow-sm">
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-900/90 py-4 px-2 sm:px-4 flex flex-col items-center justify-center">
      {/* Device frame presentation banner on desktop */}
      <div className="mb-3 text-center hidden md:flex items-center gap-2 text-xs font-medium text-stone-300 bg-stone-800/80 px-4 py-1.5 rounded-full border border-stone-700/60 backdrop-blur-sm">
        <Sparkles className="w-3.5 h-3.5 text-bubble-sage" />
        <span>Mobile-First Preview — Behance ShipIt Layouts & Swipe Mechanics</span>
      </div>

      {/* The Phone Bezel */}
      <div className="relative w-full max-w-[420px] h-[880px] max-h-[96vh] bg-[#2B3A2E] rounded-[44px] p-[8px] shadow-2xl ring-1 ring-stone-700/50 flex flex-col overflow-hidden">
        {/* Dynamic Island / Speaker Notch */}
        <div className="absolute top-4 left-1/2 -translate-x-1/2 w-28 h-5 bg-stone-950 rounded-full z-40 flex items-center justify-end px-3">
          <div className="w-2.5 h-2.5 rounded-full bg-stone-900 border border-stone-800"></div>
        </div>

        {/* Status Bar */}
        <div className="w-full bg-bubble-cream px-6 pt-2 pb-1 flex items-center justify-between text-xs font-bold text-bubble-ink z-30 select-none">
          <span>9:41</span>
          <div className="flex items-center gap-1.5 opacity-80">
            <Signal className="w-3.5 h-3.5" />
            <Wifi className="w-3.5 h-3.5" />
            <BatteryMedium className="w-4 h-4" />
          </div>
        </div>

        {/* Screen Content */}
        <div className="flex-1 bg-[#FEFAF3] overflow-y-auto overflow-x-hidden relative flex flex-col rounded-b-[36px] no-overscroll">
          {children}
        </div>
      </div>
    </div>
  );
};
