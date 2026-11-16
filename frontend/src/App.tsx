import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { DeviceFrame } from './components/common/DeviceFrame';
import { TopAppBar } from './components/navigation/TopAppBar';
import { BottomNav } from './components/navigation/BottomNav';
import { NotificationDrawer } from './components/common/NotificationDrawer';
import { AuthModal } from './screens/AuthModal';
import { HackathonDetailScreen } from './screens/HackathonDetailScreen';
import { HomeScreen } from './screens/HomeScreen';
import { DiscoverScreen } from './screens/DiscoverScreen';
import { CreateTeamWizard } from './screens/CreateTeamWizard';
import { MyTeamsScreen } from './screens/MyTeamsScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import { WelcomeScreen } from './screens/WelcomeScreen';
import { SignupScreen } from './screens/SignupScreen';
import { VerifyCodeScreen } from './screens/VerifyCodeScreen';
import { ResumeReviewScreen } from './screens/ResumeReviewScreen';
import { JoinTeamScreen } from './screens/JoinTeamScreen';
import { CandidateScreeningScreen } from './screens/CandidateScreeningScreen';
import { ShortlistFinalizeScreen } from './screens/ShortlistFinalizeScreen';
import { MyApplicationsScreen } from './screens/MyApplicationsScreen';
import { NotificationsScreen } from './screens/NotificationsScreen';

const FULL_SCREEN = new Set([
  'welcome', 'signup', 'verify', 'resume-review', 'hackathon-detail',
  'join-team', 'screening', 'finalize', 'notifications', 'applications',
]);

const MainLayout: React.FC = () => {
  const { currentScreen, setCurrentScreen } = useApp();

  if (currentScreen === 'welcome') return <WelcomeScreen />;
  if (currentScreen === 'signup') return <SignupScreen />;
  if (currentScreen === 'verify') return <VerifyCodeScreen />;
  if (currentScreen === 'resume-review') return <ResumeReviewScreen />;
  if (currentScreen === 'join-team') return <JoinTeamScreen />;
  if (currentScreen === 'screening') return <CandidateScreeningScreen />;
  if (currentScreen === 'finalize') return <ShortlistFinalizeScreen />;
  if (currentScreen === 'notifications') return <NotificationsScreen />;
  if (currentScreen === 'applications') return <MyApplicationsScreen />;

  return (
    <DeviceFrame>
      <TopAppBar />
      <main className="flex-1 flex flex-col relative overflow-x-hidden">
        {currentScreen === 'home' && <HomeScreen />}
        {currentScreen === 'discover' && <DiscoverScreen />}
        {currentScreen === 'create' && <CreateTeamWizard />}
        {currentScreen === 'my-teams' && <MyTeamsScreen />}
        {currentScreen === 'profile' && <ProfileScreen />}
      </main>
      <BottomNav />
      <AuthModal />
      <NotificationDrawer />
    </DeviceFrame>
  );
};

export default function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}