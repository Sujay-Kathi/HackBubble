import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/v1';
  static String? _token;

  static Future<String?> getToken() async => _token;
  static Future<void> setToken(String? token) async => _token = token;

  static Future<Map<String, String>> _headers({bool auth = true}) async {
    final h = <String, String>{'Content-Type': 'application/json'};
    if (auth) {
      final t = await getToken();
      if (t != null) h['Authorization'] = 'Bearer $t';
    }
    return h;
  }

  static Future<http.Response> get(String path, {Map<String, String>? query, bool auth = true}) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: query);
    return http.get(uri, headers: await _headers(auth: auth));
  }

  static Future<http.Response> post(String path, {Object? body, bool auth = true}) async {
    final uri = Uri.parse('$baseUrl$path');
    return http.post(uri, headers: await _headers(auth: auth), body: body == null ? null : jsonEncode(body));
  }

  static Future<http.Response> patch(String path, {Object? body, bool auth = true}) async {
    final uri = Uri.parse('$baseUrl$path');
    return http.patch(uri, headers: await _headers(auth: auth), body: body == null ? null : jsonEncode(body));
  }

  static Future<http.Response> delete(String path, {bool auth = true}) async {
    final uri = Uri.parse('$baseUrl$path');
    return http.delete(uri, headers: await _headers(auth: auth));
  }

  static Map<String, dynamic> decode(http.Response r) {
    if (r.body.isEmpty) return {};
    return jsonDecode(r.body) as Map<String, dynamic>;
  }
}
