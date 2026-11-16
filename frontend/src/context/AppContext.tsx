import React, { createContext, useContext, useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import {
  Hackathon,
  Candidate,
  Team,
  TeamApplication,
  TeamInvitation,
  AppNotification,
  UserProfile,
} from '../types';
import {
  initialHackathons,
  initialCandidates,
  initialTeams,
  initialApplications,
  initialInvitations,
  initialNotifications,
  initialUserProfile,
} from '../data/mockData';

interface AppContextType {
  // Navigation & View
  activeTab: 'home' | 'discover' | 'create' | 'my-teams' | 'profile';
  setActiveTab: (tab: 'home' | 'discover' | 'create' | 'my-teams' | 'profile') => void;
  selectedHackathonId: string | null;
  setSelectedHackathonId: (id: string | null) => void;
  selectedTeamId: string | null;
  setSelectedTeamId: (id: string | null) => void;
  screeningTeamId: string;
  setScreeningTeamId: (id: string) => void;
  isMobileFrame: boolean;
  setIsMobileFrame: (val: boolean) => void;
  authModalOpen: boolean;
  setAuthModalOpen: (val: boolean) => void;
  notificationDrawerOpen: boolean;
  setNotificationDrawerOpen: (val: boolean) => void;

  // Hackathons
  hackathons: Hackathon[];
  toggleBookmark: (id: string) => void;
  selectedHackathon: Hackathon | undefined;

  // Candidate Screening & Swiping
  activeCandidates: Candidate[];
  passedCandidates: Candidate[];
  interestedCandidates: Candidate[];
  currentCandidateIndex: number;
  swipeCandidate: (candidateId: string, direction: 'pass' | 'interested') => void;
  revisitPassedCandidates: () => void;

  // Teams & Finalization
  teams: Team[];
  createTeam: (teamData: Partial<Team>) => string;
  finalizeTeam: (teamId: string, selectedCandidateIds: string[]) => boolean;
  selectedTeam: Team | undefined;

  // Applications & Invitations
  applications: TeamApplication[];
  applyToRole: (teamId: string, roleId: string, message: string) => void;
  withdrawApplication: (appId: string) => void;
  invitations: TeamInvitation[];
  respondToInvitation: (invId: string, accept: boolean) => void;

  // Notifications
  notifications: AppNotification[];
  unreadNotifCount: number;
  markNotifAsRead: (id: string) => void;
  markAllNotifsAsRead: () => void;

  // User Profile & Resume
  userProfile: UserProfile;
  updateUserProfile: (data: Partial<UserProfile>) => void;
  uploadResumeMock: (file: File) => Promise<void>;
  confirmResumeMock: () => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Navigation & Shell
  const [activeTab, setActiveTab] = useState<'home' | 'discover' | 'create' | 'my-teams' | 'profile'>('home');
  const [selectedHackathonId, setSelectedHackathonId] = useState<string | null>(null);
  const [selectedTeamId, setSelectedTeamId] = useState<string | null>(null);
  const [screeningTeamId, setScreeningTeamId] = useState<string>('team-golt');
  const [isMobileFrame, setIsMobileFrame] = useState<boolean>(true);
  const [authModalOpen, setAuthModalOpen] = useState<boolean>(false);
  const [notificationDrawerOpen, setNotificationDrawerOpen] = useState<boolean>(false);

  // Data states with localStorage persistence
  const [hackathons, setHackathons] = useState<Hackathon[]>(() => {
    const saved = localStorage.getItem('hb_hackathons');
    return saved ? JSON.parse(saved) : initialHackathons;
  });

  const [activeCandidates, setActiveCandidates] = useState<Candidate[]>(() => {
    const saved = localStorage.getItem('hb_active_candidates');
    return saved ? JSON.parse(saved) : initialCandidates;
  });

  const [passedCandidates, setPassedCandidates] = useState<Candidate[]>(() => {
    const saved = localStorage.getItem('hb_passed_candidates');
    return saved ? JSON.parse(saved) : [];
  });

  const [interestedCandidates, setInterestedCandidates] = useState<Candidate[]>(() => {
    const saved = localStorage.getItem('hb_interested_candidates');
    return saved ? JSON.parse(saved) : [];
  });

  const [currentCandidateIndex, setCurrentCandidateIndex] = useState<number>(0);

  const [teams, setTeams] = useState<Team[]>(() => {
    const saved = localStorage.getItem('hb_teams');
    return saved ? JSON.parse(saved) : initialTeams;
  });

  const [applications, setApplications] = useState<TeamApplication[]>(() => {
    const saved = localStorage.getItem('hb_applications');
    return saved ? JSON.parse(saved) : initialApplications;
  });

  const [invitations, setInvitations] = useState<TeamInvitation[]>(() => {
    const saved = localStorage.getItem('hb_invitations');
    return saved ? JSON.parse(saved) : initialInvitations;
  });

  const [notifications, setNotifications] = useState<AppNotification[]>(() => {
    const saved = localStorage.getItem('hb_notifications');
    return saved ? JSON.parse(saved) : initialNotifications;
  });

  const [userProfile, setUserProfile] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('hb_user_profile');
    return saved ? JSON.parse(saved) : initialUserProfile;
  });

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem('hb_hackathons', JSON.stringify(hackathons));
  }, [hackathons]);

  useEffect(() => {
    localStorage.setItem('hb_active_candidates', JSON.stringify(activeCandidates));
    localStorage.setItem('hb_passed_candidates', JSON.stringify(passedCandidates));
    localStorage.setItem('hb_interested_candidates', JSON.stringify(interestedCandidates));
  }, [activeCandidates, passedCandidates, interestedCandidates]);

  useEffect(() => {
    localStorage.setItem('hb_teams', JSON.stringify(teams));
  }, [teams]);

  useEffect(() => {
    localStorage.setItem('hb_applications', JSON.stringify(applications));
  }, [applications]);

  useEffect(() => {
    localStorage.setItem('hb_invitations', JSON.stringify(invitations));
  }, [invitations]);

  useEffect(() => {
    localStorage.setItem('hb_notifications', JSON.stringify(notifications));
  }, [notifications]);

  useEffect(() => {
    localStorage.setItem('hb_user_profile', JSON.stringify(userProfile));
  }, [userProfile]);

  // Hackathon actions
  const toggleBookmark = (id: string) => {
    setHackathons(prev =>
      prev.map(h => (h.id === id ? { ...h, isSaved: !h.isSaved } : h))
    );
  };

  const selectedHackathon = hackathons.find(h => h.id === selectedHackathonId);
  const selectedTeam = teams.find(t => t.id === selectedTeamId);

  // Swiping Actions
  const swipeCandidate = (candidateId: string, direction: 'pass' | 'interested') => {
    const candidate = activeCandidates.find(c => c.id === candidateId);
    if (!candidate) return;

    if (direction === 'pass') {
      setPassedCandidates(prev => [...prev, candidate]);
    } else {
      setInterestedCandidates(prev => [...prev, candidate]);

      // Add to team's invited record & create notification
      const team = teams.find(t => t.id === screeningTeamId);
      const teamTitle = team ? team.name : 'Team Golt';

      const newNotif: AppNotification = {
        id: `notif-${Date.now()}`,
        type: 'invitation',
        title: 'Invitation Sent',
        message: `You expressed interest in ${candidate.name} for ${teamTitle}. Awaiting their response.`,
        time: 'Just now',
        read: false,
        targetTab: 'my-teams',
      };
      setNotifications(prev => [newNotif, ...prev]);
    }

    // Remove from active deck
    setActiveCandidates(prev => prev.filter(c => c.id !== candidateId));
  };

  // Revisit passed candidates (multi-pass screening)
  const revisitPassedCandidates = () => {
    if (passedCandidates.length === 0) return;
    setActiveCandidates(passedCandidates);
    setPassedCandidates([]);
    setCurrentCandidateIndex(0);
  };

  // Team creation
  const createTeam = (teamData: Partial<Team>): string => {
    const newId = `team-${Date.now()}`;
    const newTeam: Team = {
      id: newId,
      hackathonId: teamData.hackathonId || hackathons[0].id,
      hackathonTitle: teamData.hackathonTitle || hackathons[0].title,
      name: teamData.name || 'New Team',
      description: teamData.description || '',
      problemStatement: teamData.problemStatement || '',
      idea: teamData.idea || '',
      leaderId: userProfile.id,
      leaderName: userProfile.name,
      leaderRole: 'Team Leader',
      leaderAvatar: userProfile.avatar,
      targetSize: teamData.targetSize || 4,
      currentSize: 1,
      status: 'open',
      inviteCode: `hackathons.app/team-${Math.floor(1000 + Math.random() * 9000)}`,
      roles: teamData.roles || [],
      preferences: teamData.preferences || {
        timeCommitment: 'Weekend (20-30 hours)',
        collaborationStyle: 'Collaborative with voice & PRs',
        meetingFrequency: 'Daily standup',
        beginnerFriendly: true,
      },
      members: [
        {
          id: `m-${Date.now()}`,
          userId: userProfile.id,
          name: userProfile.name,
          role: 'Team Leader',
          avatar: userProfile.avatar,
          isLeader: true,
          joinedAt: new Date().toISOString().split('T')[0],
        }
      ],
    };

    setTeams(prev => [newTeam, ...prev]);

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'finalized',
      title: 'Team Created & Published',
      message: `Your team "${newTeam.name}" is now recruiting candidates for ${newTeam.hackathonTitle}.`,
      time: 'Just now',
      read: false,
      targetTab: 'my-teams',
      targetId: newId,
    };
    setNotifications(prev => [notif, ...prev]);

    return newId;
  };

  // Finalize Team (Pessimistic capacity check & celebratory confetti)
  const finalizeTeam = (teamId: string, selectedCandidateIds: string[]): boolean => {
    const team = teams.find(t => t.id === teamId);
    if (!team) return false;

    // Check capacity: current members + newly selected candidates cannot exceed target size
    if (team.currentSize + selectedCandidateIds.length > team.targetSize) {
      alert(`Cannot finalize: Selection exceeds team target capacity of ${team.targetSize} members.`);
      return false;
    }

    const newMembers = selectedCandidateIds.map(candId => {
      const candidate = initialCandidates.find(c => c.id === candId);
      return {
        id: `mem-${Date.now()}-${candId}`,
        userId: candId,
        name: candidate ? candidate.name : 'New Member',
        role: candidate ? candidate.role : 'Member',
        avatar: candidate ? candidate.avatar : '/avatars/alex.jpg',
        isLeader: false,
        joinedAt: new Date().toISOString().split('T')[0],
      };
    });

    const updatedSize = team.currentSize + newMembers.length;
    const isFull = updatedSize >= team.targetSize;

    setTeams(prev =>
      prev.map(t =>
        t.id === teamId
          ? {
              ...t,
              members: [...t.members, ...newMembers],
              currentSize: updatedSize,
              status: isFull ? 'full' : 'open',
            }
          : t
      )
    );

    // Fire celebratory confetti!
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 },
      colors: ['#BDCEB8', '#6D8A6B', '#F6E5EB', '#EF4444', '#FCF9F3']
    });

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'finalized',
      title: '🎉 Team Roster Finalized!',
      message: `Official membership confirmed for ${newMembers.length} candidate(s) in "${team.name}". Team status: ${isFull ? 'FULL' : 'OPEN'}.`,
      time: 'Just now',
      read: false,
      targetTab: 'my-teams',
      targetId: teamId,
    };
    setNotifications(prev => [notif, ...prev]);

    return true;
  };

  // Participant application
  const applyToRole = (teamId: string, roleId: string, message: string) => {
    const team = teams.find(t => t.id === teamId);
    if (!team) return;
    const role = team.roles.find(r => r.id === roleId);

    const newApp: TeamApplication = {
      id: `app-${Date.now()}`,
      teamId,
      teamName: team.name,
      hackathonTitle: team.hackathonTitle,
      roleId,
      roleTitle: role ? role.title : 'Member',
      applicantId: userProfile.id,
      applicantName: userProfile.name,
      applicantAvatar: userProfile.avatar,
      message,
      status: 'submitted',
      createdAt: new Date().toISOString(),
    };

    setApplications(prev => [newApp, ...prev]);

    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'application',
      title: 'Application Submitted',
      message: `You applied to join "${team.name}" as ${role?.title}. The team leader will review your profile.`,
      time: 'Just now',
      read: false,
      targetTab: 'my-teams',
    };
    setNotifications(prev => [notif, ...prev]);
  };

  const withdrawApplication = (appId: string) => {
    setApplications(prev =>
      prev.map(a => (a.id === appId ? { ...a, status: 'withdrawn' } : a))
    );
  };

  // Invitation responses
  const respondToInvitation = (invId: string, accept: boolean) => {
    setInvitations(prev =>
      prev.map(i =>
        i.id === invId ? { ...i, status: accept ? 'accepted' : 'declined' } : i
      )
    );

    const inv = invitations.find(i => i.id === invId);
    const notif: AppNotification = {
      id: `notif-${Date.now()}`,
      type: 'acceptance',
      title: accept ? 'Invitation Accepted' : 'Invitation Declined',
      message: accept
        ? `You accepted the invitation to "${inv?.teamName}". You are now awaiting final team finalization by the leader.`
        : `You declined the invitation to "${inv?.teamName}".`,
      time: 'Just now',
      read: false,
      targetTab: 'my-teams',
    };
    setNotifications(prev => [notif, ...prev]);
  };

  // Notifications
  const unreadNotifCount = notifications.filter(n => !n.read).length;

  const markNotifAsRead = (id: string) => {
    setNotifications(prev =>
      prev.map(n => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllNotifsAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  // Profile & Resume Mock
  const updateUserProfile = (data: Partial<UserProfile>) => {
    setUserProfile(prev => ({ ...prev, ...data }));
  };

  const uploadResumeMock = async (file: File) => {
    setUserProfile(prev => ({
      ...prev,
      resumeFileName: file.name,
      resumeParseStatus: 'uploading',
    }));

    // Simulate async PyMuPDF + LLM extraction pipeline
    setTimeout(() => {
      setUserProfile(prev => ({ ...prev, resumeParseStatus: 'parsing' }));
      setTimeout(() => {
        setUserProfile(prev => ({
          ...prev,
          resumeParseStatus: 'review',
          bio: prev.bio || 'Passionate software engineer with hands-on experience in full-stack web applications, AI APIs, and developer toolchains.',
        }));
      }, 1500);
    }, 1200);
  };

  const confirmResumeMock = () => {
    setUserProfile(prev => ({
      ...prev,
      resumeParseStatus: 'confirmed',
    }));
  };

  return (
    <AppContext.Provider
      value={{
        activeTab,
        setActiveTab,
        selectedHackathonId,
        setSelectedHackathonId,
        selectedTeamId,
        setSelectedTeamId,
        screeningTeamId,
        setScreeningTeamId,
        isMobileFrame,
        setIsMobileFrame,
        authModalOpen,
        setAuthModalOpen,
        notificationDrawerOpen,
        setNotificationDrawerOpen,
        hackathons,
        toggleBookmark,
        selectedHackathon,
        activeCandidates,
        passedCandidates,
        interestedCandidates,
        currentCandidateIndex,
        swipeCandidate,
        revisitPassedCandidates,
        teams,
        createTeam,
        finalizeTeam,
        selectedTeam,
        applications,
        applyToRole,
        withdrawApplication,
        invitations,
        respondToInvitation,
        notifications,
        unreadNotifCount,
        markNotifAsRead,
        markAllNotifsAsRead,
        userProfile,
        updateUserProfile,
        uploadResumeMock,
        confirmResumeMock,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
