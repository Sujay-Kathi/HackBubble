import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../theme/app_theme.dart';

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key});

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  bool isLogin = true;
  final emailCtrl = TextEditingController();
  final passCtrl = TextEditingController();
  final nameCtrl = TextEditingController();

  @override
  Widget build(BuildContext context) {
    final p = context.watch<AppProvider>();
    return Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(colors: [AppColors.bubbleSageDark, AppColors.bubbleSage]),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: const Center(child: Text('HB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 20))),
              ),
              const SizedBox(height: 16),
              const Text('HackBubble', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w800, color: AppColors.bubbleInk)),
              const SizedBox(height: 4),
              Text(isLogin ? 'Welcome back' : 'Create your account', style: const TextStyle(color: AppColors.bubbleMuted)),
              const SizedBox(height: 24),
              if (!isLogin) ...[
                TextField(controller: nameCtrl, decoration: const InputDecoration(labelText: 'Display name', border: OutlineInputBorder())),
                const SizedBox(height: 12),
              ],
              TextField(controller: emailCtrl, decoration: const InputDecoration(labelText: 'Email', border: OutlineInputBorder())),
              const SizedBox(height: 12),
              TextField(controller: passCtrl, obscureText: true, decoration: const InputDecoration(labelText: 'Password', border: OutlineInputBorder())),
              const SizedBox(height: 16),
              if (p.error != null) Text(p.error!, style: const TextStyle(color: AppColors.bubbleHeart)),
              const SizedBox(height: 8),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: p.isLoading ? null : () async {
                    final ok = isLogin
                        ? await p.login(emailCtrl.text, passCtrl.text)
                        : await p.register(emailCtrl.text, passCtrl.text, nameCtrl.text);
                    if (!ok && context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(p.error ?? 'Failed')));
                    }
                  },
                  child: p.isLoading ? const CircularProgressIndicator(color: Colors.white) : Text(isLogin ? 'Log in' : 'Sign up'),
                ),
              ),
              TextButton(
                onPressed: () => setState(() => isLogin = !isLogin),
                child: Text(isLogin ? "Don't have an account? Sign up" : 'Already have an account? Log in'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
