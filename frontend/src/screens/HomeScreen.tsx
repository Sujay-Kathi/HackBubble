import React, { useState } from 'react';
import {
  Search,
  SlidersHorizontal,
  Bookmark,
  Calendar,
  Globe,
  MapPin,
  Users,
  Clock,
  Sparkles,
  ArrowRight,
  X,
  Check,
} from 'lucide-react';
import { useApp } from '../context/AppContext';
import { Hackathon } from '../types';

export const HomeScreen: React.FC = () => {
  const {
    hackathons,
    toggleBookmark,
    setSelectedHackathonId,
    setActiveTab,
  } = useApp();

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [onlySaved, setOnlySaved] = useState<boolean>(false);
  const [showFilterModal, setShowFilterModal] = useState<boolean>(false);

  // Filters state (ShipIt Wireframe 5)
  const [filterFormat, setFilterFormat] = useState<'All' | 'Online' | 'Offline'>('All');
  const [filterWorkStyle, setFilterWorkStyle] = useState<'Both' | 'Team' | 'Solo'>('Both');

  const categories = ['All', 'Programming', 'Design', 'Analytics', 'AI/ML', 'Fullstack'];

  const filteredHackathons = hackathons.filter(h => {
    if (onlySaved && !h.isSaved) return false;
    if (selectedCategory !== 'All' && !h.themes.includes(selectedCategory)) return false;
    if (filterFormat !== 'All' && h.mode.toLowerCase() !== filterFormat.toLowerCase()) return false;
    if (searchQuery.trim() !== '') {
      const q = searchQuery.toLowerCase();
      const matchTitle = h.title.toLowerCase().includes(q);
      const matchOrg = h.organizer.toLowerCase().includes(q);
      const matchTheme = h.themes.some(t => t.toLowerCase().includes(q));
      if (!matchTitle && !matchOrg && !matchTheme) return false;
    }
    return true;
  });

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Hero Welcome / Value Proposition Banner */}
      <div className="p-4 rounded-3xl bg-gradient-to-r from-bubble-pink via-bubble-pink-light to-bubble-sage-light border border-bubble-pink-border/60 shadow-soft relative overflow-hidden">
        <div className="relative z-10 space-y-1">
          <div className="flex items-center gap-1.5 text-xs font-bold text-bubble-sage-deep">
            <Sparkles className="w-4 h-4 text-bubble-sage-dark" />
            <span>Welcome to HackBubble</span>
          </div>
          <h2 className="text-lg font-black text-bubble-ink tracking-tight">
            Start your Career & Build Teams
          </h2>
          <p className="text-xs text-bubble-muted max-w-[280px]">
            Explore verified hackathons, match with complementary teammates, and ship together.
          </p>

          <div className="pt-2 flex items-center gap-2">
            <button
              onClick={() => setActiveTab('discover')}
              className="py-1.5 px-3 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white font-bold text-xs flex items-center gap-1 shadow-sm transition-all"
            >
              <span>Join a Team</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setActiveTab('create')}
              className="py-1.5 px-3 rounded-xl bg-white text-bubble-ink font-bold text-xs border border-bubble-cream-border hover:bg-stone-50 transition-colors"
            >
              Create Team
            </button>
          </div>
        </div>

        {/* Decorative circular shapes */}
        <div className="absolute -right-6 -bottom-8 w-28 h-28 rounded-full bg-bubble-sage/30 blur-xl pointer-events-none"></div>
      </div>

      {/* Search Bar & Action Buttons (ShipIt Wireframe 4) */}
      <div className="flex items-center gap-2">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-stone-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search by title, skill or city..."
            className="w-full pl-9 pr-8 py-2.5 rounded-2xl bg-white border border-bubble-cream-border text-xs text-bubble-ink font-medium placeholder-stone-400 focus:outline-none focus:ring-2 focus:ring-bubble-sage shadow-soft transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-2.5 text-stone-400 hover:text-stone-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Filter button */}
        <button
          onClick={() => setShowFilterModal(true)}
          className={`p-2.5 rounded-2xl border transition-colors shadow-soft ${
            filterFormat !== 'All' || filterWorkStyle !== 'Both'
              ? 'bg-bubble-sage-deep text-white border-bubble-sage-deep'
              : 'bg-white text-stone-600 border-bubble-cream-border hover:bg-stone-50'
          }`}
          title="Open filters"
        >
          <SlidersHorizontal className="w-4 h-4" />
        </button>

        {/* Saved filter toggle */}
        <button
          onClick={() => setOnlySaved(!onlySaved)}
          className={`p-2.5 rounded-2xl border transition-colors shadow-soft ${
            onlySaved
              ? 'bg-bubble-pink text-bubble-heart border-bubble-pink-border'
              : 'bg-white text-stone-600 border-bubble-cream-border hover:bg-stone-50'
          }`}
          title={onlySaved ? "Show all" : "Show saved only"}
        >
          <Bookmark className={`w-4 h-4 ${onlySaved ? 'fill-bubble-heart' : ''}`} />
        </button>
      </div>

      {/* Horizontal Category Chips */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all ${
              selectedCategory === cat
                ? 'bg-bubble-sage-deep text-white shadow-sm scale-105'
                : 'bg-white text-bubble-muted hover:text-bubble-ink border border-bubble-cream-border'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Hackathon Feed Cards */}
      <div className="space-y-3.5">
        <div className="flex items-center justify-between px-1">
          <span className="text-xs font-black uppercase tracking-wider text-bubble-muted">
            {onlySaved ? 'Saved Hackathons' : 'Active & Upcoming Events'} ({filteredHackathons.length})
          </span>
          <span className="text-[11px] font-semibold text-bubble-sage-deep">
            Verified listings
          </span>
        </div>

        {filteredHackathons.length === 0 ? (
          <div className="p-8 text-center bg-white rounded-3xl border border-bubble-cream-border space-y-2">
            <p className="text-xs font-bold text-bubble-ink">No hackathons match your filter</p>
            <p className="text-[11px] text-bubble-muted">Try clearing the search query or adjusting your filters.</p>
            <button
              onClick={() => {
                setSearchQuery('');
                setSelectedCategory('All');
                setOnlySaved(false);
                setFilterFormat('All');
              }}
              className="mt-2 py-1.5 px-3 bg-bubble-sage-light text-bubble-sage-deep text-xs font-bold rounded-xl"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          filteredHackathons.map(h => (
            <div
              key={h.id}
              onClick={() => setSelectedHackathonId(h.id)}
              className="bg-white rounded-3xl p-4 border border-bubble-cream-border shadow-card hover:shadow-swipe transition-all cursor-pointer group space-y-3"
            >
              {/* Card Header */}
              <div className="flex items-start justify-between gap-2">
                <div>
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-bubble-sage-light text-bubble-sage-deep">
                      {h.mode}
                    </span>
                    <span className="text-[10px] text-stone-400 font-medium">
                      Source: {h.sourceName}
                    </span>
                  </div>
                  <h3 className="text-base font-black text-bubble-ink group-hover:text-bubble-sage-deep transition-colors leading-snug">
                    {h.title}
                  </h3>
                  <p className="text-xs text-bubble-muted">{h.organizer}</p>
                </div>

                {/* Bookmark Icon Button */}
                <button
                  onClick={e => {
                    e.stopPropagation();
                    toggleBookmark(h.id);
                  }}
                  className={`p-2 rounded-2xl border transition-colors ${
                    h.isSaved
                      ? 'bg-bubble-pink border-bubble-pink-border text-bubble-heart'
                      : 'bg-stone-50 border-stone-200 text-stone-400 hover:text-stone-600'
                  }`}
                >
                  <Bookmark className={`w-4 h-4 ${h.isSaved ? 'fill-bubble-heart' : ''}`} />
                </button>
              </div>

              {/* Tag Chips (Matching Wireframe: UX/UI, Free, Online, 2-4 Members, 3 days left) */}
              <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                <span className="px-2.5 py-1 rounded-xl bg-bubble-cream-dark text-bubble-ink font-semibold">
                  🏆 {h.prizePool}
                </span>
                <span className="px-2.5 py-1 rounded-xl bg-bubble-cream-dark text-bubble-ink font-semibold">
                  👥 {h.teamSizeLimit}
                </span>
                <span className="px-2.5 py-1 rounded-xl bg-bubble-pink/60 text-bubble-ink font-bold">
                  ⏳ {h.daysLeft} days left
                </span>
                {h.themes.slice(0, 2).map(tag => (
                  <span
                    key={tag}
                    className="px-2 py-1 rounded-xl bg-stone-100 text-stone-600 font-medium text-[10px]"
                  >
                    #{tag}
                  </span>
                ))}
              </div>

              {/* Footer row */}
              <div className="pt-2 border-t border-bubble-cream-border/70 flex items-center justify-between text-xs">
                <span className="text-[11px] font-semibold text-bubble-sage-deep">
                  View Timeline & Materials →
                </span>
                <span className="text-[10px] text-stone-400 font-medium">
                  Registration Open
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* FILTER BOTTOM SHEET / MODAL (ShipIt Wireframe 5) */}
      {showFilterModal && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4">
          <div className="bg-bubble-cream w-full max-w-sm rounded-t-[32px] sm:rounded-[32px] border border-bubble-cream-border p-5 shadow-2xl space-y-4 animate-in slide-in-from-bottom duration-200">
            <div className="flex items-center justify-between pb-2 border-b border-bubble-cream-border">
              <h3 className="text-base font-black text-bubble-ink">Filters</h3>
              <button
                onClick={() => setShowFilterModal(false)}
                className="p-1 rounded-full hover:bg-stone-200/60 text-stone-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Format: Online, Offline, All */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-bubble-ink block">Format / Mode</label>
              <div className="grid grid-cols-3 gap-2">
                {(['All', 'Online', 'Offline'] as const).map(fmt => (
                  <button
                    key={fmt}
                    onClick={() => setFilterFormat(fmt)}
                    className={`py-2 text-xs font-bold rounded-xl border transition-colors ${
                      filterFormat === fmt
                        ? 'bg-bubble-sage-deep text-white border-bubble-sage-deep'
                        : 'bg-white border-bubble-cream-border text-bubble-muted hover:text-bubble-ink'
                    }`}
                  >
                    {fmt}
                  </button>
                ))}
              </div>
            </div>

            {/* Work style: Team, Solo, Both */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-bubble-ink block">Work Style</label>
              <div className="grid grid-cols-3 gap-2">
                {(['Both', 'Team', 'Solo'] as const).map(style => (
                  <button
                    key={style}
                    onClick={() => setFilterWorkStyle(style)}
                    className={`py-2 text-xs font-bold rounded-xl border transition-colors ${
                      filterWorkStyle === style
                        ? 'bg-bubble-sage-deep text-white border-bubble-sage-deep'
                        : 'bg-white border-bubble-cream-border text-bubble-muted hover:text-bubble-ink'
                    }`}
                  >
                    {style}
                  </button>
                ))}
              </div>
            </div>

            {/* Actions: Clear all & Show results */}
            <div className="pt-2 flex items-center gap-2">
              <button
                onClick={() => {
                  setFilterFormat('All');
                  setFilterWorkStyle('Both');
                }}
                className="flex-1 py-2.5 rounded-xl border border-bubble-cream-border bg-stone-100 hover:bg-stone-200 text-xs font-bold text-stone-700"
              >
                Clear all
              </button>
              <button
                onClick={() => setShowFilterModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white text-xs font-bold shadow-md"
              >
                Show results
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
