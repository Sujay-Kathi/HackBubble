import { Hackathon, Candidate, Team, TeamApplication, TeamInvitation, AppNotification, UserProfile } from '../types';

export const initialHackathons: Hackathon[] = [
  {
    id: 'h-shipit-2026',
    title: 'ShipIt Sprint 2026',
    organizer: 'ShipIt Foundation & Devfolio',
    description: 'A global 48-hour builder sprint focused on shipping full-stack apps, AI agents, and product design prototypes that solve real community challenges.',
    mode: 'online',
    startDate: '2026-11-20',
    endDate: '2026-11-22',
    registrationDeadline: '2026-11-19',
    daysLeft: 3,
    prizePool: '$25,000',
    themes: ['Programming', 'Design', 'AI Agents', 'Fullstack'],
    teamSizeLimit: '2-4 Members',
    sourceName: 'Devfolio',
    sourceUrl: 'https://devfolio.co/shipit-sprint-2026',
    isSaved: true,
    status: 'registration_open',
    timeline: [
      { id: 't1', title: 'Registration Deadline', time: 'Nov 19, 23:59 GMT', type: 'deadline' },
      { id: 't2', title: 'Mentor call - Team Ideation', time: 'Today 18:00 GMT', type: 'mentor_call' },
      { id: 't3', title: 'Workshop - Rapid UI Prototyping', time: 'Tomorrow 19:00 GMT', type: 'workshop' },
      { id: 't4', title: 'Submission draft deadline', time: 'Nov 22, 16:00 GMT', type: 'submission' },
    ],
    materials: [
      { id: 'm1', group: 'Official info', title: 'Hackathon Rules', type: 'pdf', size: '2.1 MB', updatedAt: '2d ago' },
      { id: 'm2', group: 'Official info', title: 'Submission Guide', type: 'pdf', size: '4.1 MB', updatedAt: '2d ago' },
      { id: 'm3', group: 'Official info', title: 'Judging Criteria', type: 'pdf', size: '1.0 MB', updatedAt: '2d ago' },
      { id: 'm4', group: 'Documents', title: 'Project template.docx', type: 'docx', size: '320 KB', updatedAt: '3d ago' },
      { id: 'm5', group: 'Documents', title: 'Branding pack.zip', type: 'zip', size: '50 MB', updatedAt: '3d ago' },
      { id: 'm6', group: 'Design assets', title: 'Figma KIT.fig', type: 'fig', size: 'Shared 2d ago', updatedAt: '2d ago' },
      { id: 'm7', group: 'Design assets', title: 'Logo pack.zip', type: 'zip', size: '19 MB', updatedAt: '2d ago' },
    ],
    evaluation: {
      projectName: 'StudyFlow',
      teamName: 'Team Nova',
      description: 'StudyFlow is a student-focused platform that helps users find hackathons, connect with teammates, and organize project work in one place.',
      demoUrl: 'https://studyflow-demo.app',
      githubUrl: 'https://github.com/studyflow/shipit',
      pitchDeckUrl: 'https://pitch.com/studyflow-deck',
      demoVideoUrl: 'https://youtube.com/watch?v=mockdemo',
      ratings: {
        idea: 4,
        execution: 5,
        design: 4,
        presentation: 5,
      },
      feedback: 'Great UX and crisp two-sided team matchmaking. Solid problem statement addressing hackathon team fragmentation.',
      submitted: true,
    }
  },
  {
    id: 'h-ai-agents',
    title: 'AI Vision & Agents Arena',
    organizer: 'OpenSource AI Labs',
    description: 'Build autonomous multimodal agents, intelligent decision workflows, and agentic UI interfaces using state-of-the-art LLMs.',
    mode: 'hybrid',
    location: 'San Francisco & Online',
    startDate: '2026-12-05',
    endDate: '2026-12-08',
    registrationDeadline: '2026-12-01',
    daysLeft: 14,
    prizePool: '$40,000',
    themes: ['AI/ML', 'Programming', 'Analytics', 'Agents'],
    teamSizeLimit: '3-5 Members',
    sourceName: 'Unstop',
    sourceUrl: 'https://unstop.com/hackathons/ai-vision-arena',
    isSaved: false,
    status: 'registration_open',
    timeline: [
      { id: 't2-1', title: 'Hackathon Kickoff', time: 'Dec 05, 10:00 PST', type: 'workshop' },
      { id: 't2-2', title: 'Final Pitching Round', time: 'Dec 08, 14:00 PST', type: 'submission' },
    ],
    materials: [
      { id: 'm2-1', group: 'Official info', title: 'API Access Keys Guide', type: 'pdf', size: '1.8 MB', updatedAt: '1w ago' },
      { id: 'm2-2', group: 'Design assets', title: 'Agent UI Kit', type: 'fig', size: 'Shared 1w ago', updatedAt: '1w ago' },
    ],
  },
  {
    id: 'h-green-sprint',
    title: 'GreenTech Sustainability Sprint',
    organizer: 'Climate Innovators Hub',
    description: 'Harness IoT, sensor telemetry, and clean computing dashboards to address urban carbon footprints and circular energy systems.',
    mode: 'offline',
    location: 'Bengaluru Innovation Center',
    startDate: '2026-12-15',
    endDate: '2026-12-17',
    registrationDeadline: '2026-12-10',
    daysLeft: 24,
    prizePool: '$15,000',
    themes: ['Hardware/IoT', 'Design', 'Data'],
    teamSizeLimit: '2-4 Members',
    sourceName: 'Devpost',
    sourceUrl: 'https://devpost.com/greentech-sprint',
    isSaved: false,
    status: 'upcoming',
    timeline: [
      { id: 't3-1', title: 'Hardware Kit Distribution', time: 'Dec 15, 09:00 IST', type: 'workshop' },
    ],
    materials: [
      { id: 'm3-1', group: 'Official info', title: 'Hardware Spec Sheet', type: 'pdf', size: '3.2 MB', updatedAt: '5d ago' },
    ],
  }
];

export const initialCandidates: Candidate[] = [
  {
    id: 'c-alex',
    name: 'Alex Rivera',
    role: 'Fullstack & Cloud Developer',
    avatar: '/avatars/alex.jpg',
    bio: 'Passionate about building resilient web apps with FastAPI, React, and cloud serverless. Winner of 2 international hackathons.',
    college: 'Stanford University (CS Junior)',
    location: 'San Francisco, CA',
    matchScore: 96,
    matchExplanation: 'Direct skill overlap in React & FastAPI backend; proven hackathon track record with 2 wins.',
    matchedSkills: ['React', 'TypeScript', 'FastAPI', 'PostgreSQL'],
    preferredSkills: ['Tailwind CSS', 'Docker', 'AWS'],
    otherSkills: ['GraphQL', 'Redis', 'CI/CD'],
    projects: [
      {
        title: 'NexusSync',
        description: 'Real-time collaborative markdown editor with CRDT and WebSocket synchronization.',
        tech: ['React', 'WebSockets', 'FastAPI', 'Redis'],
        link: 'https://github.com/alexr/nexussync',
      },
      {
        title: 'PulseTelemetry',
        description: 'Serverless event streaming dashboard processing 10k metrics/sec.',
        tech: ['AWS Lambda', 'TimescaleDB', 'React'],
      }
    ],
    experience: [
      { role: 'Software Engineering Intern', org: 'Cloudflare', period: 'Summer 2026' },
      { role: 'Fullstack Lead', org: 'Stanford Hackers Club', period: '2025 - Present' }
    ],
    education: 'B.S. in Computer Science, Stanford University',
    githubUrl: 'https://github.com/alexrivera',
    linkedinUrl: 'https://linkedin.com/in/alexrivera-dev',
  },
  {
    id: 'c-chen',
    name: 'Chen Wei',
    role: 'AI/ML & LLM Engineer',
    avatar: '/avatars/chen.jpg',
    bio: 'Specializing in prompt grounding, vector embeddings (pgvector/Pinecone), and LLM structured extraction pipelines.',
    college: 'UC Berkeley',
    location: 'Berkeley, CA',
    matchScore: 94,
    matchExplanation: 'Excellent alignment with problem statement AI requirements and semantic search capabilities.',
    matchedSkills: ['Python', 'PyTorch', 'FastAPI', 'Vector DBs'],
    preferredSkills: ['LangChain', 'pgvector', 'HuggingFace'],
    otherSkills: ['NumPy', 'Pandas', 'Docker'],
    projects: [
      {
        title: 'DocuQuery AI',
        description: 'Context-grounded OCR and question answering agent for legal contracts.',
        tech: ['PyMuPDF', 'all-MiniLM-L6-v2', 'FastAPI'],
      }
    ],
    experience: [
      { role: 'Research Assistant', org: 'Berkeley AI Research (BAIR)', period: '2025 - 2026' }
    ],
    education: 'M.S. in Electrical Engineering & Computer Science, UC Berkeley',
    githubUrl: 'https://github.com/chenwei-ai',
    linkedinUrl: 'https://linkedin.com/in/chenwei-ml',
  },
  {
    id: 'c-priya',
    name: 'Priya Sharma',
    role: 'Lead Frontend & UI/UX Developer',
    avatar: '/avatars/priya.jpg',
    bio: 'Design engineer creating crisp, accessible, and high-fidelity user experiences. Translates complex UX wireframes into clean code.',
    college: 'Carnegie Mellon University',
    location: 'Pittsburgh, PA',
    matchScore: 92,
    matchExplanation: 'Matches all UI/UX and mobile-first design specifications with rich React & Tailwind experience.',
    matchedSkills: ['React', 'TypeScript', 'Tailwind CSS', 'Figma'],
    preferredSkills: ['Next.js', 'Framer Motion', 'Accessibility (WCAG)'],
    otherSkills: ['Storybook', 'HTML5/CSS3', 'Jest'],
    projects: [
      {
        title: 'ShipIt Wireframe System',
        description: 'Comprehensive design system token library with 40+ responsive touch-friendly components.',
        tech: ['Figma', 'React', 'Tailwind CSS'],
      }
    ],
    experience: [
      { role: 'Product Design Intern', org: 'Notion', period: 'Summer 2026' }
    ],
    education: 'B.Des & HCI, Carnegie Mellon University',
    githubUrl: 'https://github.com/priyasharma-ux',
    linkedinUrl: 'https://linkedin.com/in/priya-sharma-design',
  },
  {
    id: 'c-maya',
    name: 'Maya Jenkins',
    role: 'Backend & Systems Architect',
    avatar: '/avatars/maya.jpg',
    bio: 'Dedicated to high-throughput REST APIs, database index optimization, and concurrency-safe transactional workflows.',
    college: 'Georgia Tech',
    location: 'Atlanta, GA',
    matchScore: 89,
    matchExplanation: 'Strong experience in database locking mechanisms and asynchronous task workers.',
    matchedSkills: ['Python', 'PostgreSQL', 'Docker', 'FastAPI'],
    preferredSkills: ['Redis', 'Alembic', 'SQLAlchemy'],
    otherSkills: ['Kubernetes', 'Go', 'Linux'],
    projects: [
      {
        title: 'LockGuard',
        description: 'Pessimistic concurrency locker testbed simulating high contention seat bookings.',
        tech: ['Python', 'PostgreSQL', 'Locust'],
      }
    ],
    experience: [
      { role: 'Backend Intern', org: 'Stripe', period: '2025' }
    ],
    education: 'B.S. in Computer Engineering, Georgia Tech',
    githubUrl: 'https://github.com/mayajenkins',
    linkedinUrl: 'https://linkedin.com/in/mayajenkins',
  },
  {
    id: 'c-nia',
    name: 'Nia Adebayo',
    role: 'Product Designer & Research Lead',
    avatar: '/avatars/nia.jpg',
    bio: 'Fusing empathetic user research with sleek aesthetics. Led team pitch and presentation in 3 top-tier hackathons.',
    college: 'Columbia University',
    location: 'New York, NY',
    matchScore: 88,
    matchExplanation: 'Brings strong product presentation, user journey mapping, and collaborative design leadership.',
    matchedSkills: ['Figma', 'User Research', 'Pitching', 'Prototyping'],
    preferredSkills: ['Design Systems', 'Design Sprint', 'Copywriting'],
    otherSkills: ['Illustrator', 'Video Editing', 'Miro'],
    projects: [
      {
        title: 'EcoTrack UX',
        description: 'Gamified carbon footprint tracker that won 1st Place at SustainHack 2025.',
        tech: ['Figma', 'User Testing'],
      }
    ],
    experience: [
      { role: 'Lead Designer', org: 'Columbia Tech Review', period: '2024 - 2026' }
    ],
    education: 'B.A. in Visual Arts & Information Science, Columbia University',
    linkedinUrl: 'https://linkedin.com/in/nia-adebayo',
  },
  {
    id: 'c-rohan',
    name: 'Rohan Patel',
    role: 'Mobile & Flutter Engineer',
    avatar: '/avatars/rohan.jpg',
    bio: 'Passionate mobile developer with experience in responsive touch gestures, offline caching, and cross-platform native plugins.',
    college: 'University of Illinois Urbana-Champaign',
    location: 'Chicago, IL',
    matchScore: 87,
    matchExplanation: 'Experienced in mobile card gesture interactions, push notifications, and local offline state.',
    matchedSkills: ['Flutter', 'Dart', 'Mobile UI', 'REST APIs'],
    preferredSkills: ['Firebase', 'State Management', 'Android/iOS'],
    otherSkills: ['Kotlin', 'Swift', 'Git'],
    projects: [
      {
        title: 'CardSwipe Engine',
        description: 'Performant card physics and swipe threshold gesture library for touch devices.',
        tech: ['Dart', 'Flutter', 'Canvas'],
      }
    ],
    experience: [
      { role: 'Mobile App Developer', org: 'Freelance', period: '2024 - Present' }
    ],
    education: 'B.S. in Computer Science, UIUC',
    githubUrl: 'https://github.com/rohanpatel-dev',
  }
];

export const initialTeams: Team[] = [
  {
    id: 'team-golt',
    hackathonId: 'h-shipit-2026',
    hackathonTitle: 'ShipIt Sprint 2026',
    name: 'Team Golt',
    description: 'Building an AI-assisted hackathon submission and evaluation workspace for judges and builders.',
    problemStatement: 'Hackathon participants struggle with disparate communication channels and messy team formation, while judges lack standard rubric evaluation tools.',
    idea: 'A unified portal combining instant team matching with integrated judging evaluation rubrics.',
    leaderId: 'u-current',
    leaderName: 'Oleksandr Kuzmak',
    leaderRole: 'Leader • Frontend Dev',
    leaderAvatar: '/avatars/alex.jpg',
    targetSize: 4,
    currentSize: 2,
    status: 'open',
    inviteCode: 'hackathons.app/golt-2026',
    roles: [
      {
        id: 'r1',
        title: 'Backend Developer',
        vacancies: 1,
        filledCount: 0,
        mustHaveSkills: ['FastAPI', 'PostgreSQL', 'Python'],
        preferredSkills: ['Docker', 'pgvector'],
        experienceLevel: 'Some experience',
        priority: 'Must fill',
      },
      {
        id: 'r2',
        title: 'UI/UX Designer',
        vacancies: 1,
        filledCount: 0,
        mustHaveSkills: ['Figma', 'Mobile UI'],
        preferredSkills: ['Design Systems', 'Prototyping'],
        experienceLevel: 'Any',
        priority: 'Must fill',
      }
    ],
    preferences: {
      timeCommitment: 'Full weekend (25-30 hours)',
      collaborationStyle: 'Active voice chat & shared repo',
      meetingFrequency: 'Daily standup at 10:00 GMT',
      beginnerFriendly: true,
    },
    members: [
      {
        id: 'm-1',
        userId: 'u-current',
        name: 'Oleksandr Kuzmak',
        role: 'Leader • Frontend Dev',
        avatar: '/avatars/alex.jpg',
        isLeader: true,
        joinedAt: '2026-11-15'
      },
      {
        id: 'm-2',
        userId: 'u-skakun',
        name: 'Oleksandr Skakun',
        role: 'Designer • PM',
        avatar: '/avatars/priya.jpg',
        isLeader: false,
        joinedAt: '2026-11-16'
      }
    ]
  },
  {
    id: 'team-visionarius',
    hackathonId: 'h-ai-agents',
    hackathonTitle: 'AI Vision & Agents Arena',
    name: 'AI Visionarius',
    description: 'Developing autonomous research agents with recursive verification loops.',
    problemStatement: 'Large language models produce hallucinated citations; we are building an agentic fact-checker with real-time web grounding.',
    leaderId: 'u-chen',
    leaderName: 'Chen Wei',
    leaderRole: 'Leader • AI Lead',
    leaderAvatar: '/avatars/chen.jpg',
    targetSize: 4,
    currentSize: 2,
    status: 'open',
    inviteCode: 'hackathons.app/visionarius',
    roles: [
      {
        id: 'r-vis-1',
        title: 'Frontend Dev',
        vacancies: 1,
        filledCount: 0,
        mustHaveSkills: ['React', 'TypeScript', 'Tailwind CSS'],
        preferredSkills: ['Data Visualizations', 'Streaming UI'],
        experienceLevel: 'Some experience',
        priority: 'Must fill',
      },
      {
        id: 'r-vis-2',
        title: 'Product Mgr',
        vacancies: 1,
        filledCount: 0,
        mustHaveSkills: ['Pitching', 'Slide Deck'],
        preferredSkills: ['Product Strategy'],
        experienceLevel: 'Any',
        priority: 'Nice to have',
      }
    ],
    preferences: {
      timeCommitment: 'High intensity (~35 hrs)',
      collaborationStyle: 'Async PR reviews + Discord',
      meetingFrequency: 'Twice daily',
      beginnerFriendly: false,
    },
    members: [
      {
        id: 'm-v1',
        userId: 'u-chen',
        name: 'Chen Wei',
        role: 'Leader • AI Lead',
        avatar: '/avatars/chen.jpg',
        isLeader: true,
        joinedAt: '2026-11-14'
      },
      {
        id: 'm-v2',
        userId: 'u-maya',
        name: 'Maya Jenkins',
        role: 'Backend Architect',
        avatar: '/avatars/maya.jpg',
        isLeader: false,
        joinedAt: '2026-11-15'
      }
    ]
  }
];

export const initialApplications: TeamApplication[] = [
  {
    id: 'app-1',
    teamId: 'team-visionarius',
    teamName: 'AI Visionarius',
    hackathonTitle: 'AI Vision & Agents Arena',
    roleId: 'r-vis-1',
    roleTitle: 'Frontend Dev',
    applicantId: 'u-current',
    applicantName: 'Oleksandr Kuzmak',
    applicantAvatar: '/avatars/alex.jpg',
    message: 'I have deep expertise building reactive streaming UI for generative AI agents. Would love to join!',
    status: 'under_review',
    createdAt: '2026-11-16T09:30:00Z',
  }
];

export const initialInvitations: TeamInvitation[] = [
  {
    id: 'inv-1',
    teamId: 'team-visionarius',
    teamName: 'AI Visionarius',
    hackathonTitle: 'AI Vision & Agents Arena',
    roleTitle: 'Frontend Lead',
    leaderName: 'Chen Wei',
    leaderAvatar: '/avatars/chen.jpg',
    candidateId: 'u-current',
    candidateName: 'Oleksandr Kuzmak',
    status: 'pending',
    createdAt: '2026-11-16T11:00:00Z',
  }
];

export const initialNotifications: AppNotification[] = [
  {
    id: 'notif-1',
    type: 'invitation',
    title: 'New Team Invitation',
    message: 'Chen Wei invited you to join "AI Visionarius" as Frontend Lead.',
    time: '20m ago',
    read: false,
    targetTab: 'my-teams',
    targetId: 'inv-1',
  },
  {
    id: 'notif-2',
    type: 'application',
    title: 'Candidate Accepted Invitation',
    message: 'Priya Sharma accepted your invitation for UI/UX Designer in Team Golt! Ready for finalization.',
    time: '1h ago',
    read: false,
    targetTab: 'my-teams',
    targetId: 'team-golt',
  },
  {
    id: 'notif-3',
    type: 'reminder',
    title: 'Hackathon Deadline Approaching',
    message: 'Registration for ShipIt Sprint 2026 closes in 3 days.',
    time: '4h ago',
    read: true,
    targetTab: 'home',
    targetId: 'h-shipit-2026',
  }
];

export const initialUserProfile: UserProfile = {
  id: 'u-current',
  name: 'Oleksandr Kuzmak',
  email: 'oleksandr@shipit.com',
  avatar: '/avatars/alex.jpg',
  bio: 'Fullstack builder enthusiastic about hackathons, modular architecture, and modern UX design systems.',
  college: 'Kyiv Polytechnic Institute',
  location: 'Kyiv / Remote',
  domains: ['Fullstack', 'Frontend', 'Cloud', 'Design Systems'],
  skills: [
    { name: 'React', proficiency: 'Advanced', verified: true },
    { name: 'TypeScript', proficiency: 'Advanced', verified: true },
    { name: 'FastAPI', proficiency: 'Intermediate', verified: true },
    { name: 'Tailwind CSS', proficiency: 'Advanced', verified: true },
    { name: 'PostgreSQL', proficiency: 'Intermediate', verified: true },
  ],
  githubUrl: 'https://github.com/oleksandr-k',
  linkedinUrl: 'https://linkedin.com/in/oleksandr-kuzmak',
  portfolioUrl: 'https://oleksandr.dev',
  resumeFileName: 'Oleksandr_Kuzmak_Resume_2026.pdf',
  resumeParseStatus: 'confirmed',
};
