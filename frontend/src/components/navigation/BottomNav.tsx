import React from 'react';
import { Home, Compass, PlusCircle, Users, User, LucideIcon } from 'lucide-react';
import { useApp } from '../../context/AppContext';

interface NavItem {
  id: 'home' | 'discover' | 'create' | 'my-teams' | 'profile';
  label: string;
  icon: LucideIcon;
  isPrimary?: boolean;
  badge?: number;
}

export const BottomNav: React.FC = () => {
  const { activeTab, setActiveTab, invitations } = useApp();

  const pendingInvitations = invitations.filter(i => i.status === 'pending').length;

  const navItems: NavItem[] = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'discover', label: 'Discover', icon: Compass },
    { id: 'create', label: 'Create', icon: PlusCircle, isPrimary: true },
    { id: 'my-teams', label: 'My Teams', icon: Users, badge: pendingInvitations },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 bg-bubble-cream/95 backdrop-blur-md border-t border-bubble-cream-border safe-area-pb transition-all">
      <div className="max-w-md mx-auto px-4 py-2 flex items-center justify-between">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;

          if (item.isPrimary) {
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className="flex flex-col items-center group -mt-5"
                aria-label={item.label}
              >
                <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-transform duration-200 group-hover:scale-110 ${
                  isActive
                    ? 'bg-bubble-sage-deep text-white shadow-bubble-sage/40'
                    : 'bg-bubble-sage-dark text-white shadow-bubble-sage-dark/30'
                }`}>
                  <Icon className="w-6 h-6 stroke-[2.2]" />
                </div>
                <span className={`text-[10px] font-bold mt-1 transition-colors ${
                  isActive ? 'text-bubble-sage-deep' : 'text-bubble-muted'
                }`}>
                  {item.label}
                </span>
              </button>
            );
          }

          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`flex flex-col items-center py-1 px-2.5 rounded-xl transition-all relative ${
                isActive
                  ? 'text-bubble-sage-deep font-bold scale-105'
                  : 'text-bubble-muted hover:text-bubble-ink font-medium'
              }`}
            >
              <div className="relative">
                <Icon className={`w-5 h-5 transition-transform ${isActive ? 'stroke-[2.5]' : 'stroke-[1.8]'}`} />
                {item.badge && item.badge > 0 ? (
                  <span className="absolute -top-1.5 -right-2 min-w-[15px] h-[15px] px-1 bg-bubble-heart text-white text-[9px] font-bold rounded-full flex items-center justify-center">
                    {item.badge}
                  </span>
                ) : null}
              </div>
              <span className="text-[10px] mt-1 tracking-tight">
                {item.label}
              </span>
              {isActive && (
                <span className="w-1 h-1 rounded-full bg-bubble-sage-deep mt-0.5"></span>
              )}
            </button>
          );
        })}
      </div>
    </nav>
  );
};
