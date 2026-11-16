import React, { useState } from 'react';
import {
  X,
  Bookmark,
  Calendar,
  MapPin,
  ExternalLink,
  Users,
  Award,
  Clock,
  FileText,
  Paperclip,
  CheckCircle2,
  Star,
  Plus,
  Share2,
  Globe,
} from 'lucide-react';
import { useApp } from '../context/AppContext';

export const HackathonDetailModal: React.FC = () => {
  const {
    selectedHackathon,
    setSelectedHackathonId,
    toggleBookmark,
    setActiveTab,
    setSelectedTeamId,
  } = useApp();

  const [activeSubTab, setActiveSubTab] = useState<'timeline' | 'materials' | 'evaluation'>('timeline');
  const [evalRatings, setEvalRatings] = useState({
    idea: selectedHackathon?.evaluation?.ratings.idea || 4,
    execution: selectedHackathon?.evaluation?.ratings.execution || 5,
    design: selectedHackathon?.evaluation?.ratings.design || 4,
    presentation: selectedHackathon?.evaluation?.ratings.presentation || 5,
  });
  const [feedback, setFeedback] = useState(selectedHackathon?.evaluation?.feedback || '');
  const [submittedEval, setSubmittedEval] = useState(selectedHackathon?.evaluation?.submitted || false);
  const [showAddMaterial, setShowAddMaterial] = useState(false);

  if (!selectedHackathon) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4">
      <div className="bg-bubble-cream w-full max-w-lg max-h-[92vh] rounded-[32px] border border-bubble-cream-border flex flex-col shadow-2xl relative overflow-hidden animate-in fade-in zoom-in-95 duration-200">
        {/* Sticky Header */}
        <div className="p-4 border-b border-bubble-cream-border bg-white flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-bubble-sage-light text-bubble-sage-deep">
              {selectedHackathon.mode}
            </span>
            <span className="text-xs text-bubble-muted font-medium">
              Source: <strong className="text-bubble-ink">{selectedHackathon.sourceName}</strong>
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => toggleBookmark(selectedHackathon.id)}
              className={`p-2 rounded-full border transition-colors ${
                selectedHackathon.isSaved
                  ? 'bg-bubble-pink border-bubble-pink-border text-bubble-heart'
                  : 'bg-stone-50 border-stone-200 text-stone-500 hover:text-bubble-ink'
              }`}
              title={selectedHackathon.isSaved ? "Saved" : "Save hackathon"}
            >
              <Bookmark className={`w-4 h-4 ${selectedHackathon.isSaved ? 'fill-bubble-heart' : ''}`} />
            </button>
            <button
              onClick={() => setSelectedHackathonId(null)}
              className="p-1.5 rounded-full hover:bg-stone-100 text-stone-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Hero Details */}
          <div className="space-y-2">
            <h1 className="text-xl font-black text-bubble-ink tracking-tight">
              {selectedHackathon.title}
            </h1>
            <p className="text-xs text-bubble-muted font-medium">
              Organized by <span className="text-bubble-sage-deep font-bold">{selectedHackathon.organizer}</span>
            </p>
            <p className="text-xs text-stone-600 leading-relaxed pt-1">
              {selectedHackathon.description}
            </p>
          </div>

          {/* Quick Metrics Bar */}
          <div className="grid grid-cols-3 gap-2 p-3 bg-white rounded-2xl border border-bubble-cream-border shadow-soft text-center">
            <div>
              <span className="text-[10px] text-bubble-muted font-semibold block">Prize Pool</span>
              <span className="text-xs font-black text-bubble-sage-deep">{selectedHackathon.prizePool}</span>
            </div>
            <div className="border-x border-bubble-cream-border">
              <span className="text-[10px] text-bubble-muted font-semibold block">Team Limit</span>
              <span className="text-xs font-bold text-bubble-ink">{selectedHackathon.teamSizeLimit}</span>
            </div>
            <div>
              <span className="text-[10px] text-bubble-muted font-semibold block">Deadline</span>
              <span className="text-xs font-bold text-bubble-heart">{selectedHackathon.daysLeft} days left</span>
            </div>
          </div>

          {/* Sub-Tabs (ShipIt Wireframe: Timeline / Materials / Results) */}
          <div className="flex items-center p-1 bg-white rounded-2xl border border-bubble-cream-border shadow-sm">
            <button
              onClick={() => setActiveSubTab('timeline')}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
                activeSubTab === 'timeline'
                  ? 'bg-bubble-sage-deep text-white shadow-sm'
                  : 'text-bubble-muted hover:text-bubble-ink'
              }`}
            >
              Timeline
            </button>
            <button
              onClick={() => setActiveSubTab('materials')}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
                activeSubTab === 'materials'
                  ? 'bg-bubble-sage-deep text-white shadow-sm'
                  : 'text-bubble-muted hover:text-bubble-ink'
              }`}
            >
              Materials ({selectedHackathon.materials.length})
            </button>
            <button
              onClick={() => setActiveSubTab('evaluation')}
              className={`flex-1 py-2 text-xs font-bold rounded-xl transition-all ${
                activeSubTab === 'evaluation'
                  ? 'bg-bubble-sage-deep text-white shadow-sm'
                  : 'text-bubble-muted hover:text-bubble-ink'
              }`}
            >
              Evaluation
            </button>
          </div>

          {/* SUB-TAB 1: TIMELINE & UPCOMING SCHEDULE */}
          {activeSubTab === 'timeline' && (
            <div className="space-y-3">
              <h3 className="text-xs font-black uppercase tracking-wider text-bubble-muted">
                Today / Upcoming Schedule
              </h3>
              <div className="space-y-2">
                {selectedHackathon.timeline.map((item, idx) => (
                  <div
                    key={item.id}
                    className="p-3 bg-white rounded-2xl border border-bubble-cream-border flex items-start gap-3 shadow-soft"
                  >
                    <div className="w-8 h-8 rounded-xl bg-bubble-pink/60 text-bubble-ink flex items-center justify-center shrink-0 font-bold text-xs">
                      {idx + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-bubble-ink">{item.title}</span>
                        <span className="text-[10px] font-semibold text-bubble-sage-deep">{item.time}</span>
                      </div>
                      <p className="text-[10px] text-stone-400 capitalize mt-0.5">
                        Track: {item.type.replace('_', ' ')}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SUB-TAB 2: MATERIALS (ShipIt Wireframe 11 & 12) */}
          {activeSubTab === 'materials' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-black uppercase tracking-wider text-bubble-muted">
                  Official Info & Resources
                </h3>
                <button
                  onClick={() => setShowAddMaterial(!showAddMaterial)}
                  className="text-xs font-bold text-bubble-sage-deep flex items-center gap-1 hover:underline"
                >
                  <Plus className="w-3.5 h-3.5" />
                  <span>Add Material</span>
                </button>
              </div>

              {/* Add Material modal snippet */}
              {showAddMaterial && (
                <div className="p-3.5 bg-bubble-pink/30 rounded-2xl border border-bubble-pink-border space-y-2 animate-in fade-in">
                  <span className="text-xs font-bold text-bubble-ink block">Upload or Link New Material</span>
                  <div className="grid grid-cols-2 gap-2 pt-1">
                    <button
                      onClick={() => {
                        alert('File upload dialog opened: selected file will be added to team materials.');
                        setShowAddMaterial(false);
                      }}
                      className="py-2 px-3 bg-white rounded-xl border border-bubble-cream-border text-xs font-bold text-bubble-sage-deep hover:bg-stone-50"
                    >
                      📎 Upload file
                    </button>
                    <button
                      onClick={() => {
                        const url = prompt('Enter resource URL:');
                        if (url) alert('Link saved to materials.');
                        setShowAddMaterial(false);
                      }}
                      className="py-2 px-3 bg-white rounded-xl border border-bubble-cream-border text-xs font-bold text-bubble-sage-deep hover:bg-stone-50"
                    >
                      🔗 Add link
                    </button>
                  </div>
                </div>
              )}

              {/* Grouped materials list */}
              {['Official info', 'Documents', 'Design assets'].map(groupName => {
                const groupItems = selectedHackathon.materials.filter(m => m.group === groupName);
                if (groupItems.length === 0) return null;
                return (
                  <div key={groupName} className="space-y-1.5">
                    <h4 className="text-[11px] font-bold text-bubble-sage-deep">{groupName}</h4>
                    <div className="space-y-1.5">
                      {groupItems.map(item => (
                        <div
                          key={item.id}
                          className="p-2.5 bg-white rounded-xl border border-bubble-cream-border flex items-center justify-between hover:bg-stone-50 transition-colors"
                        >
                          <div className="flex items-center gap-2.5">
                            <div className="w-7 h-7 rounded-lg bg-stone-100 flex items-center justify-center text-[10px] font-bold uppercase text-stone-600">
                              {item.type}
                            </div>
                            <div>
                              <span className="text-xs font-bold text-bubble-ink block">{item.title}</span>
                              <span className="text-[10px] text-stone-400">{item.size} • {item.updatedAt}</span>
                            </div>
                          </div>
                          <span className="text-xs text-bubble-sage-deep font-bold">Download</span>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* SUB-TAB 3: EVALUATION & SUBMISSION RUBRIC (ShipIt Wireframe 7) */}
          {activeSubTab === 'evaluation' && (
            <div className="space-y-4">
              {selectedHackathon.evaluation ? (
                <div className="bg-white p-4 rounded-2xl border border-bubble-cream-border space-y-4 shadow-soft">
                  <div>
                    <span className="text-[10px] font-bold text-bubble-sage-deep uppercase tracking-wider block">
                      Project Submission Review
                    </span>
                    <h3 className="text-base font-black text-bubble-ink">
                      {selectedHackathon.evaluation.projectName}
                    </h3>
                    <p className="text-xs text-bubble-muted">
                      by <strong className="text-bubble-ink">{selectedHackathon.evaluation.teamName}</strong>
                    </p>
                    <p className="text-xs text-stone-600 mt-1 leading-relaxed">
                      {selectedHackathon.evaluation.description}
                    </p>
                  </div>

                  {/* Submission Links */}
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <a
                      href={selectedHackathon.evaluation.demoUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between text-bubble-sage-deep font-semibold"
                    >
                      <span>🌐 Live Demo</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    <a
                      href={selectedHackathon.evaluation.githubUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="p-2 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between text-bubble-sage-deep font-semibold"
                    >
                      <span>🐙 GitHub Repo</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>

                  {/* 5-Star Evaluation Rubric */}
                  <div className="space-y-2.5 pt-2 border-t border-bubble-cream-border">
                    <h4 className="text-xs font-black uppercase text-bubble-muted">Judge Rubric Scoring</h4>

                    {(['idea', 'execution', 'design', 'presentation'] as const).map(criteria => (
                      <div key={criteria} className="flex items-center justify-between">
                        <span className="text-xs font-semibold capitalize text-bubble-ink">{criteria}</span>
                        <div className="flex items-center gap-1">
                          {[1, 2, 3, 4, 5].map(star => (
                            <button
                              key={star}
                              onClick={() => setEvalRatings(prev => ({ ...prev, [criteria]: star }))}
                              className="p-0.5"
                            >
                              <Star
                                className={`w-4 h-4 transition-colors ${
                                  star <= evalRatings[criteria]
                                    ? 'fill-amber-400 text-amber-400'
                                    : 'text-stone-300'
                                }`}
                              />
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Feedback text */}
                  <div>
                    <label className="text-[11px] font-bold text-bubble-ink block mb-1">Feedback Comments</label>
                    <textarea
                      value={feedback}
                      onChange={e => setFeedback(e.target.value)}
                      placeholder="Add constructive notes on technical depth and UI polish..."
                      rows={2}
                      className="w-full p-2.5 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink focus:outline-none focus:ring-1 focus:ring-bubble-sage font-medium bg-stone-50"
                    />
                  </div>

                  <div className="flex items-center gap-2 pt-1">
                    <button
                      onClick={() => alert('Evaluation draft saved!')}
                      className="flex-1 py-2 rounded-xl border border-bubble-cream-border bg-stone-50 text-xs font-bold text-stone-700 hover:bg-stone-100"
                    >
                      Save draft
                    </button>
                    <button
                      onClick={() => {
                        setSubmittedEval(true);
                        alert('Evaluation scorecard submitted to organizers!');
                      }}
                      className="flex-1 py-2 rounded-xl bg-bubble-sage-deep text-white text-xs font-bold hover:bg-bubble-sage-dark shadow-sm"
                    >
                      {submittedEval ? 'Submitted ✓' : 'Submit Score'}
                    </button>
                  </div>
                </div>
              ) : (
                <div className="p-6 text-center text-bubble-muted bg-white rounded-2xl border border-bubble-cream-border">
                  <p className="text-xs font-medium">Evaluation rubric opens after project submission deadline.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Sticky Action Footer */}
        <div className="p-4 border-t border-bubble-cream-border bg-white flex flex-col sm:flex-row gap-2">
          <button
            onClick={() => {
              setSelectedHackathonId(null);
              setActiveTab('create');
            }}
            className="flex-1 py-3 px-4 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
          >
            <Users className="w-4 h-4" />
            <span>Create a team for this hackathon</span>
          </button>

          <a
            href={selectedHackathon.sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="py-3 px-4 rounded-2xl bg-bubble-pink hover:bg-bubble-pink-border text-bubble-ink font-bold text-xs flex items-center justify-center gap-1.5 transition-colors border border-bubble-pink-border"
          >
            <span>Register on {selectedHackathon.sourceName}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};
