import React, { useState } from 'react';
import {
  Users,
  Sparkles,
  ArrowRight,
  CheckCircle2,
  XCircle,
  Clock,
  Plus,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { TeamWorkspaceScreen } from './TeamWorkspaceScreen';

export const MyTeamsScreen: React.FC = () => {
  const {
    teams,
    selectedTeamId,
    setSelectedTeamId,
    invitations,
    respondToInvitation,
    applications,
    setActiveTab,
    setScreeningTeamId,
  } = useApp();

  const [activeSubTab, setActiveSubTab] = useState<'leading' | 'invitations' | 'applications'>('leading');

  // If a team is actively selected, show its full Team Workspace!
  if (selectedTeamId) {
    return (
      <div className="space-y-2">
        <button
          onClick={() => setSelectedTeamId(null)}
          className="mx-4 mt-3 text-xs font-bold text-bubble-sage-deep hover:underline flex items-center gap-1"
        >
          ← Back to All Teams
        </button>
        <TeamWorkspaceScreen />
      </div>
    );
  }

  const pendingInvitations = invitations.filter(i => i.status === 'pending');

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Segmented Control */}
      <div className="flex p-1 bg-white rounded-2xl border border-bubble-cream-border shadow-soft">
        <button
          onClick={() => setActiveSubTab('leading')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
            activeSubTab === 'leading'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          Teams I Lead ({teams.length})
        </button>
        <button
          onClick={() => setActiveSubTab('invitations')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all relative ${
            activeSubTab === 'invitations'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          <span>Invitations</span>
          {pendingInvitations.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-bubble-heart inline-block ml-1"></span>
          )}
        </button>
        <button
          onClick={() => setActiveSubTab('applications')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
            activeSubTab === 'applications'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          Applications ({applications.length})
        </button>
      </div>

      {/* SUB-TAB 1: TEAMS I LEAD */}
      {activeSubTab === 'leading' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-black uppercase tracking-wider text-bubble-muted">
              Managed Teams
            </span>
            <button
              onClick={() => setActiveTab('create')}
              className="text-xs font-bold text-bubble-sage-deep flex items-center gap-1 hover:underline"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>New Team</span>
            </button>
          </div>

          {teams.map(t => (
            <div
              key={t.id}
              onClick={() => setSelectedTeamId(t.id)}
              className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-card hover:shadow-swipe transition-all cursor-pointer space-y-3"
            >
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-bubble-sage-deep block">
                    {t.hackathonTitle}
                  </span>
                  <h3 className="text-base font-black text-bubble-ink leading-tight">
                    {t.name}
                  </h3>
                  <p className="text-xs text-bubble-muted font-medium">
                    Leader: {t.leaderName}
                  </p>
                </div>

                <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                  t.status === 'full'
                    ? 'bg-emerald-100 text-emerald-800'
                    : 'bg-bubble-pink text-bubble-ink'
                }`}>
                  {t.currentSize}/{t.targetSize} Members
                </span>
              </div>

              <p className="text-xs text-stone-600 line-clamp-2 leading-relaxed">
                "{t.problemStatement}"
              </p>

              {/* Roster avatars preview */}
              <div className="pt-2 border-t border-bubble-cream-border flex items-center justify-between">
                <div className="flex -space-x-2">
                  {t.members.map(m => (
                    <img
                      key={m.id}
                      src={m.avatar}
                      alt={m.name}
                      title={`${m.name} (${m.role})`}
                      className="w-7 h-7 rounded-full border-2 border-white object-cover"
                    />
                  ))}
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={e => {
                      e.stopPropagation();
                      setScreeningTeamId(t.id);
                      setActiveTab('discover');
                    }}
                    className="py-1.5 px-3 rounded-xl bg-bubble-heart text-white text-xs font-bold shadow-sm hover:bg-rose-600"
                  >
                    Screen Candidates
                  </button>
                  <span className="text-xs font-bold text-bubble-sage-deep">
                    Manage →
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* SUB-TAB 2: INVITATIONS RECEIVED */}
      {activeSubTab === 'invitations' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-black uppercase tracking-wider text-bubble-muted">
              Team Invitations Received
            </span>
          </div>

          {invitations.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-3xl border border-bubble-cream-border text-bubble-muted">
              <p className="text-xs font-bold text-bubble-ink">No pending invitations</p>
              <p className="text-[11px] mt-0.5">When team leaders express interest in your profile, invitations will show here.</p>
            </div>
          ) : (
            invitations.map(inv => (
              <div
                key={inv.id}
                className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-card space-y-3"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <img
                      src={inv.leaderAvatar}
                      alt={inv.leaderName}
                      className="w-10 h-10 rounded-2xl object-cover border"
                    />
                    <div>
                      <h4 className="text-sm font-black text-bubble-ink leading-tight">
                        {inv.teamName}
                      </h4>
                      <p className="text-[11px] text-bubble-muted font-medium">
                        for {inv.hackathonTitle}
                      </p>
                      <span className="text-[10px] text-bubble-sage-deep font-bold">
                        Invited as: {inv.roleTitle}
                      </span>
                    </div>
                  </div>

                  <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold capitalize ${
                    inv.status === 'accepted'
                      ? 'bg-emerald-100 text-emerald-800'
                      : inv.status === 'declined'
                      ? 'bg-stone-100 text-stone-500'
                      : 'bg-bubble-pink text-bubble-ink'
                  }`}>
                    {inv.status === 'accepted' ? 'Accepted (Awaiting finalization)' : inv.status}
                  </span>
                </div>

                {inv.status === 'pending' && (
                  <div className="flex items-center gap-2 pt-2 border-t border-bubble-cream-border">
                    <button
                      onClick={() => respondToInvitation(inv.id, false)}
                      className="flex-1 py-2 rounded-xl border border-bubble-cream-border text-xs font-bold text-stone-600 hover:bg-stone-50"
                    >
                      Decline
                    </button>
                    <button
                      onClick={() => respondToInvitation(inv.id, true)}
                      className="flex-1 py-2 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white text-xs font-bold shadow-sm"
                    >
                      Accept Invitation
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      )}

      {/* SUB-TAB 3: MY APPLICATIONS */}
      {activeSubTab === 'applications' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-xs font-black uppercase tracking-wider text-bubble-muted">
              Applications You Submitted
            </span>
          </div>

          {applications.length === 0 ? (
            <div className="p-8 text-center bg-white rounded-3xl border border-bubble-cream-border text-bubble-muted">
              <p className="text-xs font-bold text-bubble-ink">No active applications</p>
              <p className="text-[11px] mt-0.5">Explore open teams and apply for role vacancies in the Discover tab.</p>
            </div>
          ) : (
            applications.map(app => (
              <div
                key={app.id}
                className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-card space-y-2"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-black text-bubble-ink leading-tight">
                      {app.teamName}
                    </h4>
                    <p className="text-[11px] text-bubble-muted font-medium">
                      {app.hackathonTitle}
                    </p>
                  </div>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-bubble-sage-light text-bubble-sage-deep capitalize">
                    {app.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="text-xs text-stone-600">
                  <strong>Role applied:</strong> {app.roleTitle}
                </div>

                {app.message && (
                  <p className="text-xs text-stone-500 bg-stone-50 p-2 rounded-xl italic">
                    "{app.message}"
                  </p>
                )}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
