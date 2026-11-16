import React, { useState } from 'react';
import {
  Users,
  UserCheck,
  UserPlus,
  Share2,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  Copy,
  Plus,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Team, TeamMember } from '../types';

export const TeamWorkspaceScreen: React.FC = () => {
  const {
    teams,
    selectedTeamId,
    setSelectedTeamId,
    interestedCandidates,
    applications,
    finalizeTeam,
    setScreeningTeamId,
    setActiveTab,
  } = useApp();

  const [activeTabSub, setActiveTabSub] = useState<'members' | 'invited' | 'requests'>('members');
  const [selectedForFinalize, setSelectedForFinalize] = useState<string[]>([]);

  const team = teams.find(t => t.id === selectedTeamId) || teams[0];

  // Candidates who were swiped right / invited by leader
  const invitedList = interestedCandidates;

  // Participant applications for this team
  const teamApps = applications.filter(a => a.teamId === team.id && a.status === 'submitted');

  const handleToggleSelectFinalize = (candId: string) => {
    if (selectedForFinalize.includes(candId)) {
      setSelectedForFinalize(selectedForFinalize.filter(id => id !== candId));
    } else {
      setSelectedForFinalize([...selectedForFinalize, candId]);
    }
  };

  const handleFinalizeConfirm = () => {
    if (selectedForFinalize.length === 0) {
      alert('Please check at least one accepted candidate to finalize into the official roster.');
      return;
    }
    const success = finalizeTeam(team.id, selectedForFinalize);
    if (success) {
      setSelectedForFinalize([]);
      setActiveTabSub('members');
    }
  };

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Team Header & Roster Status (ShipIt Wireframe 9) */}
      <div className="p-4 rounded-3xl bg-white border border-bubble-cream-border shadow-card space-y-3">
        <div className="flex items-start justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-bubble-sage-deep block">
              {team.hackathonTitle}
            </span>
            <h1 className="text-xl font-black text-bubble-ink leading-tight">
              {team.name}
            </h1>
            <p className="text-xs text-bubble-muted font-medium mt-0.5">
              Leader: <strong className="text-bubble-ink">{team.leaderName}</strong>
            </p>
          </div>

          <div className="text-right">
            <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
              team.status === 'full'
                ? 'bg-emerald-100 text-emerald-800'
                : 'bg-bubble-pink text-bubble-ink'
            }`}>
              {team.status === 'full' ? 'Roster Full' : `${team.currentSize}/${team.targetSize} Members`}
            </span>
            <span className="text-[10px] text-stone-400 block mt-1">
              {team.targetSize - team.currentSize} seats remaining
            </span>
          </div>
        </div>

        {/* Share Invite Code pill */}
        <div className="p-2.5 rounded-2xl bg-stone-50 border border-stone-200/80 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <Share2 className="w-3.5 h-3.5 text-stone-500" />
            <span className="font-mono text-stone-600 font-semibold">{team.inviteCode || 'hackathons.app/golt-2026'}</span>
          </div>
          <button
            onClick={() => {
              navigator.clipboard?.writeText(team.inviteCode || 'hackathons.app/golt-2026');
              alert('Team invite code copied to clipboard!');
            }}
            className="p-1 rounded-lg hover:bg-stone-200 text-stone-600"
            title="Copy Code"
          >
            <Copy className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* CTAs: + Add mates (opens swipe deck) */}
        <button
          onClick={() => {
            setScreeningTeamId(team.id);
            setActiveTab('discover');
          }}
          className="w-full py-2.5 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-sm flex items-center justify-center gap-1.5 transition-all"
        >
          <UserPlus className="w-4 h-4" />
          <span>+ Add mates (Screen & Swipe Candidates)</span>
        </button>
      </div>

      {/* Tabs (ShipIt Wireframe: Members / Invited / Request) */}
      <div className="flex p-1 bg-white rounded-2xl border border-bubble-cream-border shadow-soft">
        <button
          onClick={() => setActiveTabSub('members')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTabSub === 'members'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          Members ({team.members.length})
        </button>
        <button
          onClick={() => setActiveTabSub('invited')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all relative ${
            activeTabSub === 'invited'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          <span>Invited ({invitedList.length})</span>
          {invitedList.length > 0 && (
            <span className="w-2 h-2 rounded-full bg-bubble-heart inline-block ml-1"></span>
          )}
        </button>
        <button
          onClick={() => setActiveTabSub('requests')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
            activeTabSub === 'requests'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          Requests ({teamApps.length})
        </button>
      </div>

      {/* TAB 1: MEMBERS (Official Roster) */}
      {activeTabSub === 'members' && (
        <div className="space-y-2.5">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-bold text-bubble-muted uppercase">
              Official Team Roster ({team.members.length}/{team.targetSize})
            </span>
            <span className="text-[10px] text-emerald-600 font-bold">
              ✓ Confirmed Members
            </span>
          </div>

          {team.members.map(member => (
            <div
              key={member.id}
              className="p-3 bg-white rounded-2xl border border-bubble-cream-border shadow-soft flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <img
                  src={member.avatar}
                  alt={member.name}
                  className="w-10 h-10 rounded-2xl object-cover border border-bubble-cream-border shadow-sm"
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-black text-bubble-ink">{member.name}</span>
                    {member.isLeader && (
                      <span className="px-1.5 py-0.2 bg-bubble-pink text-bubble-sage-deep font-bold text-[9px] rounded-md">
                        Leader
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-bubble-muted font-medium">{member.role}</span>
                </div>
              </div>
              <span className="text-[10px] text-stone-400 font-medium">Joined {member.joinedAt}</span>
            </div>
          ))}
        </div>
      )}

      {/* TAB 2: INVITED / SHORTLIST (SRS Candidate Screening Pass & Finalization) */}
      {activeTabSub === 'invited' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-bold text-bubble-muted uppercase">
              Shortlisted Candidates ({invitedList.length})
            </span>
            <span className="text-[10px] text-bubble-sage-deep font-bold">
              Two-sided Consent
            </span>
          </div>

          {invitedList.length === 0 ? (
            <div className="p-6 text-center bg-white rounded-2xl border border-bubble-cream-border text-bubble-muted">
              <p className="text-xs font-bold text-bubble-ink mb-1">No shortlisted candidates yet</p>
              <p className="text-[11px]">Swipe right on candidates in the screening deck to invite them.</p>
              <button
                onClick={() => {
                  setScreeningTeamId(team.id);
                  setActiveTab('discover');
                }}
                className="mt-3 py-1.5 px-3 bg-bubble-sage-light text-bubble-sage-deep text-xs font-bold rounded-xl"
              >
                Open Candidate Screening Deck
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <p className="text-[11px] text-stone-500 bg-bubble-cream p-2.5 rounded-xl border border-bubble-cream-border">
                💡 Check candidates who have accepted to finalize them into your official roster.
              </p>

              {invitedList.map(cand => (
                <div
                  key={cand.id}
                  className="p-3 bg-white rounded-2xl border border-bubble-cream-border shadow-soft flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={selectedForFinalize.includes(cand.id)}
                      onChange={() => handleToggleSelectFinalize(cand.id)}
                      className="w-4 h-4 rounded text-bubble-sage-deep focus:ring-bubble-sage cursor-pointer"
                    />
                    <img
                      src={cand.avatar}
                      alt={cand.name}
                      className="w-10 h-10 rounded-2xl object-cover border border-bubble-cream-border"
                    />
                    <div>
                      <span className="text-xs font-bold text-bubble-ink block">{cand.name}</span>
                      <span className="text-[10px] text-bubble-muted">{cand.role}</span>
                      <span className="text-[9px] text-emerald-600 font-bold block">
                        ✓ Accepted — Ready for Finalization
                      </span>
                    </div>
                  </div>

                  <span className="text-[10px] font-bold text-bubble-sage-deep bg-bubble-sage-light px-2 py-0.5 rounded-full">
                    {cand.matchScore}% Match
                  </span>
                </div>
              ))}

              {/* Finalization Action Button (SRS SYS-FR-024) */}
              <button
                onClick={handleFinalizeConfirm}
                disabled={selectedForFinalize.length === 0}
                className={`w-full py-3 rounded-2xl font-bold text-xs shadow-md transition-all flex items-center justify-center gap-1.5 ${
                  selectedForFinalize.length > 0
                    ? 'bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white shadow-bubble-sage-deep/20'
                    : 'bg-stone-200 text-stone-400 cursor-not-allowed'
                }`}
              >
                <ShieldCheck className="w-4 h-4" />
                <span>
                  Finalize {selectedForFinalize.length} Member(s) into Official Roster
                </span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* TAB 3: REQUESTS (Applicant Requests) */}
      {activeTabSub === 'requests' && (
        <div className="space-y-3">
          <div className="flex items-center justify-between px-1">
            <span className="text-[11px] font-bold text-bubble-muted uppercase">
              Incoming Applications ({teamApps.length})
            </span>
          </div>

          {teamApps.length === 0 ? (
            <div className="p-6 text-center bg-white rounded-2xl border border-bubble-cream-border text-bubble-muted">
              <p className="text-xs font-bold text-bubble-ink">No pending applicant requests</p>
              <p className="text-[11px] mt-0.5">When participants apply for vacancies, they will appear here.</p>
            </div>
          ) : (
            teamApps.map(app => (
              <div
                key={app.id}
                className="p-3 bg-white rounded-2xl border border-bubble-cream-border shadow-soft space-y-2"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2.5">
                    <img
                      src={app.applicantAvatar}
                      alt={app.applicantName}
                      className="w-9 h-9 rounded-2xl object-cover border"
                    />
                    <div>
                      <span className="text-xs font-bold text-bubble-ink block">{app.applicantName}</span>
                      <span className="text-[10px] text-bubble-sage-deep font-semibold">
                        Applied for: {app.roleTitle}
                      </span>
                    </div>
                  </div>
                  <span className="text-[10px] text-stone-400 font-medium">Just now</span>
                </div>

                {app.message && (
                  <p className="text-xs text-stone-600 bg-stone-50 p-2 rounded-xl italic">
                    "{app.message}"
                  </p>
                )}

                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => alert('Applicant declined.')}
                    className="flex-1 py-1.5 rounded-xl border border-stone-200 text-xs font-bold text-stone-600 hover:bg-stone-50"
                  >
                    Decline
                  </button>
                  <button
                    onClick={() => {
                      finalizeTeam(team.id, [app.applicantId]);
                      alert('Applicant approved and added to official roster!');
                    }}
                    className="flex-1 py-1.5 rounded-xl bg-bubble-sage-deep text-white text-xs font-bold hover:bg-bubble-sage-dark shadow-sm"
                  >
                    Accept & Finalize
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
};
