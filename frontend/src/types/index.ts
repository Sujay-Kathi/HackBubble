export type HackathonMode = 'online' | 'offline' | 'hybrid';
export type HackathonStatus = 'registration_open' | 'upcoming' | 'ongoing' | 'closed';

export interface HackathonMaterial {
  id: string;
  group: 'Official info' | 'Documents' | 'Design assets';
  title: string;
  type: 'pdf' | 'docx' | 'fig' | 'zip';
  size: string;
  updatedAt: string;
}

export interface HackathonTimelineItem {
  id: string;
  title: string;
  time: string;
  type: 'mentor_call' | 'workshop' | 'deadline' | 'submission';
  completed?: boolean;
}

export interface HackathonEvaluation {
  projectName: string;
  teamName: string;
  description: string;
  demoUrl: string;
  githubUrl: string;
  pitchDeckUrl: string;
  demoVideoUrl: string;
  ratings: {
    idea: number;
    execution: number;
    design: number;
    presentation: number;
  };
  feedback: string;
  submitted: boolean;
}

export interface Hackathon {
  id: string;
  title: string;
  organizer: string;
  description: string;
  mode: HackathonMode;
  location?: string;
  startDate: string;
  endDate: string;
  registrationDeadline: string;
  daysLeft: number;
  prizePool: string;
  themes: string[];
  teamSizeLimit: string;
  sourceName: string;
  sourceUrl: string;
  isSaved?: boolean;
  status: HackathonStatus;
  materials: HackathonMaterial[];
  timeline: HackathonTimelineItem[];
  evaluation?: HackathonEvaluation;
}

export interface Candidate {
  id: string;
  name: string;
  role: string;
  avatar: string;
  bio: string;
  college?: string;
  location?: string;
  matchScore: number;
  matchExplanation: string;
  matchedSkills: string[];
  preferredSkills: string[];
  otherSkills: string[];
  projects: {
    title: string;
    description: string;
    tech: string[];
    link?: string;
  }[];
  experience: {
    role: string;
    org: string;
    period: string;
  }[];
  education: string;
  portfolioUrl?: string;
  githubUrl?: string;
  linkedinUrl?: string;
}

export interface TeamRole {
  id: string;
  title: string;
  vacancies: number;
  filledCount: number;
  mustHaveSkills: string[];
  preferredSkills: string[];
  experienceLevel: 'Beginner-friendly' | 'Some experience' | 'Experienced' | 'Any';
  priority: 'Must fill' | 'Nice to have';
}

export interface TeamMember {
  id: string;
  userId: string;
  name: string;
  role: string;
  avatar: string;
  isLeader?: boolean;
  joinedAt: string;
}

export interface TeamPreference {
  timeCommitment: string;
  collaborationStyle: string;
  meetingFrequency: string;
  beginnerFriendly: boolean;
}

export interface Team {
  id: string;
  hackathonId: string;
  hackathonTitle: string;
  name: string;
  description: string;
  problemStatement: string;
  idea?: string;
  leaderId: string;
  leaderName: string;
  leaderRole: string;
  leaderAvatar: string;
  targetSize: number;
  currentSize: number;
  status: 'open' | 'paused' | 'full' | 'closed';
  roles: TeamRole[];
  preferences: TeamPreference;
  members: TeamMember[];
  inviteCode?: string;
}

export interface TeamApplication {
  id: string;
  teamId: string;
  teamName: string;
  hackathonTitle: string;
  roleId: string;
  roleTitle: string;
  applicantId: string;
  applicantName: string;
  applicantAvatar: string;
  message?: string;
  status: 'submitted' | 'under_review' | 'shortlisted' | 'accepted' | 'declined' | 'rejected' | 'finalized' | 'withdrawn';
  createdAt: string;
}

export interface TeamInvitation {
  id: string;
  teamId: string;
  teamName: string;
  hackathonTitle: string;
  roleTitle: string;
  leaderName: string;
  leaderAvatar: string;
  candidateId: string;
  candidateName: string;
  status: 'pending' | 'accepted' | 'declined' | 'finalized';
  createdAt: string;
}

export interface AppNotification {
  id: string;
  type: 'invitation' | 'application' | 'acceptance' | 'finalized' | 'reminder';
  title: string;
  message: string;
  time: string;
  read: boolean;
  targetTab?: 'my-teams' | 'discover' | 'home';
  targetId?: string;
}

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  avatar: string;
  bio: string;
  college: string;
  location: string;
  domains: string[];
  skills: { name: string; proficiency: 'Beginner' | 'Intermediate' | 'Advanced'; verified: boolean }[];
  portfolioUrl?: string;
  githubUrl?: string;
  linkedinUrl?: string;
  resumeFileName?: string;
  resumeParseStatus?: 'idle' | 'uploading' | 'parsing' | 'review' | 'confirmed';
}
