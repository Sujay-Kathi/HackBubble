import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'theme/app_theme.dart';
import 'providers/app_provider.dart';
import 'screens/home_screen.dart';
import 'screens/discover_screen.dart';
import 'screens/create_team_screen.dart';
import 'screens/my_teams_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/auth_screen.dart';
import 'components/top_app_bar.dart';
import 'components/notification_drawer.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final provider = AppProvider();
  await provider.init();
  runApp(
    ChangeNotifierProvider.value(
      value: provider,
      child: const HackBubbleApp(),
    ),
  );
}

class HackBubbleApp extends StatelessWidget {
  const HackBubbleApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HackBubble',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      home: Consumer<AppProvider>(
        builder: (context, p, _) {
          if (!p.isAuthenticated) return const AuthScreen();
          return const MainShell();
        },
      ),
    );
  }
}

class MainShell extends StatelessWidget {
  const MainShell({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    final screens = [
      const HomeScreen(),
      const DiscoverScreen(),
      const CreateTeamScreen(),
      const MyTeamsScreen(),
      const ProfileScreen(),
    ];
    return Scaffold(
      appBar: const TopAppBar(),
      body: Stack(
        children: [
          SafeArea(child: screens[p.activeTab]),
          if (p.notificationDrawerOpen) const NotificationDrawer(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: p.activeTab,
        onDestinationSelected: p.setTab,
        backgroundColor: AppColors.bubbleCream,
        indicatorColor: AppColors.bubbleSageLight,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Home'),
          NavigationDestination(icon: Icon(Icons.compass_calibration_outlined), selectedIcon: Icon(Icons.compass_calibration), label: 'Discover'),
          NavigationDestination(icon: Icon(Icons.add_circle_outline), selectedIcon: Icon(Icons.add_circle), label: 'Create'),
          NavigationDestination(icon: Icon(Icons.groups_outlined), selectedIcon: Icon(Icons.groups), label: 'My Teams'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Profile'),
        ],
      ),
    );
  }
}
