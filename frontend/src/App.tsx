import React from 'react';
import { AppProvider, useApp } from './context/AppContext';
import { DeviceFrame } from './components/common/DeviceFrame';
import { TopAppBar } from './components/navigation/TopAppBar';
import { BottomNav } from './components/navigation/BottomNav';
import { NotificationDrawer } from './components/common/NotificationDrawer';
import { AuthModal } from './screens/AuthModal';
import { HackathonDetailModal } from './screens/HackathonDetailModal';
import { HomeScreen } from './screens/HomeScreen';
import { DiscoverScreen } from './screens/DiscoverScreen';
import { CreateTeamWizard } from './screens/CreateTeamWizard';
import { MyTeamsScreen } from './screens/MyTeamsScreen';
import { ProfileScreen } from './screens/ProfileScreen';

const MainLayout: React.FC = () => {
  const { activeTab } = useApp();

  return (
    <DeviceFrame>
      {/* Top Application Bar */}
      <TopAppBar />

      {/* Main Dynamic Screen Outlet */}
      <main className="flex-1 flex flex-col relative overflow-x-hidden">
        {activeTab === 'home' && <HomeScreen />}
        {activeTab === 'discover' && <DiscoverScreen />}
        {activeTab === 'create' && <CreateTeamWizard />}
        {activeTab === 'my-teams' && <MyTeamsScreen />}
        {activeTab === 'profile' && <ProfileScreen />}
      </main>

      {/* Global Persistent Bottom Navigation */}
      <BottomNav />

      {/* Modals & Overlays */}
      <HackathonDetailModal />
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
