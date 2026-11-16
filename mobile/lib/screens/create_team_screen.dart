import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';

class CreateTeamScreen extends StatefulWidget {
  const CreateTeamScreen({super.key});

  @override
  State<CreateTeamScreen> createState() => _CreateTeamScreenState();
}

class _CreateTeamScreenState extends State<CreateTeamScreen> {
  final nameCtrl = TextEditingController();
  final problemCtrl = TextEditingController();
  final roleCtrl = TextEditingController();
  String? hackathonId;
  bool loading = false;

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    if (hackathonId == null && p.hackathons.isNotEmpty) {
      hackathonId = p.hackathons.first.id;
    }
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Create Team', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            value: hackathonId,
            decoration: const InputDecoration(labelText: 'Hackathon', border: OutlineInputBorder()),
            items: p.hackathons.map((h) => DropdownMenuItem(value: h.id, child: Text(h.title))).toList(),
            onChanged: (v) => setState(() => hackathonId = v),
          ),
          const SizedBox(height: 12),
          TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Team name', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          TextField(controller: problemCtrl, maxLines: 3, decoration: const InputDecoration(labelText: 'Problem statement', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          TextField(controller: roleCtrl, decoration: const InputDecoration(labelText: 'Role name', border: OutlineInputBorder())),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: loading ? null : () async {
                if (hackathonId == null) return;
                setState(() => loading = true);
                final res = await ApiService.post('/teams', body: {
                  'hackathon_id': hackathonId,
                  'name': nameCtrl.text,
                  'problem_statement': problemCtrl.text,
                  'target_size': 4,
                  'roles': [{'role_name': roleCtrl.text.isEmpty ? 'Member' : roleCtrl.text, 'vacancy_count': 1, 'mandatory_skills': []}],
                });
                setState(() => loading = false);
                if (res.statusCode == 201) {
                  await ApiService.post('/teams/${ApiService.decode(res)['data']['id']}/publish');
                  if (context.mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Team created')));
                    p.setTab(3);
                  }
                } else {
                  if (context.mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: ${res.body}')));
                }
              },
              child: loading ? const CircularProgressIndicator(color: Colors.white) : const Text('Create & publish'),
            ),
          ),
        ],
      ),
    );
  }
}
