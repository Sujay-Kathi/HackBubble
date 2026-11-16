import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { ShieldCheck } from 'lucide-react';

export const VerifyCodeScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [otp, setOtp] = useState(['4', '2', '8', '', '', '']);

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col items-center justify-center px-6">
      <div className="w-12 h-12 rounded-2xl bg-[#E3EDDF] text-[#4F6B52] flex items-center justify-center mb-4">
        <ShieldCheck className="w-6 h-6" />
      </div>
      <h1 className="text-[20px] font-bold text-[#2B3A2E]">Verify code</h1>
      <p className="text-xs text-[#5E6B60] mt-1 text-center max-w-[240px]">
        Enter the 6-digit code we sent to <span className="font-semibold text-[#2B3A2E]">you@email.com</span>
      </p>
      <div className="flex gap-2 mt-6">
        {otp.map((d, i) => (
          <input key={i} maxLength={1} value={d}
            onChange={e => { const n = [...otp]; n[i] = e.target.value; setOtp(n); }}
            className="w-10 h-12 rounded-[12px] border-2 border-[#EBDDE2] bg-white text-center font-bold text-base text-[#2B3A2E] focus:border-[#4F6B52] outline-none" />
        ))}
      </div>
      <div className="w-full mt-6 space-y-3">
        <button onClick={() => setCurrentScreen('home')} className="w-full py-3 rounded-[14px] bg-[#4F6B52] text-white font-bold text-xs">
          Continue
        </button>
        <p className="text-xs text-[#5E6B60] text-center">
          Didn't get a code? <button className="text-[#4F6B52] font-bold">Resend</button>
        </p>
        <button onClick={() => setCurrentScreen('welcome')} className="text-[11px] text-stone-400 block mx-auto">Back to sign in</button>
      </div>
    </div>
  );
};