import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class MyTeamsScreen extends StatefulWidget {
  const MyTeamsScreen({super.key});

  @override
  State<MyTeamsScreen> createState() => _MyTeamsScreenState();
}

class _MyTeamsScreenState extends State<MyTeamsScreen> {
  List<dynamic> teams = [];
  bool loading = false;

  Future<void> load() async {
    setState(() => loading = true);
    try {
      final res = await ApiService.get('/teams/discover');
      final data = ApiService.decode(res);
      if (res.statusCode == 200 && data['success'] == true) {
        teams = (data['data'] as List);
      }
    } catch (_) {}
    setState(() => loading = false);
  }

  @override
  void initState() {
    super.initState();
    load();
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: load,
      child: loading
          ? const Center(child: CircularProgressIndicator())
          : ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: teams.length,
              itemBuilder: (_, i) {
                final t = teams[i] as Map<String, dynamic>;
                return Card(
                  margin: const EdgeInsets.only(bottom: 10),
                  child: ListTile(
                    title: Text(t['name'] ?? ''),
                    subtitle: Text('Status: ${t['status']}'),
                    trailing: Text('${t['current_size']}/${t['target_size']}'),
                  ),
                );
              },
            ),
    );
  }
}
