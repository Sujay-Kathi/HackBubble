import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Row(
          children: [
            const CircleAvatar(radius: 28, backgroundColor: AppColors.bubbleSageLight, child: Icon(Icons.person, color: AppColors.bubbleSageDeep)),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(p.displayName ?? 'User', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18)),
                Text(p.userId ?? '', style: const TextStyle(color: AppColors.bubbleMuted, fontSize: 12)),
              ],
            ),
          ],
        ),
        const SizedBox(height: 20),
        ElevatedButton.icon(
          onPressed: () async {
            final res = await ApiService.get('/profiles/me');
            if (context.mounted) {
              ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Profile loaded: ${res.statusCode}')));
            }
          },
          icon: const Icon(Icons.refresh),
          label: const Text('Refresh profile'),
        ),
        const SizedBox(height: 12),
        OutlinedButton.icon(
          onPressed: () => p.logout(),
          icon: const Icon(Icons.logout),
          label: const Text('Log out'),
        ),
      ],
    );
  }
}
