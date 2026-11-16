import React from 'react';
import { X, CheckCheck, Bell, Sparkles } from 'lucide-react';
import { useApp } from '../../context/AppContext';

export const NotificationDrawer: React.FC = () => {
  const {
    notificationDrawerOpen,
    setNotificationDrawerOpen,
    notifications,
    markNotifAsRead,
    markAllNotifsAsRead,
    setActiveTab,
    setSelectedHackathonId,
    setSelectedTeamId,
  } = useApp();

  if (!notificationDrawerOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex justify-end transition-opacity">
      <div className="w-full max-w-sm bg-bubble-cream h-full shadow-2xl flex flex-col border-l border-bubble-cream-border animate-in slide-in-from-right duration-200">
        {/* Header */}
        <div className="p-4 border-b border-bubble-cream-border flex items-center justify-between bg-white">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-bubble-sage-light text-bubble-sage-deep">
              <Bell className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-bubble-ink text-base">Notifications</h3>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={markAllNotifsAsRead}
              className="text-xs text-bubble-sage-deep hover:underline flex items-center gap-1 font-medium"
              title="Mark all as read"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              <span>Read all</span>
            </button>
            <button
              onClick={() => setNotificationDrawerOpen(false)}
              className="p-1 rounded-full hover:bg-stone-100 text-stone-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {notifications.length === 0 ? (
            <div className="text-center py-12 text-bubble-muted">
              <Sparkles className="w-8 h-8 mx-auto mb-2 opacity-40 text-bubble-sage-dark" />
              <p className="text-sm font-medium">No new notifications</p>
            </div>
          ) : (
            notifications.map(notif => (
              <div
                key={notif.id}
                onClick={() => {
                  markNotifAsRead(notif.id);
                  if (notif.targetTab) setActiveTab(notif.targetTab);
                  if (notif.targetId && notif.targetTab === 'home') setSelectedHackathonId(notif.targetId);
                  if (notif.targetId && notif.targetTab === 'my-teams') setSelectedTeamId(notif.targetId);
                  setNotificationDrawerOpen(false);
                }}
                className={`p-3.5 rounded-2xl border transition-all cursor-pointer relative ${
                  notif.read
                    ? 'bg-white/80 border-stone-200/80 text-bubble-ink'
                    : 'bg-bubble-pink/30 border-bubble-pink-border text-bubble-ink font-semibold shadow-sm'
                }`}
              >
                {!notif.read && (
                  <span className="absolute top-3 right-3 w-2 h-2 rounded-full bg-bubble-heart"></span>
                )}
                <div className="text-xs font-bold text-bubble-sage-deep mb-1">
                  {notif.title}
                </div>
                <p className="text-xs text-bubble-muted line-clamp-2 leading-relaxed">
                  {notif.message}
                </p>
                <div className="mt-2 text-[10px] text-stone-400 font-medium">
                  {notif.time}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
