import React, { useState } from 'react';
import { useApp } from '../context/AppContext';
import { ArrowLeft, Mail, Lock, User as UserIcon, Eye, EyeOff } from 'lucide-react';

export const SignupScreen: React.FC = () => {
  const { setCurrentScreen } = useApp();
  const [isSignUp, setIsSignUp] = useState(true);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [terms, setTerms] = useState(true);

  return (
    <div className="min-h-screen bg-[#FEFAF3] flex flex-col">
      <div className="px-4 pt-4">
        <button onClick={() => setCurrentScreen('welcome')} className="w-[38px] h-[38px] rounded-[10px] border border-[#EBDDE2] bg-white flex items-center justify-center text-[#2B3A2E]">‹</button>
      </div>
      <div className="flex-1 px-6 pt-4">
        <h1 className="text-[20px] font-bold text-[#2B3A2E]">{isSignUp ? "Let's begin" : "Welcome back"}</h1>
        <p className="text-xs text-[#5E6B60] mt-1">{isSignUp ? 'Create an account to save events and build teams.' : 'Sign in to manage your teams.'}</p>
        <div className="mt-6 space-y-4">
          {isSignUp && (
            <div>
              <label className="text-[11px] font-bold text-[#2B3A2E] block mb-1">Full name</label>
              <div className="relative">
                <UserIcon className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
                <input value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Oleksandr Kuzmak"
                  className="w-full pl-9 pr-3 py-2.5 rounded-[12px] border border-[#EBDDE2] bg-white text-xs text-[#2B3A2E]" />
              </div>
            </div>
          )}
          <div>
            <label className="text-[11px] font-bold text-[#2B3A2E] block mb-1">Email or phone</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
              <input value={email} onChange={e => setEmail(e.target.value)} placeholder="example@shipit.com"
                className="w-full pl-9 pr-3 py-2.5 rounded-[12px] border border-[#EBDDE2] bg-white text-xs text-[#2B3A2E]" />
            </div>
          </div>
          <div>
            <label className="text-[11px] font-bold text-[#2B3A2E] block mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
              <input type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••"
                className="w-full pl-9 pr-10 py-2.5 rounded-[12px] border border-[#EBDDE2] bg-white text-xs text-[#2B3A2E]" />
              <button onClick={() => setShowPw(!showPw)} className="absolute right-3 top-2.5 text-stone-400">
                {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            <p className="text-[10px] text-stone-400 mt-1">Include 1 digit and 1 uppercase letter.</p>
          </div>
          {isSignUp && (
            <div className="flex items-center gap-2">
              <input type="checkbox" checked={terms} onChange={e => setTerms(e.target.checked)} className="rounded border-stone-300 text-[#4F6B52]" />
              <label className="text-[11px] text-[#5E6B60]">I agree to the terms of use and privacy policy</label>
            </div>
          )}
          <button onClick={() => setCurrentScreen('verify')} className="w-full py-3 rounded-[14px] bg-[#4F6B52] text-white font-bold text-xs">
            {isSignUp ? 'Create account' : 'Sign in'}
          </button>
          <div className="relative flex py-2 items-center">
            <div className="flex-grow border-t border-[#EBDDE2]" />
            <span className="mx-2 text-[10px] text-stone-400 font-semibold">or</span>
            <div className="flex-grow border-t border-[#EBDDE2]" />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <button onClick={() => setCurrentScreen('verify')} className="py-2.5 rounded-[12px] border border-[#EBDDE2] bg-white text-xs font-semibold flex items-center justify-center gap-1.5">
              <span className="font-bold text-stone-700">G</span> Google
            </button>
            <button onClick={() => setCurrentScreen('verify')} className="py-2.5 rounded-[12px] border border-[#EBDDE2] bg-white text-xs font-semibold flex items-center justify-center gap-1.5">
              <span className="font-bold text-stone-900"></span> Apple
            </button>
          </div>
          <button onClick={() => setIsSignUp(!isSignUp)} className="text-xs text-[#5E6B60] w-full text-center">
            {isSignUp ? 'Already have an account? Sign in' : "Don't have an account? Sign up"}
          </button>
        </div>
      </div>
    </div>
  );
};