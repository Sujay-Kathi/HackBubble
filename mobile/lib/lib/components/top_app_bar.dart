import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../theme/app_theme.dart';

class TopAppBar extends StatelessWidget implements PreferredSizeWidget {
  const TopAppBar({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(56);

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    final titles = ['Hackathons', 'Find Teams', 'Create Team', 'My Teams', 'Profile'];
    return AppBar(
      backgroundColor: AppColors.bubbleCream.withOpacity(0.95),
      title: Row(
        children: [
          GestureDetector(
            onTap: () => p.setTab(0),
            child: Container(
              width: 32, height: 32,
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [AppColors.bubbleSageDark, AppColors.bubbleSage]),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Center(child: Text('HB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 12))),
            ),
          ),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('HackBubble', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: AppColors.bubbleInk)),
              Text(titles[p.activeTab], style: const TextStyle(fontSize: 10, color: AppColors.bubbleMuted)),
            ],
          ),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.notifications_outlined),
          onPressed: () => p.setNotificationDrawerOpen(true),
        ),
        Padding(
          padding: const EdgeInsets.only(right: 8),
          child: CircleAvatar(radius: 14, backgroundColor: AppColors.bubbleSageLight, child: Text((p.displayName ?? 'U')[0].toUpperCase(), style: const TextStyle(color: AppColors.bubbleSageDeep, fontWeight: FontWeight.bold))),
        ),
      ],
    );
  }
}
