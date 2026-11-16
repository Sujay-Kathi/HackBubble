import React from 'react';
import { Bell, Smartphone, Monitor, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const TopAppBar: React.FC = () => {
  const {
    activeTab,
    setActiveTab,
    unreadNotifCount,
    setNotificationDrawerOpen,
    isMobileFrame,
    setIsMobileFrame,
    setAuthModalOpen,
    userProfile,
  } = useApp();

  const getTitle = () => {
    switch (activeTab) {
      case 'home':
        return 'Hackathons';
      case 'discover':
        return 'Find Teams';
      case 'create':
        return 'Create Team';
      case 'my-teams':
        return 'My Teams';
      case 'profile':
        return 'Profile';
      default:
        return 'HackBubble';
    }
  };

  return (
    <header className="sticky top-0 z-30 bg-bubble-cream/95 backdrop-blur-md border-b border-bubble-cream-border px-4 py-3 flex items-center justify-between transition-all">
      {/* Brand logo & screen title */}
      <div className="flex items-center gap-2.5">
        <div
          onClick={() => setActiveTab('home')}
          className="cursor-pointer flex items-center gap-2 group"
        >
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-bubble-sage-dark to-bubble-sage flex items-center justify-center text-white font-extrabold shadow-sm group-hover:scale-105 transition-transform">
            <span className="text-sm tracking-tight">HB</span>
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-base tracking-tight text-bubble-ink">HackBubble</span>
              <span className="w-1.5 h-1.5 rounded-full bg-bubble-sage-dark animate-pulse"></span>
            </div>
            <p className="text-[10px] text-bubble-muted font-medium capitalize leading-none -mt-0.5">{getTitle()}</p>
          </div>
        </div>
      </div>

      {/* Right actions: Desktop Frame toggle, Notification bell, User avatar */}
      <div className="flex items-center gap-2">
        {/* Toggle Mobile Frame view button (useful when on desktop) */}
        <button
          onClick={() => setIsMobileFrame(!isMobileFrame)}
          title={isMobileFrame ? "Switch to Wide Responsive View" : "Switch to Mobile Phone Preview"}
          className="hidden md:flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded-full bg-bubble-sage-light text-bubble-sage-deep hover:bg-bubble-sage/40 transition-colors border border-bubble-sage-border/50"
        >
          {isMobileFrame ? (
            <>
              <Monitor className="w-3.5 h-3.5" />
              <span>Full View</span>
            </>
          ) : (
            <>
              <Smartphone className="w-3.5 h-3.5" />
              <span>Phone Frame</span>
            </>
          )}
        </button>

        {/* Auth modal launcher */}
        <button
          onClick={() => setAuthModalOpen(true)}
          className="px-2 py-1 text-xs font-semibold rounded-lg bg-bubble-pink hover:bg-bubble-pink-border text-bubble-ink transition-colors flex items-center gap-1"
          title="Open Authentication Flow (ShipIt Wireframe)"
        >
          <Sparkles className="w-3 h-3 text-bubble-sage-dark" />
          <span className="hidden sm:inline">Auth Demo</span>
        </button>

        {/* Notifications */}
        <button
          onClick={() => setNotificationDrawerOpen(true)}
          className="relative p-2 rounded-full hover:bg-bubble-cream-dark transition-colors text-bubble-ink"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5" />
          {unreadNotifCount > 0 && (
            <span className="absolute top-1 right-1 min-w-[18px] h-[18px] px-1 bg-bubble-heart text-white text-[10px] font-bold rounded-full flex items-center justify-center shadow-sm animate-bounce">
              {unreadNotifCount}
            </span>
          )}
        </button>

        {/* Profile Avatar */}
        <button
          onClick={() => setActiveTab('profile')}
          className="p-0.5 rounded-full ring-2 ring-bubble-sage/60 hover:ring-bubble-sage-dark transition-all"
        >
          <img
            src={userProfile.avatar}
            alt={userProfile.name}
            className="w-7 h-7 rounded-full object-cover"
          />
        </button>
      </div>
    </header>
  );
};
