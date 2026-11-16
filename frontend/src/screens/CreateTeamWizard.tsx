import React, { useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Plus,
  Trash2,
  CheckCircle2,
  Sparkles,
  Users,
  Clock,
  HelpCircle,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { TeamRole, TeamPreference } from '../types';

export const CreateTeamWizard: React.FC = () => {
  const { hackathons, createTeam, setActiveTab, setSelectedTeamId } = useApp();

  const [currentStep, setCurrentStep] = useState<number>(1);

  // Form state
  const [selectedHackathonId, setSelectedHackathonId] = useState<string>(hackathons[0]?.id || '');
  const [teamName, setTeamName] = useState<string>('');
  const [teamDescription, setTeamDescription] = useState<string>('');
  const [problemStatement, setProblemStatement] = useState<string>('');
  const [projectIdea, setProjectIdea] = useState<string>('');
  const [targetSize, setTargetSize] = useState<number>(4);

  // Role vacancies state
  const [roles, setRoles] = useState<TeamRole[]>([
    {
      id: 'r-1',
      title: 'Fullstack Developer',
      vacancies: 1,
      filledCount: 0,
      mustHaveSkills: ['React', 'FastAPI'],
      preferredSkills: ['PostgreSQL'],
      experienceLevel: 'Some experience',
      priority: 'Must fill',
    },
    {
      id: 'r-2',
      title: 'UI/UX Designer',
      vacancies: 1,
      filledCount: 0,
      mustHaveSkills: ['Figma'],
      preferredSkills: ['Design Systems'],
      experienceLevel: 'Any',
      priority: 'Must fill',
    }
  ]);

  // Working preferences
  const [preferences, setPreferences] = useState<TeamPreference>({
    timeCommitment: 'Weekend (20-30 hours)',
    collaborationStyle: 'Collaborative with voice & PRs',
    meetingFrequency: 'Daily standup at 10:00 GMT',
    beginnerFriendly: true,
  });

  const selectedHackathon = hackathons.find(h => h.id === selectedHackathonId) || hackathons[0];

  const handleAddRole = () => {
    const newRole: TeamRole = {
      id: `r-${Date.now()}`,
      title: 'Backend Developer',
      vacancies: 1,
      filledCount: 0,
      mustHaveSkills: ['Python', 'PostgreSQL'],
      preferredSkills: ['Docker'],
      experienceLevel: 'Some experience',
      priority: 'Must fill',
    };
    setRoles([...roles, newRole]);
  };

  const handleRemoveRole = (id: string) => {
    setRoles(roles.filter(r => r.id !== id));
  };

  const handlePublish = () => {
    if (!teamName.trim() || !problemStatement.trim()) {
      alert('Please provide a team name and problem statement.');
      return;
    }

    const newTeamId = createTeam({
      hackathonId: selectedHackathon.id,
      hackathonTitle: selectedHackathon.title,
      name: teamName,
      description: teamDescription,
      problemStatement,
      idea: projectIdea,
      targetSize,
      roles,
      preferences,
    });

    setSelectedTeamId(newTeamId);
    setActiveTab('my-teams');
  };

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Wizard Step Progress Header */}
      <div className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-soft space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-6 h-6 rounded-full bg-bubble-sage-deep text-white text-xs font-bold flex items-center justify-center">
              {currentStep}
            </span>
            <h2 className="text-sm font-black text-bubble-ink">
              {currentStep === 1 && 'Choose Hackathon'}
              {currentStep === 2 && 'Team Identity'}
              {currentStep === 3 && 'Problem Statement & Idea'}
              {currentStep === 4 && 'Target Size & Roles'}
              {currentStep === 5 && 'Working Style & Preferences'}
              {currentStep === 6 && 'Review & Publish Team'}
            </h2>
          </div>
          <span className="text-[11px] font-bold text-bubble-muted">Step {currentStep} of 6</span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-stone-100 h-1.5 rounded-full overflow-hidden">
          <div
            className="bg-bubble-sage-deep h-full rounded-full transition-all duration-300"
            style={{ width: `${(currentStep / 6) * 100}%` }}
          ></div>
        </div>
      </div>

      {/* STEP 1: CHOOSE HACKATHON */}
      {currentStep === 1 && (
        <div className="space-y-3 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Select the Hackathon</h3>
            <p className="text-xs text-bubble-muted">
              Every team in HackBubble is bound to a verified hackathon event.
            </p>
          </div>

          <div className="space-y-2">
            {hackathons.map(h => (
              <div
                key={h.id}
                onClick={() => setSelectedHackathonId(h.id)}
                className={`p-3.5 rounded-2xl border transition-all cursor-pointer flex items-center justify-between ${
                  selectedHackathonId === h.id
                    ? 'bg-bubble-sage-light border-bubble-sage-dark shadow-sm'
                    : 'bg-white border-bubble-cream-border hover:bg-stone-50'
                }`}
              >
                <div>
                  <span className="text-xs font-bold text-bubble-ink block">{h.title}</span>
                  <span className="text-[10px] text-stone-500 font-medium">
                    {h.organizer} • {h.mode} • {h.prizePool}
                  </span>
                </div>
                {selectedHackathonId === h.id && (
                  <CheckCircle2 className="w-5 h-5 text-bubble-sage-dark" />
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* STEP 2: TEAM IDENTITY */}
      {currentStep === 2 && (
        <div className="space-y-4 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Team Identity</h3>
            <p className="text-xs text-bubble-muted">
              Give your team a memorable name and short introduction.
            </p>
          </div>

          <div className="space-y-3 bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-soft">
            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">
                Team Name <span className="text-rose-500">*</span>
              </label>
              <input
                type="text"
                value={teamName}
                onChange={e => setTeamName(e.target.value)}
                placeholder="e.g. Team Golt / Nova Pioneers"
                className="w-full px-3 py-2.5 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:ring-2 focus:ring-bubble-sage focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">
                Short Description
              </label>
              <textarea
                value={teamDescription}
                onChange={e => setTeamDescription(e.target.value)}
                placeholder="e.g. A motivated group building AI-assisted submission tools..."
                rows={3}
                className="w-full p-3 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:ring-2 focus:ring-bubble-sage focus:outline-none"
              />
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: PROBLEM STATEMENT & IDEA */}
      {currentStep === 3 && (
        <div className="space-y-4 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Problem Statement & Idea</h3>
            <p className="text-xs text-bubble-muted">
              Used by HackBubble's AI to match candidates who have relevant prior projects.
            </p>
          </div>

          <div className="space-y-3 bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-soft">
            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">
                Problem Statement <span className="text-rose-500">*</span>
              </label>
              <textarea
                value={problemStatement}
                onChange={e => setProblemStatement(e.target.value)}
                placeholder="Explain the user pain point or industry challenge your team is tackling..."
                rows={3}
                className="w-full p-3 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:ring-2 focus:ring-bubble-sage focus:outline-none"
              />
            </div>

            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">
                Proposed Solution / Project Idea (Optional)
              </label>
              <textarea
                value={projectIdea}
                onChange={e => setProjectIdea(e.target.value)}
                placeholder="High-level solution architecture or key features..."
                rows={2}
                className="w-full p-3 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium focus:ring-2 focus:ring-bubble-sage focus:outline-none"
              />
            </div>
          </div>
        </div>
      )}

      {/* STEP 4: TARGET SIZE & ROLES */}
      {currentStep === 4 && (
        <div className="space-y-4 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Team Size & Role Vacancies</h3>
            <p className="text-xs text-bubble-muted">
              Define the open seats so candidates can apply and match.
            </p>
          </div>

          {/* Target Size Counter */}
          <div className="p-3 bg-white rounded-2xl border border-bubble-cream-border flex items-center justify-between">
            <div>
              <span className="text-xs font-bold text-bubble-ink block">Target Total Team Size</span>
              <span className="text-[10px] text-stone-500">Including yourself as leader</span>
            </div>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setTargetSize(Math.max(2, targetSize - 1))}
                className="w-7 h-7 rounded-lg bg-stone-100 text-stone-700 font-bold hover:bg-stone-200"
              >
                -
              </button>
              <span className="text-sm font-black text-bubble-ink">{targetSize}</span>
              <button
                onClick={() => setTargetSize(Math.min(6, targetSize + 1))}
                className="w-7 h-7 rounded-lg bg-stone-100 text-stone-700 font-bold hover:bg-stone-200"
              >
                +
              </button>
            </div>
          </div>

          {/* Roles list */}
          <div className="space-y-2">
            {roles.map((role, idx) => (
              <div
                key={role.id}
                className="p-3.5 bg-white rounded-2xl border border-bubble-cream-border space-y-2 relative"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-bubble-ink">
                    Role #{idx + 1}: {role.title}
                  </span>
                  {roles.length > 1 && (
                    <button
                      onClick={() => handleRemoveRole(role.id)}
                      className="text-stone-400 hover:text-rose-500 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  )}
                </div>

                <div className="text-[11px] text-stone-500 space-y-1">
                  <div>
                    <strong>Must-have skills:</strong> {role.mustHaveSkills.join(', ')}
                  </div>
                  <div>
                    <strong>Experience:</strong> {role.experienceLevel}
                  </div>
                </div>
              </div>
            ))}

            <button
              onClick={handleAddRole}
              className="w-full py-2.5 border-2 border-dashed border-bubble-cream-border rounded-2xl text-xs font-bold text-bubble-sage-deep hover:bg-white flex items-center justify-center gap-1.5 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>Add Another Role Vacancy</span>
            </button>
          </div>
        </div>
      )}

      {/* STEP 5: WORKING STYLE & PREFERENCES */}
      {currentStep === 5 && (
        <div className="space-y-4 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Working Style & Preferences</h3>
            <p className="text-xs text-bubble-muted">
              Help teammates understand your team culture and meeting expectations.
            </p>
          </div>

          <div className="space-y-3 bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-soft">
            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">Time Commitment</label>
              <select
                value={preferences.timeCommitment}
                onChange={e => setPreferences({ ...preferences, timeCommitment: e.target.value })}
                className="w-full p-2.5 rounded-xl border border-bubble-cream-border bg-stone-50 text-xs font-medium text-bubble-ink"
              >
                <option>Weekend (20-30 hours)</option>
                <option>High Intensity (~35+ hours)</option>
                <option>Moderate / Part-time (10-15 hours)</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-bold text-bubble-ink block mb-1">Meeting Frequency</label>
              <select
                value={preferences.meetingFrequency}
                onChange={e => setPreferences({ ...preferences, meetingFrequency: e.target.value })}
                className="w-full p-2.5 rounded-xl border border-bubble-cream-border bg-stone-50 text-xs font-medium text-bubble-ink"
              >
                <option>Daily standup at 10:00 GMT</option>
                <option>Twice daily syncs</option>
                <option>Asynchronous updates via Discord/Slack</option>
              </select>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div>
                <span className="text-xs font-bold text-bubble-ink block">Beginner Friendly</span>
                <span className="text-[10px] text-stone-500">Open to mentorship and students</span>
              </div>
              <input
                type="checkbox"
                checked={preferences.beginnerFriendly}
                onChange={e => setPreferences({ ...preferences, beginnerFriendly: e.target.checked })}
                className="w-4 h-4 rounded text-bubble-sage-deep focus:ring-bubble-sage"
              />
            </div>
          </div>
        </div>
      )}

      {/* STEP 6: REVIEW & PUBLISH */}
      {currentStep === 6 && (
        <div className="space-y-4 animate-in fade-in">
          <div className="space-y-1">
            <h3 className="text-base font-black text-bubble-ink">Review & Publish Team</h3>
            <p className="text-xs text-bubble-muted">
              Confirm your team parameters before publishing to HackBubble discovery.
            </p>
          </div>

          <div className="bg-white p-4 rounded-3xl border border-bubble-cream-border shadow-soft space-y-3">
            <div>
              <span className="text-[10px] font-bold uppercase text-bubble-muted block">Hackathon</span>
              <strong className="text-xs text-bubble-ink">{selectedHackathon.title}</strong>
            </div>

            <div>
              <span className="text-[10px] font-bold uppercase text-bubble-muted block">Team Name</span>
              <strong className="text-xs text-bubble-ink">{teamName || 'Team Golt'}</strong>
            </div>

            <div>
              <span className="text-[10px] font-bold uppercase text-bubble-muted block">Problem Statement</span>
              <p className="text-xs text-stone-600 leading-relaxed">
                {problemStatement || 'Building AI submission tools for developers.'}
              </p>
            </div>

            <div>
              <span className="text-[10px] font-bold uppercase text-bubble-muted block">Vacancies</span>
              <div className="flex gap-1.5 flex-wrap pt-1">
                {roles.map(r => (
                  <span
                    key={r.id}
                    className="px-2 py-0.5 rounded-lg bg-bubble-sage-light text-bubble-sage-deep text-[11px] font-bold"
                  >
                    {r.title} ({r.vacancies})
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Step Actions */}
      <div className="flex items-center gap-2 pt-2">
        {currentStep > 1 && (
          <button
            onClick={() => setCurrentStep(currentStep - 1)}
            className="py-3 px-4 rounded-2xl border border-bubble-cream-border bg-white text-xs font-bold text-stone-700 hover:bg-stone-50 flex items-center gap-1.5 shadow-sm"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back</span>
          </button>
        )}

        {currentStep < 6 ? (
          <button
            onClick={() => setCurrentStep(currentStep + 1)}
            className="flex-1 py-3 px-4 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md flex items-center justify-center gap-1.5 transition-all"
          >
            <span>Continue</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        ) : (
          <button
            onClick={handlePublish}
            className="flex-1 py-3 px-4 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md flex items-center justify-center gap-1.5 transition-all"
          >
            <Sparkles className="w-3.5 h-3.5 text-bubble-pink" />
            <span>Publish Team to Discovery</span>
          </button>
        )}
      </div>
    </div>
  );
};
