import React, { useState } from 'react';
import { X, Sparkles, ArrowRight, ShieldCheck, Mail, Lock, User as UserIcon } from 'lucide-react';
import { useApp } from '../context/AppContext';

export const AuthModal: React.FC = () => {
  const { authModalOpen, setAuthModalOpen, userProfile, updateUserProfile, login, register } = useApp();
  const [step, setStep] = useState<'welcome' | 'form' | 'verify'>('welcome');
  const [isSignUp, setIsSignUp] = useState<boolean>(true);
  const [name, setName] = useState<string>(userProfile.name);
  const [email, setEmail] = useState<string>(userProfile.email);
  const [password, setPassword] = useState<string>('••••••••');
  const [otp, setOtp] = useState<string[]>(['4', '2', '8', '1', '9', '0']);

  if (!authModalOpen) return null;

  const handleVerify = async () => {
    try {
      if (isSignUp) {
        await register(email, password, name);
      } else {
        await login(email, password);
      }
    } catch (e) {
      console.error(e);
    }
    updateUserProfile({ name, email });
    setAuthModalOpen(false);
    setStep('welcome');
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-bubble-cream w-full max-w-sm rounded-[32px] border border-bubble-cream-border p-6 shadow-2xl relative overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Close Button */}
        <button
          onClick={() => setAuthModalOpen(false)}
          className="absolute top-4 right-4 p-2 rounded-full hover:bg-stone-200/60 text-stone-600 transition-colors z-10"
        >
          <X className="w-5 h-5" />
        </button>

        {/* STEP 1: WELCOME SCREEN (ShipIt Wireframe 1) */}
        {step === 'welcome' && (
          <div className="text-center pt-2 pb-1 space-y-6">
            <div className="w-16 h-16 mx-auto rounded-3xl bg-gradient-to-tr from-bubble-sage-dark to-bubble-sage flex items-center justify-center text-white text-2xl font-black shadow-card">
              HB
            </div>

            <div className="space-y-2">
              <h2 className="text-2xl font-black tracking-tight text-bubble-ink">
                HackBubble
              </h2>
              <div className="h-44 w-full rounded-2xl bg-gradient-to-b from-bubble-pink/50 to-bubble-sage-light/60 border border-bubble-cream-border flex flex-col items-center justify-center p-4 relative overflow-hidden">
                {/* Decorative wireframe visual */}
                <div className="w-20 h-20 rounded-full bg-white/70 flex items-center justify-center shadow-sm mb-2">
                  <Sparkles className="w-10 h-10 text-bubble-sage-dark animate-pulse" />
                </div>
                <p className="text-xs font-semibold text-bubble-sage-deep">
                  Hackathons & challenges — in one place.
                </p>
                <p className="text-[11px] text-bubble-muted text-center mt-1 max-w-[240px]">
                  Find events, build a team, and submit projects without the chaos.
                </p>
              </div>
            </div>

            <div className="space-y-3">
              <button
                onClick={() => {
                  setIsSignUp(true);
                  setStep('form');
                }}
                className="w-full py-3.5 px-4 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-sm shadow-md flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
              >
                <span>Get Started</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => {
                  setIsSignUp(false);
                  setStep('form');
                }}
                className="text-xs font-semibold text-bubble-muted hover:text-bubble-ink transition-colors"
              >
                Already have an account? <span className="text-bubble-sage-deep underline">Sign in</span>
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: SIGN UP / SIGN IN (ShipIt Wireframe 2) */}
        {step === 'form' && (
          <div className="space-y-4 pt-1">
            <div className="text-center space-y-1">
              <h2 className="text-xl font-bold tracking-tight text-bubble-ink">
                {isSignUp ? "Let's begin" : "Welcome back"}
              </h2>
              <p className="text-xs text-bubble-muted">
                {isSignUp
                  ? "Create an account to save events and move towards results."
                  : "Sign in to manage your teams and hackathons."}
              </p>
            </div>

            <div className="space-y-3">
              {isSignUp && (
                <div>
                  <label className="text-[11px] font-bold text-bubble-ink block mb-1">Name</label>
                  <div className="relative">
                    <UserIcon className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
                    <input
                      type="text"
                      value={name}
                      onChange={e => setName(e.target.value)}
                      placeholder="e.g. Oleksandr Kuzmak"
                      className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-bubble-cream-border bg-white text-xs text-bubble-ink focus:outline-none focus:ring-2 focus:ring-bubble-sage font-medium"
                    />
                  </div>
                </div>
              )}

              <div>
                <label className="text-[11px] font-bold text-bubble-ink block mb-1">Email or Phone</label>
                <div className="relative">
                  <Mail className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
                  <input
                    type="email"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    placeholder="example@shipit.com"
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-bubble-cream-border bg-white text-xs text-bubble-ink focus:outline-none focus:ring-2 focus:ring-bubble-sage font-medium"
                  />
                </div>
              </div>

              <div>
                <label className="text-[11px] font-bold text-bubble-ink block mb-1">Password</label>
                <div className="relative">
                  <Lock className="w-4 h-4 text-stone-400 absolute left-3 top-3" />
                  <input
                    type="password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-bubble-cream-border bg-white text-xs text-bubble-ink focus:outline-none focus:ring-2 focus:ring-bubble-sage font-medium"
                  />
                </div>
                <p className="text-[10px] text-stone-400 mt-1">Include 1 digit and 1 uppercase letter.</p>
              </div>

              <div className="flex items-center gap-2 pt-1">
                <input
                  type="checkbox"
                  id="terms"
                  defaultChecked
                  className="rounded border-stone-300 text-bubble-sage-deep focus:ring-bubble-sage"
                />
                <label htmlFor="terms" className="text-[11px] text-bubble-muted">
                  I agree to the terms of use and privacy policy
                </label>
              </div>

              <button
                onClick={() => setStep('verify')}
                className="w-full py-3 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md transition-all mt-2"
              >
                {isSignUp ? 'Create account' : 'Sign In'}
              </button>

              <div className="relative flex py-2 items-center">
                <div className="flex-grow border-t border-bubble-cream-border"></div>
                <span className="flex-shrink mx-2 text-[10px] text-stone-400 font-semibold">or</span>
                <div className="flex-grow border-t border-bubble-cream-border"></div>
              </div>

              {/* Social login buttons */}
              <div className="grid grid-cols-2 gap-2">
                <button
                  onClick={() => setStep('verify')}
                  className="py-2.5 px-3 rounded-xl border border-bubble-cream-border bg-white hover:bg-stone-50 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span className="font-bold text-stone-700">G</span>
                  <span>Google</span>
                </button>
                <button
                  onClick={() => setStep('verify')}
                  className="py-2.5 px-3 rounded-xl border border-bubble-cream-border bg-white hover:bg-stone-50 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
                >
                  <span className="font-bold text-stone-900"></span>
                  <span>Apple</span>
                </button>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: VERIFY CODE (ShipIt Wireframe 3) */}
        {step === 'verify' && (
          <div className="text-center space-y-5 pt-2 pb-1">
            <div className="w-12 h-12 mx-auto rounded-2xl bg-bubble-sage-light text-bubble-sage-deep flex items-center justify-center">
              <ShieldCheck className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <h2 className="text-xl font-bold tracking-tight text-bubble-ink">Verify code</h2>
              <p className="text-xs text-bubble-muted max-w-[240px] mx-auto">
                Enter the 6-digit code we sent to <span className="font-semibold text-bubble-ink">{email}</span>
              </p>
            </div>

            {/* 6 Digit Input Boxes */}
            <div className="flex justify-center gap-2">
              {otp.map((digit, idx) => (
                <input
                  key={idx}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={e => {
                    const newOtp = [...otp];
                    newOtp[idx] = e.target.value;
                    setOtp(newOtp);
                  }}
                  className="w-10 h-12 rounded-xl border-2 border-bubble-cream-border bg-white text-center font-bold text-base text-bubble-ink focus:border-bubble-sage-dark focus:outline-none transition-colors shadow-sm"
                />
              ))}
            </div>

            <div className="space-y-3 pt-2">
              <button
                onClick={handleVerify}
                className="w-full py-3 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md transition-all"
              >
                Continue to HackBubble
              </button>

              <div className="text-xs text-bubble-muted">
                Didn't get a code?{' '}
                <button
                  onClick={() => alert('New 6-digit code sent: 428190')}
                  className="text-bubble-sage-deep font-bold hover:underline"
                >
                  Resend
                </button>
              </div>

              <button
                onClick={() => setStep('welcome')}
                className="text-[11px] text-stone-400 hover:text-stone-600 block mx-auto"
              >
                Back to sign in
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
