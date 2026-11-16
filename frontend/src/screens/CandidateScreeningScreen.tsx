import React, { useState } from 'react';
import {
  Heart,
  HeartCrack,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  Award,
  ExternalLink,
  RotateCcw,
  BookOpen,
  Briefcase,
  GraduationCap,
  Users,
  CheckCircle2,
  Info,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Candidate } from '../types';

export const CandidateScreeningScreen: React.FC = () => {
  const {
    activeCandidates,
    passedCandidates,
    interestedCandidates,
    swipeCandidate,
    revisitPassedCandidates,
    screeningTeamId,
    teams,
    setActiveTab,
    setSelectedTeamId,
  } = useApp();

  const [expandedInfo, setExpandedInfo] = useState<boolean>(false);
  const [dragOffset, setDragOffset] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [swipeFeedback, setSwipeFeedback] = useState<'pass' | 'interested' | null>(null);

  const team = teams.find(t => t.id === screeningTeamId) || teams[0];
  const candidate = activeCandidates[0];

  // Drag / Touch handlers for gesture swiping
  const handleTouchStart = (e: React.TouchEvent | React.MouseEvent) => {
    setIsDragging(true);
  };

  const handleTouchMove = (clientX: number, startX: number) => {
    if (!isDragging) return;
    const diff = clientX - startX;
    setDragOffset(diff);
  };

  const handleAction = (direction: 'pass' | 'interested') => {
    if (!candidate) return;
    setSwipeFeedback(direction);
    setDragOffset(direction === 'pass' ? -350 : 350);

    setTimeout(() => {
      swipeCandidate(candidate.id, direction);
      setDragOffset(0);
      setSwipeFeedback(null);
      setExpandedInfo(false);
    }, 280);
  };

  // If no candidates remain in the active deck
  if (!candidate) {
    return (
      <div className="p-6 text-center space-y-5 bg-white rounded-3xl border border-bubble-cream-border shadow-soft m-4">
        <div className="w-16 h-16 mx-auto rounded-full bg-bubble-pink flex items-center justify-center">
          <Sparkles className="w-8 h-8 text-bubble-sage-deep" />
        </div>

        <div className="space-y-1">
          <h2 className="text-lg font-black text-bubble-ink">Screening Pass Complete!</h2>
          <p className="text-xs text-bubble-muted max-w-xs mx-auto">
            You've reviewed all available candidates for <strong className="text-bubble-ink">{team.name}</strong>.
          </p>
        </div>

        {/* Stats card */}
        <div className="grid grid-cols-2 gap-3 p-3 bg-bubble-cream rounded-2xl border border-bubble-cream-border text-center">
          <div>
            <span className="text-[10px] text-bubble-muted font-bold uppercase block">Interested / Shortlisted</span>
            <span className="text-base font-black text-bubble-sage-deep">{interestedCandidates.length}</span>
          </div>
          <div>
            <span className="text-[10px] text-bubble-muted font-bold uppercase block">Passed for this Pass</span>
            <span className="text-base font-black text-stone-500">{passedCandidates.length}</span>
          </div>
        </div>

        <div className="space-y-2 pt-2">
          {passedCandidates.length > 0 && (
            <button
              onClick={revisitPassedCandidates}
              className="w-full py-3 px-4 rounded-2xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs shadow-md flex items-center justify-center gap-2 transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Review Passed Candidates (Pass 2)</span>
            </button>
          )}

          <button
            onClick={() => {
              setSelectedTeamId(team.id);
              setActiveTab('my-teams');
            }}
            className="w-full py-3 px-4 rounded-2xl bg-bubble-pink hover:bg-bubble-pink-border text-bubble-ink font-bold text-xs border border-bubble-pink-border transition-colors"
          >
            Go to Team Workspace & Finalize Roster
          </button>
        </div>
      </div>
    );
  }

  // Calculate rotation and opacity for swipe cards
  const rotation = dragOffset * 0.08;
  const isPassThreshold = dragOffset < -80 || swipeFeedback === 'pass';
  const isInterestThreshold = dragOffset > 80 || swipeFeedback === 'interested';

  return (
    <div className="space-y-3 px-4 pt-1 pb-6">
      {/* Screening Header */}
      <div className="flex items-center justify-between px-1">
        <div>
          <span className="text-[10px] font-bold text-bubble-muted uppercase tracking-wider block">
            Leader Screening Deck
          </span>
          <span className="text-xs font-black text-bubble-ink">
            Recruiting for: <span className="text-bubble-sage-deep font-bold">{team.name}</span>
          </span>
        </div>
        <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-bubble-cream-dark text-bubble-muted">
          {activeCandidates.length} left
        </span>
      </div>

      {/* SWIPE CARD CONTAINER */}
      <div className="relative w-full min-h-[460px] max-h-[580px] flex items-center justify-center">
        {/* Underneath card illusion */}
        {activeCandidates[1] && (
          <div className="absolute inset-0 top-3 scale-[0.96] opacity-60 bg-white rounded-[32px] border border-bubble-cream-border shadow-card pointer-events-none -z-10"></div>
        )}

        {/* ACTIVE SWIPABLE CARD */}
        <div
          style={{
            transform: `translateX(${dragOffset}px) rotate(${rotation}deg)`,
            transition: isDragging ? 'none' : 'transform 0.28s ease-out',
          }}
          className="w-full bg-white rounded-[32px] border border-bubble-cream-border shadow-swipe overflow-hidden flex flex-col relative select-none cursor-grab active:cursor-grabbing"
        >
          {/* SWIPE FEEDBACK OVERLAYS (Matching User's Swiping Reference Image) */}
          {/* Left Swipe: Broken Heart badge */}
          <div
            className={`absolute top-6 left-6 z-30 p-3 rounded-full bg-white/95 border-2 border-stone-400 shadow-xl flex items-center justify-center transition-opacity duration-150 ${
              isPassThreshold ? 'opacity-100 scale-110' : 'opacity-0 scale-90'
            }`}
          >
            <HeartCrack className="w-10 h-10 text-stone-600 fill-stone-300" />
          </div>

          {/* Right Swipe: Red Heart badge + "Hi!" Speech Bubble */}
          <div
            className={`absolute top-6 right-6 z-30 flex items-center gap-2 transition-opacity duration-150 ${
              isInterestThreshold ? 'opacity-100 scale-110' : 'opacity-0 scale-90'
            }`}
          >
            <div className="px-3 py-1 rounded-2xl bg-white border border-rose-300 text-bubble-heart font-black text-sm shadow-md animate-bounce">
              Hi! 👋
            </div>
            <div className="p-3 rounded-full bg-white/95 border-2 border-bubble-heart shadow-xl flex items-center justify-center">
              <Heart className="w-10 h-10 text-bubble-heart fill-bubble-heart" />
            </div>
          </div>

          {/* Candidate Portrait Image */}
          <div className="relative h-64 w-full bg-stone-100 overflow-hidden">
            <img
              src={candidate.avatar}
              alt={candidate.name}
              className="w-full h-full object-cover object-top pointer-events-none"
            />
            {/* Gradient overlay for text legibility */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>

            {/* AI Match Pill */}
            <div className="absolute top-4 left-4 z-20 flex items-center gap-1.5 px-3 py-1 rounded-full bg-bubble-cream/90 backdrop-blur-md text-bubble-sage-deep font-black text-xs border border-white/60 shadow-sm">
              <Sparkles className="w-3.5 h-3.5 text-bubble-sage-dark" />
              <span>{candidate.matchScore}% Match</span>
            </div>

            {/* Candidate Title & Location */}
            <div className="absolute bottom-3 left-4 right-4 text-white z-20 space-y-0.5">
              <h2 className="text-xl font-black tracking-tight leading-tight">
                {candidate.name}
              </h2>
              <p className="text-xs font-semibold text-bubble-pink">
                {candidate.role}
              </p>
              <p className="text-[11px] text-stone-300 font-medium">
                {candidate.college} • {candidate.location}
              </p>
            </div>
          </div>

          {/* Card Details & AI Rationale */}
          <div className="p-4 space-y-3 overflow-y-auto max-h-[240px]">
            {/* AI Match Explanation */}
            <div className="p-2.5 rounded-2xl bg-bubble-sage-light/70 border border-bubble-sage-border/50 text-[11px] text-bubble-sage-deep leading-relaxed flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 text-bubble-sage-dark shrink-0 mt-0.5" />
              <div>
                <strong className="block text-bubble-ink font-bold">Why matched:</strong>
                {candidate.matchExplanation}
              </div>
            </div>

            {/* Skills Chips */}
            <div className="space-y-1.5">
              <span className="text-[10px] font-bold uppercase tracking-wider text-bubble-muted">
                Matched & Verified Skills
              </span>
              <div className="flex flex-wrap gap-1">
                {candidate.matchedSkills.map(skill => (
                  <span
                    key={skill}
                    className="px-2 py-0.5 rounded-lg bg-bubble-sage/40 text-bubble-sage-deep font-bold text-[10px] border border-bubble-sage"
                  >
                    ✓ {skill}
                  </span>
                ))}
                {candidate.preferredSkills.map(skill => (
                  <span
                    key={skill}
                    className="px-2 py-0.5 rounded-lg bg-bubble-pink text-bubble-ink font-semibold text-[10px]"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            {/* Bio summary */}
            <p className="text-xs text-stone-600 leading-relaxed">
              "{candidate.bio}"
            </p>

            {/* Expanded details (Projects & Experience) */}
            {expandedInfo && (
              <div className="space-y-3 pt-2 border-t border-bubble-cream-border animate-in fade-in">
                <div>
                  <span className="text-[10px] font-bold text-bubble-muted uppercase block mb-1">
                    Notable Project
                  </span>
                  {candidate.projects.map((proj, idx) => (
                    <div key={idx} className="p-2 bg-stone-50 rounded-xl border border-stone-200/70 text-xs space-y-1">
                      <div className="flex items-center justify-between">
                        <strong className="text-bubble-ink font-bold">{proj.title}</strong>
                        {proj.link && (
                          <a
                            href={proj.link}
                            target="_blank"
                            rel="noreferrer"
                            className="text-[10px] text-bubble-sage-deep font-bold flex items-center gap-0.5"
                          >
                            GitHub <ExternalLink className="w-2.5 h-2.5" />
                          </a>
                        )}
                      </div>
                      <p className="text-[11px] text-stone-600">{proj.description}</p>
                      <div className="flex gap-1 text-[9px] text-stone-400">
                        {proj.tech.join(' • ')}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="text-xs text-stone-500">
                  <strong>Education:</strong> {candidate.education}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SWIPE BUTTON BAR (Matching Image << and >> buttons) */}
      <div className="flex items-center justify-center gap-4 pt-2">
        {/* Left Reject / Pass Button (<<) */}
        <button
          onClick={() => handleAction('pass')}
          className="flex items-center gap-2 px-5 py-3 rounded-full bg-white border border-stone-300 text-stone-700 font-extrabold text-sm shadow-md hover:bg-stone-50 hover:scale-105 transition-all group"
          title="Pass / Reject candidate for this pass"
        >
          <span className="text-stone-400 group-hover:text-stone-700 font-black">{'<<'}</span>
          <HeartCrack className="w-5 h-5 text-stone-500" />
          <span>Pass</span>
        </button>

        {/* Expand Info Button */}
        <button
          onClick={() => setExpandedInfo(!expandedInfo)}
          className={`p-3 rounded-full border transition-all ${
            expandedInfo
              ? 'bg-bubble-sage-deep text-white border-bubble-sage-deep'
              : 'bg-white text-stone-600 border-bubble-cream-border hover:bg-stone-50'
          }`}
          title="Toggle Full Candidate Profile"
        >
          <Info className="w-5 h-5" />
        </button>

        {/* Right Like / Interested Button (>>) */}
        <button
          onClick={() => handleAction('interested')}
          className="flex items-center gap-2 px-5 py-3 rounded-full bg-bubble-heart text-white font-extrabold text-sm shadow-md hover:bg-rose-600 hover:scale-105 transition-all group"
          title="Express Interest / Send Invitation"
        >
          <span>Interested</span>
          <Heart className="w-5 h-5 fill-white" />
          <span className="text-rose-200 group-hover:text-white font-black">{'>>'}</span>
        </button>
      </div>

      <p className="text-[10px] text-center text-stone-400 pt-1">
        Tip: Swipe left/right on the card or click the buttons to review candidates.
      </p>
    </div>
  );
};
