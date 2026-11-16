import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class DiscoverScreen extends StatefulWidget {
  const DiscoverScreen({super.key});

  @override
  State<DiscoverScreen> createState() => _DiscoverScreenState();
}

class _DiscoverScreenState extends State<DiscoverScreen> {
  List<dynamic> teams = [];
  bool loading = false;
  final roleCtrl = TextEditingController();
  final skillCtrl = TextEditingController();

  Future<void> load() async {
    setState(() => loading = true);
    try {
      final res = await ApiService.get('/teams/discover', query: {
        if (roleCtrl.text.isNotEmpty) 'role_name': roleCtrl.text,
        if (skillCtrl.text.isNotEmpty) 'skill': skillCtrl.text,
      });
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
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Expanded(child: TextField(controller: roleCtrl, decoration: const InputDecoration(hintText: 'Role', border: OutlineInputBorder(), isDense: true))),
              const SizedBox(width: 8),
              Expanded(child: TextField(controller: skillCtrl, decoration: const InputDecoration(hintText: 'Skill', border: OutlineInputBorder(), isDense: true))),
              const SizedBox(width: 8),
              IconButton(onPressed: load, icon: const Icon(Icons.search)),
            ],
          ),
        ),
        Expanded(
          child: loading
              ? const Center(child: CircularProgressIndicator())
              : RefreshIndicator(
                  onRefresh: load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: teams.length,
                    itemBuilder: (_, i) {
                      final t = teams[i] as Map<String, dynamic>;
                      return Card(
                        margin: const EdgeInsets.only(bottom: 10),
                        child: ListTile(
                          title: Text(t['name'] ?? ''),
                          subtitle: Text(t['problem_statement'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis),
                          trailing: Text('${t['current_size']}/${t['target_size']}'),
                        ),
                      );
                    },
                  ),
                ),
        ),
      ],
    );
  }
}
