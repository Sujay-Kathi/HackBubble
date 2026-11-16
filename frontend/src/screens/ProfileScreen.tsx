import React, { useState } from 'react';
import {
  User,
  Upload,
  FileText,
  Sparkles,
  CheckCircle2,
  ExternalLink,
  Edit2,
  Save,
  Shield,
  Layers,
  GraduationCap,
  MapPin,
  Clock,
} from 'lucide-react';
import { useApp } from '../context/AppContext';

export const ProfileScreen: React.FC = () => {
  const { userProfile, updateUserProfile, uploadResumeMock, confirmResumeMock } = useApp();

  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [name, setName] = useState<string>(userProfile.name);
  const [bio, setBio] = useState<string>(userProfile.bio);
  const [college, setCollege] = useState<string>(userProfile.college);
  const [location, setLocation] = useState<string>(userProfile.location);

  const handleSaveProfile = () => {
    updateUserProfile({ name, bio, college, location });
    setIsEditing(false);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadResumeMock(e.target.files[0]);
    }
  };

  return (
    <div className="flex-1 pb-24 px-4 pt-3 space-y-4">
      {/* Profile Header Card */}
      <div className="p-4 rounded-3xl bg-white border border-bubble-cream-border shadow-card space-y-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <img
              src={userProfile.avatar}
              alt={userProfile.name}
              className="w-14 h-14 rounded-3xl object-cover border-2 border-bubble-sage shadow-md"
            />
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="text-base font-black text-bubble-ink leading-tight">
                  {userProfile.name}
                </h1>
                <span className="p-0.5 rounded-full bg-bubble-sage-light text-bubble-sage-deep" title="Verified Profile">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                </span>
              </div>
              <p className="text-xs text-bubble-muted font-medium">{userProfile.email}</p>
              <p className="text-[11px] text-stone-500 flex items-center gap-1 mt-0.5">
                <MapPin className="w-3 h-3 text-stone-400" />
                <span>{userProfile.location}</span>
              </p>
            </div>
          </div>

          <button
            onClick={() => {
              if (isEditing) handleSaveProfile();
              else setIsEditing(true);
            }}
            className="p-2 rounded-2xl border border-bubble-cream-border text-stone-600 hover:bg-stone-50 transition-colors"
            title={isEditing ? 'Save Changes' : 'Edit Profile'}
          >
            {isEditing ? <Save className="w-4 h-4 text-bubble-sage-deep" /> : <Edit2 className="w-4 h-4" />}
          </button>
        </div>

        {/* Bio */}
        {isEditing ? (
          <div className="space-y-2 pt-2">
            <div>
              <label className="text-[10px] font-bold text-bubble-muted uppercase block">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={e => setName(e.target.value)}
                className="w-full px-3 py-1.5 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-bubble-muted uppercase block">Bio</label>
              <textarea
                value={bio}
                onChange={e => setBio(e.target.value)}
                rows={3}
                className="w-full p-2.5 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium"
              />
            </div>
            <div>
              <label className="text-[10px] font-bold text-bubble-muted uppercase block">College / University</label>
              <input
                type="text"
                value={college}
                onChange={e => setCollege(e.target.value)}
                className="w-full px-3 py-1.5 rounded-xl border border-bubble-cream-border text-xs text-bubble-ink font-medium"
              />
            </div>
            <button
              onClick={handleSaveProfile}
              className="py-1.5 px-4 rounded-xl bg-bubble-sage-deep text-white text-xs font-bold"
            >
              Save Profile
            </button>
          </div>
        ) : (
          <p className="text-xs text-stone-600 leading-relaxed pt-1">
            "{userProfile.bio}"
          </p>
        )}

        {/* Domains / Tags */}
        <div className="flex flex-wrap gap-1.5 pt-1">
          {userProfile.domains.map(d => (
            <span
              key={d}
              className="px-2.5 py-0.5 rounded-full bg-bubble-cream-dark text-bubble-ink font-semibold text-[10px]"
            >
              #{d}
            </span>
          ))}
        </div>
      </div>

      {/* RESUME UPLOAD & AI EXTRACTION PIPELINE (PRD FR-03 & SRS 5.1) */}
      <div className="p-4 rounded-3xl bg-white border border-bubble-cream-border shadow-card space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-xl bg-bubble-pink text-bubble-ink">
              <FileText className="w-4 h-4 text-bubble-sage-deep" />
            </div>
            <div>
              <h3 className="text-xs font-black text-bubble-ink">
                AI Resume Intelligence & Extraction
              </h3>
              <p className="text-[10px] text-bubble-muted">
                PyMuPDF OCR + Schema-constrained LLM Parser
              </p>
            </div>
          </div>

          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold capitalize ${
            userProfile.resumeParseStatus === 'confirmed'
              ? 'bg-emerald-100 text-emerald-800'
              : userProfile.resumeParseStatus === 'parsing'
              ? 'bg-amber-100 text-amber-800 animate-pulse'
              : 'bg-bubble-pink text-bubble-ink'
          }`}>
            {userProfile.resumeParseStatus || 'confirmed'}
          </span>
        </div>

        {/* Upload box */}
        <div className="p-4 rounded-2xl border-2 border-dashed border-bubble-cream-border bg-stone-50/60 text-center space-y-2 relative">
          <Upload className="w-6 h-6 text-bubble-sage-dark mx-auto" />
          <div>
            <span className="text-xs font-bold text-bubble-ink block">
              {userProfile.resumeFileName || 'Upload PDF Resume (Max 10MB)'}
            </span>
            <span className="text-[10px] text-stone-400">
              Extracts skills, project experience, and generates grounded vectors
            </span>
          </div>

          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileChange}
            className="absolute inset-0 opacity-0 cursor-pointer"
          />
        </div>

        {/* Processing State Simulator */}
        {userProfile.resumeParseStatus === 'uploading' && (
          <div className="p-3 rounded-2xl bg-bubble-pink/30 border border-bubble-pink-border flex items-center gap-2 text-xs font-medium text-bubble-ink">
            <span className="w-2 h-2 rounded-full bg-bubble-sage-deep animate-ping"></span>
            <span>Uploading file to secure private storage...</span>
          </div>
        )}

        {userProfile.resumeParseStatus === 'parsing' && (
          <div className="p-3 rounded-2xl bg-amber-50 border border-amber-200 flex items-center gap-2 text-xs font-medium text-amber-900">
            <Sparkles className="w-4 h-4 text-amber-600 animate-spin" />
            <span>Running OCR text recovery & LLM structured schema validation...</span>
          </div>
        )}

        {/* Review Parsed Draft State (PRD FR-03 Human Verification requirement) */}
        {userProfile.resumeParseStatus === 'review' && (
          <div className="p-3.5 rounded-2xl bg-bubble-sage-light/70 border border-bubble-sage-border space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-bubble-sage-deep flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-bubble-sage-dark" />
                <span>Extracted Profile Draft</span>
              </span>
              <span className="text-[10px] font-bold text-amber-700 bg-amber-100 px-2 py-0.5 rounded-full">
                Review Required
              </span>
            </div>

            <p className="text-[11px] text-stone-600">
              Extracted 5 verified skills and summary. Review and confirm to mark verified.
            </p>

            <div className="flex gap-2 pt-1">
              <button
                onClick={confirmResumeMock}
                className="flex-1 py-2 rounded-xl bg-bubble-sage-deep hover:bg-bubble-sage-dark text-white text-xs font-bold shadow-sm"
              >
                Confirm Extracted Details ✓
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Verified Skills */}
      <div className="p-4 rounded-3xl bg-white border border-bubble-cream-border shadow-card space-y-2.5">
        <h3 className="text-xs font-black uppercase tracking-wider text-bubble-muted">
          Verified Skill Vector Profile
        </h3>

        <div className="flex flex-wrap gap-1.5">
          {userProfile.skills.map(skill => (
            <div
              key={skill.name}
              className="px-3 py-1 rounded-xl bg-bubble-sage-light text-bubble-sage-deep font-bold text-xs flex items-center gap-1.5 border border-bubble-sage-border/60"
            >
              <span>{skill.name}</span>
              <span className="text-[9px] text-stone-500 font-medium">({skill.proficiency})</span>
            </div>
          ))}
        </div>
      </div>

      {/* External Links */}
      <div className="p-4 rounded-3xl bg-white border border-bubble-cream-border shadow-card space-y-2">
        <h3 className="text-xs font-black uppercase tracking-wider text-bubble-muted">
          Public Portfolios & Links
        </h3>

        <div className="space-y-1.5 text-xs">
          {userProfile.githubUrl && (
            <a
              href={userProfile.githubUrl}
              target="_blank"
              rel="noreferrer"
              className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between text-bubble-sage-deep font-bold"
            >
              <span>🐙 GitHub Profile</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          {userProfile.linkedinUrl && (
            <a
              href={userProfile.linkedinUrl}
              target="_blank"
              rel="noreferrer"
              className="p-2.5 rounded-xl bg-stone-50 border border-stone-200 flex items-center justify-between text-bubble-sage-deep font-bold"
            >
              <span>💼 LinkedIn Profile</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
};
