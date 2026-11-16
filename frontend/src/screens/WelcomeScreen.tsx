import React from 'react';
import { useApp } from '../context/AppContext';
import { ArrowRight } from 'lucide-react';

export const WelcomeScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="h-[430px] bg-[#F6E2E9] relative overflow-hidden">
        <div className="absolute top-6 left-6 text-xl font-black text-[#2B3A2E]">HackMate</div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-44 h-44 rounded-full bg-[#B8CFB3] flex items-center justify-center relative">
            <div className="absolute -top-4 -left-6 w-20 h-20 rounded-full bg-white/80 border-4 border-[#FEFAF3] overflow-hidden">
              <img src="https://i.pravatar.cc/100?img=1" alt="" className="w-full h-full object-cover" />
            </div>
            <div className="absolute top-2 right-2 w-14 h-14 rounded-full bg-white/80 border-4 border-[#FEFAF3] overflow-hidden">
              <img src="https://i.pravatar.cc/100?img=2" alt="" className="w-full h-full object-cover" />
            </div>
            <div className="absolute bottom-2 left-10 w-12 h-12 rounded-full bg-white/80 border-4 border-[#FEFAF3] overflow-hidden">
              <img src="https://i.pravatar.cc/100?img=3" alt="" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </div>
      <div className="flex-1 px-6 pt-8 pb-6 flex flex-col">
        <h1 className="text-[28px] font-bold text-[#2B3A2E] leading-tight">Find your hackathon. Build your team.</h1>
        <p className="text-sm text-[#5E6B60] mt-2">Discover events and match teammates by skills, experience and availability.</p>
        <div className="mt-auto space-y-3">
          <button
            onClick={() => setCurrentScreen('signup')}
            className="w-full py-3.5 rounded-[14px] bg-[#4F6B52] text-white font-bold text-sm flex items-center justify-center gap-2"
          >
            Get started <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => setCurrentScreen('signin' as any)}
            className="w-full text-sm text-[#5E6B60] font-semibold"
          >
            Already have an account? <span className="text-[#4F6B52] underline">Sign in</span>
          </button>
        </div>
      </div>
    </div>
  );
};