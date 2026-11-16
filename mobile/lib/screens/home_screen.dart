import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../models/hackathon.dart';
import '../theme/app_theme.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    return RefreshIndicator(
      onRefresh: () => p.loadHackathons(),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Hackathons', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          if (p.hackathons.isEmpty)
            const Padding(
              padding: EdgeInsets.only(top: 40),
              child: Center(child: Text('No hackathons yet. Pull to refresh.', style: TextStyle(color: AppColors.bubbleMuted))),
            )
          else
            ...p.hackathons.map((h) => _HackathonCard(hackathon: h)),
        ],
      ),
    );
  }
}

class _HackathonCard extends StatelessWidget {
  final Hackathon hackathon;
  const _HackathonCard({required this.hackathon});

  @override
  Widget build(BuildContext context) {
    final p = context.read<AppProvider>();
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(hackathon.title, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16)),
                ),
                IconButton(
                  icon: Icon(hackathon.isBookmarked ? Icons.bookmark : Icons.bookmark_border, color: AppColors.bubbleSageDark),
                  onPressed: () => p.toggleBookmark(hackathon.id),
                ),
              ],
            ),
            if (hackathon.organizer != null)
              Text(hackathon.organizer!, style: const TextStyle(color: AppColors.bubbleMuted, fontSize: 12)),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              children: hackathon.themes.map((t) => Chip(label: Text(t, style: const TextStyle(fontSize: 11)), backgroundColor: AppColors.bubbleSageLight)).toList(),
            ),
            const SizedBox(height: 6),
            Row(
              children: [
                Icon(Icons.location_on_outlined, size: 14, color: AppColors.bubbleMuted),
                const SizedBox(width: 4),
                Text(hackathon.mode, style: const TextStyle(fontSize: 12, color: AppColors.bubbleMuted)),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(color: AppColors.bubbleSageLight, borderRadius: BorderRadius.circular(8)),
                  child: Text(hackathon.status, style: const TextStyle(fontSize: 11, color: AppColors.bubbleSageDeep)),
                ),
              ],
            ),
            if (hackathon.registrationUrl != null) ...[
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: () {},
                  child: const Text('View details'),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
