import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../theme/app_theme.dart';

class NotificationDrawer extends StatelessWidget {
  const NotificationDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    return GestureDetector(
      onTap: () => p.setNotificationDrawerOpen(false),
      child: Container(
        color: Colors.black45,
        child: Align(
          alignment: Alignment.centerRight,
          child: GestureDetector(
            onTap: () {},
            child: Container(
              width: MediaQuery.of(context).size.width * 0.85,
              height: double.infinity,
              color: AppColors.bubbleCream,
              child: Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Row(
                      children: [
                        const Icon(Icons.notifications, color: AppColors.bubbleSageDeep),
                        const SizedBox(width: 8),
                        const Text('Notifications', style: TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                        const Spacer(),
                        TextButton(onPressed: () => p.markAllNotifsAsRead(), child: const Text('Read all')),
                        IconButton(icon: const Icon(Icons.close), onPressed: () => p.setNotificationDrawerOpen(false)),
                      ],
                    ),
                  ),
                  Expanded(
                    child: p.notifications.isEmpty
                        ? const Center(child: Text('No new notifications', style: TextStyle(color: AppColors.bubbleMuted)))
                        : ListView.builder(
                            itemCount: p.notifications.length,
                            itemBuilder: (_, i) {
                              final n = p.notifications[i];
                              return ListTile(
                                title: Text(n.title, style: TextStyle(fontWeight: n.read ? FontWeight.normal : FontWeight.bold)),
                                subtitle: Text(n.message, maxLines: 2, overflow: TextOverflow.ellipsis),
                                trailing: n.read ? null : Container(width: 8, height: 8, decoration: const BoxDecoration(color: AppColors.bubbleHeart, shape: BoxShape.circle)),
                                onTap: () => p.markNotifAsRead(n.id),
                              );
                            },
                          ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
