import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/hackathon.dart';

class AppNotification {
  final String id;
  final String title;
  final String message;
  final bool read;
  final String? targetTab;
  final String? targetId;
  AppNotification({required this.id, required this.title, required this.message, required this.read, this.targetTab, this.targetId});
  factory AppNotification.fromJson(Map<String, dynamic> j) => AppNotification(
        id: j['id'],
        title: j['title'],
        message: j['body'] ?? '',
        read: j['read_at'] != null,
        targetTab: null,
        targetId: j['entity_id'],
      );
}

class AppProvider extends ChangeNotifier {
  bool isLoading = false;
  String? error;
  String? token;
  String? userId;
  String? displayName;
  bool get isAuthenticated => token != null;

  List<Hackathon> hackathons = [];
  List<AppNotification> notifications = [];
  List<String> myTeamIds = [];
  int activeTab = 0;
  bool notificationDrawerOpen = false;
  String? selectedHackathonId;
  String? selectedTeamId;
  String screeningTeamId = '';
  bool isMobileFrame = true;
  bool authModalOpen = false;

  int get unreadNotifCount => notifications.where((n) => !n.read).length;

  Future<void> init() async {
    if (isAuthenticated) {
      await loadHackathons();
      await loadNotifications();
    }
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    isLoading = true; notifyListeners();
    try {
      final res = await ApiService.post('/auth/login', body: {'email': email, 'password': password}, auth: false);
      final data = ApiService.decode(res);
      if (res.statusCode == 200 && data['success'] == true) {
        final d = data['data'];
        token = d['access_token']; userId = d['user_id']; displayName = d['display_name'] ?? email;
        await ApiService.setToken(token);
        await loadHackathons(); await loadNotifications();
        isLoading = false; notifyListeners(); return true;
      }
      error = data['detail'] ?? 'Login failed';
    } catch (e) { error = e.toString(); }
    isLoading = false; notifyListeners(); return false;
  }

  Future<bool> register(String email, String password, String name) async {
    isLoading = true; notifyListeners();
    try {
      final res = await ApiService.post('/auth/register', body: {'email': email, 'password': password, 'display_name': name}, auth: false);
      final data = ApiService.decode(res);
      if (res.statusCode == 201 && data['success'] == true) {
        final d = data['data'];
        token = d['access_token']; userId = d['user_id']; displayName = name;
        await ApiService.setToken(token);
        await loadHackathons(); await loadNotifications();
        isLoading = false; notifyListeners(); return true;
      }
      error = data['detail'] ?? 'Registration failed';
    } catch (e) { error = e.toString(); }
    isLoading = false; notifyListeners(); return false;
  }

  Future<void> logout() async {
    token = null; userId = null; displayName = null; hackathons = []; notifications = []; myTeamIds = [];
    await ApiService.setToken(null); notifyListeners();
  }

  Future<void> loadHackathons({String? theme}) async {
    try {
      final res = await ApiService.get('/hackathons', query: theme != null ? {'theme': theme} : null);
      final data = ApiService.decode(res);
      if (res.statusCode == 200 && data['success'] == true) {
        hackathons = ((data['data'] as List).cast<Map<String, dynamic>>()).map(Hackathon.fromJson).toList();
      }
    } catch (e) { error = e.toString(); }
    notifyListeners();
  }

  Future<void> toggleBookmark(String id) async {
    final h = hackathons.firstWhere((e) => e.id == id);
    try {
      if (h.isBookmarked) await ApiService.delete('/hackathons/$id/bookmark');
      else await ApiService.post('/hackathons/$id/bookmark');
      h.isBookmarked = !h.isBookmarked; notifyListeners();
    } catch (_) {}
  }

  Future<void> loadNotifications() async {
    try {
      final res = await ApiService.get('/notifications');
      final data = ApiService.decode(res);
      if (res.statusCode == 200 && data['success'] == true) {
        notifications = ((data['items'] as List?) ?? []).cast<Map<String, dynamic>>().map(AppNotification.fromJson).toList();
      }
    } catch (_) {}
    notifyListeners();
  }

  Future<void> markNotifAsRead(String id) async {
    await ApiService.patch('/notifications/$id/read');
    final idx = notifications.indexWhere((n) => n.id == id);
    if (idx >= 0) {
      notifications[idx] = AppNotification(id: notifications[idx].id, title: notifications[idx].title, message: notifications[idx].message, read: true, targetTab: notifications[idx].targetTab, targetId: notifications[idx].targetId);
      notifyListeners();
    }
  }

  Future<void> markAllNotifsAsRead() async {
    await ApiService.patch('/notifications/read-all');
    notifications = notifications.map((n) => AppNotification(id: n.id, title: n.title, message: n.message, read: true, targetTab: n.targetTab, targetId: n.targetId)).toList();
    notifyListeners();
  }

  void setTab(int i) { activeTab = i; notifyListeners(); }
  void setNotificationDrawerOpen(bool v) { notificationDrawerOpen = v; notifyListeners(); }
  void setSelectedHackathonId(String? v) { selectedHackathonId = v; notifyListeners(); }
  void setSelectedTeamId(String? v) { selectedTeamId = v; notifyListeners(); }
  void setScreeningTeamId(String v) { screeningTeamId = v; notifyListeners(); }
  void setIsMobileFrame(bool v) { isMobileFrame = v; notifyListeners(); }
  void setAuthModalOpen(bool v) { authModalOpen = v; notifyListeners(); }
}
