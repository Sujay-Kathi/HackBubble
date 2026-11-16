import React, { useState } from 'react';
import {
  Search,
  Users,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  X,
  Share2,
  Plus,
  Send,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Team, TeamRole } from '../types';
import { CandidateScreeningScreen } from './CandidateScreeningScreen';

export const DiscoverScreen: React.FC = () => {
  const {
    teams,
    applyToRole,
    setActiveTab,
    applications,
    setScreeningTeamId,
  } = useApp();

  const [activeSubMode, setActiveSubMode] = useState<'find-team' | 'screen-candidates'>('find-team');
  const [inviteCodeInput, setInviteCodeInput] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTeamForApply, setSelectedTeamForApply] = useState<Team | null>(null);
  const [selectedRoleId, setSelectedRoleId] = useState<string>('');
  const [applyMessage, setApplyMessage] = useState<string>('');

  const filteredTeams = teams.filter(t => {
    if (searchQuery.trim() === '') return true;
    const q = searchQuery.toLowerCase();
    const matchName = t.name.toLowerCase().includes(q);
    const matchHack = t.hackathonTitle.toLowerCase().includes(q);
    const matchRole = t.roles.some(r => r.title.toLowerCase().includes(q));
    return matchName || matchHack || matchRole;
  });

  const handleApplySubmit = () => {
    if (!selectedTeamForApply || !selectedRoleId) {
      alert('Please select a role vacancy to apply for.');
      return;
    }
    applyToRole(selectedTeamForApply.id, selectedRoleId, applyMessage);
    setSelectedTeamForApply(null);
    setSelectedRoleId('');
    setApplyMessage('');
    alert('Application sent successfully! The leader will review your profile.');
  };

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Sub-Mode Toggle: Participant "Find Team" vs Leader "Candidate Screening" */}
      <div className="flex p-1 bg-white rounded-2xl border border-bubble-cream-border shadow-soft">
        <button
          onClick={() => setActiveSubMode('find-team')}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
            activeSubMode === 'find-team'
              ? 'bg-bubble-sage-deep text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>Join a Team</span>
        </button>
        <button
          onClick={() => {
            setScreeningTeamId('team-golt');
            setActiveSubMode('screen-candidates');
          }}
          className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all flex items-center justify-center gap-1.5 ${
            activeSubMode === 'screen-candidates'
              ? 'bg-bubble-heart text-white shadow-sm'
              : 'text-bubble-muted hover:text-bubble-ink'
          }`}
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Leader Screening Deck</span>
        </button>
      </div>

      {/* MODE 1: CANDIDATE SCREENING SWIPE DECK */}
      {activeSubMode === 'screen-candidates' ? (
        <CandidateScreeningScreen />
      ) : (
        /* MODE 2: PARTICIPANT DISCOVERY & JOIN TEAM (ShipIt Wireframe 8 & 10) */
        <div className="space-y-4">
          {/* Header Action Banner */}
          <div className="p-4 rounded-3xl bg-gradient-to-tr from-bubble-cream-dark to-white border border-bubble-cream-border space-y-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-bubble-sage-deep block">
              Find your hackathon team
            </span>
            <h2 className="text-base font-black text-bubble-ink">
              Collaborate & Build Something Great
            </h2>
            <p className="text-xs text-bubble-muted leading-relaxed">
              Browse teams with open role vacancies or join with a private team invite code.
            </p>

            <div className="pt-1 flex items-center gap-2">
              <button
                onClick={() => setActiveTab('create')}
                className="py-1.5 px-3 rounded-xl bg-bubble-sage-deep text-white font-bold text-xs flex items-center gap-1"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Create New Team</span>
              </button>
            </div>
          </div>

          {/* Join with Code / Link (ShipIt Wireframe 10) */}
          <div className="p-3.5 bg-white rounded-2xl border border-bubble-cream-border shadow-soft space-y-2">
            <label className="text-xs font-bold text-bubble-ink block">
              Invite link or code
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={inviteCodeInput}
                onChange={e => setInviteCodeInput(e.target.value)}
                placeholder="e.g. hackathons.app/golt-2026"
                className="flex-1 px-3 py-2 rounded-xl bg-stone-50 border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:outline-none focus:ring-1 focus:ring-bubble-sage"
              />
              <button
                onClick={() => {
                  if (inviteCodeInput.trim()) {
                    alert(`Validating invite code: ${inviteCodeInput}. Connecting to team...`);
                    setInviteCodeInput('');
                  } else {
                    alert('Please enter an invite code or link.');
                  }
                }}
                className="py-2 px-4 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-sm transition-colors"
              >
                Join
              </button>
            </div>
          </div>

          {/* Search Teams */}
          <div className="relative">
            <Search className="w-4 h-4 text-stone-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search by team name or role..."
              className="w-full pl-9 pr-3 py-2.5 rounded-2xl bg-white border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:outline-none focus:ring-2 focus:ring-bubble-sage shadow-soft"
            />
          </div>

          {/* Open Teams List (Matching Wireframe 10 Cards: Team Golt, AI Visionarius) */}
          <div className="space-y-3">
            <div className="flex items-center justify-between px-1">
              <span className="text-xs font-black uppercase tracking-wider text-bubble-muted">
                Teams Recruiting ({filteredTeams.length})
              </span>
              <span className="text-[11px] text-bubble-sage-deep font-semibold">
                Open Vacancies
              </span>
            </div>

            {filteredTeams.map(t => {
              const hasApplied = applications.some(a => a.teamId === t.id && a.status === 'submitted');

              return (
                <div
                  key={t.id}
                  className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-card space-y-3"
                >
                  {/* Team Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2.5">
                      <img
                        src={t.leaderAvatar}
                        alt={t.leaderName}
                        className="w-10 h-10 rounded-2xl object-cover border border-bubble-cream-border shadow-sm"
                      />
                      <div>
                        <h3 className="text-sm font-black text-bubble-ink leading-tight">
                          {t.name}
                        </h3>
                        <p className="text-[11px] text-bubble-muted font-medium">
                          for <strong className="text-bubble-sage-deep">{t.hackathonTitle}</strong>
                        </p>
                      </div>
                    </div>

                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-bubble-cream-dark text-bubble-ink">
                      {t.currentSize}/{t.targetSize} Members
                    </span>
                  </div>

                  {/* Problem Statement snippet */}
                  <p className="text-xs text-stone-600 line-clamp-2 leading-relaxed">
                    "{t.problemStatement}"
                  </p>

                  {/* Roles Recruiting */}
                  <div className="space-y-1.5 pt-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-bubble-muted">
                      Open Roles
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {t.roles.map(r => (
                        <div
                          key={r.id}
                          className="px-2.5 py-1 rounded-xl bg-bubble-sage-light/60 border border-bubble-sage-border/50 text-[11px] font-bold text-bubble-sage-deep flex items-center gap-1.5"
                        >
                          <span>{r.title}</span>
                          <span className="w-1.5 h-1.5 rounded-full bg-bubble-sage-dark"></span>
                          <span className="text-[9px] text-stone-500 font-semibold">{r.vacancies} needed</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Roster Preview */}
                  <div className="pt-2 border-t border-bubble-cream-border flex items-center justify-between">
                    <div className="flex -space-x-2">
                      {t.members.map(m => (
                        <img
                          key={m.id}
                          src={m.avatar}
                          alt={m.name}
                          title={`${m.name} (${m.role})`}
                          className="w-6 h-6 rounded-full border-2 border-white object-cover shadow-sm"
                        />
                      ))}
                    </div>

                    <button
                      onClick={() => {
                        setSelectedTeamForApply(t);
                        setSelectedRoleId(t.roles[0]?.id || '');
                      }}
                      disabled={hasApplied}
                      className={`py-1.5 px-4 rounded-xl font-bold text-xs transition-all shadow-sm ${
                        hasApplied
                          ? 'bg-stone-100 text-stone-400 cursor-not-allowed'
                          : 'bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white'
                      }`}
                    >
                      {hasApplied ? 'Request Sent' : 'Request to Join'}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* APPLICATION BOTTOM SHEET MODAL */}
          {selectedTeamForApply && (
            <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4">
              <div className="bg-bubble-cream w-full max-w-sm rounded-t-[32px] sm:rounded-[32px] border border-bubble-cream-border p-5 shadow-2xl space-y-4 animate-in slide-in-from-bottom duration-200">
                <div className="flex items-center justify-between pb-2 border-b border-bubble-cream-border">
                  <div>
                    <h3 className="text-base font-black text-bubble-ink">
                      Join {selectedTeamForApply.name}
                    </h3>
                    <p className="text-[11px] text-bubble-muted">
                      Select which vacancy you want to fill
                    </p>
                  </div>
                  <button
                    onClick={() => setSelectedTeamForApply(null)}
                    className="p-1 rounded-full hover:bg-stone-200 text-stone-600"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                {/* Role select */}
                <div className="space-y-1.5">
                  <label className="text-xs font-bold text-bubble-ink block">Available Role</label>
                  <div className="space-y-1.5">
                    {selectedTeamForApply.roles.map(r => (
                      <div
                        key={r.id}
                        onClick={() => setSelectedRoleId(r.id)}
                        className={`p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                          selectedRoleId === r.id
                            ? 'bg-bubble-sage-light border-bubble-sage-dark text-bubble-sage-deep font-bold shadow-sm'
                            : 'bg-white border-bubble-cream-border text-bubble-ink'
                        }`}
                      >
                        <div>
                          <span className="text-xs font-bold block">{r.title}</span>
                          <span className="text-[10px] text-stone-500">
                            Must-have: {r.mustHaveSkills.join(', ')}
                          </span>
                        </div>
                        {selectedRoleId === r.id && (
                          <CheckCircle2 className="w-4 h-4 text-bubble-sage-dark" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Optional Message to Leader */}
                <div className="space-y-1">
                  <label className="text-xs font-bold text-bubble-ink block">
                    Message to Leader (Optional)
                  </label>
                  <textarea
                    value={applyMessage}
                    onChange={e => setApplyMessage(e.target.value)}
                    placeholder="Briefly state your relevant project experience or enthusiasm..."
                    rows={2}
                    className="w-full p-2.5 rounded-xl border border-bubble-cream-border bg-white text-xs text-bubble-ink font-medium focus:outline-none focus:ring-1 focus:ring-bubble-sage"
                  />
                </div>

                {/* Actions */}
                <div className="pt-2 flex items-center gap-2">
                  <button
                    onClick={() => setSelectedTeamForApply(null)}
                    className="flex-1 py-2.5 rounded-xl border border-bubble-cream-border bg-stone-100 text-xs font-bold text-stone-700"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleApplySubmit}
                    className="flex-1 py-2.5 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white text-xs font-bold shadow-md flex items-center justify-center gap-1.5"
                  >
                    <Send className="w-3.5 h-3.5" />
                    <span>Send Application</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
