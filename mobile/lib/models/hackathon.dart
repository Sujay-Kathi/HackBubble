class Hackathon {
  final String id;
  final String title;
  final String? organizer;
  final List<String> themes;
  final String mode;
  final String? location;
  final String? registrationUrl;
  final String eventUrl;
  final String sourceName;
  final DateTime? registrationDeadline;
  final String status;
  bool isBookmarked;

  Hackathon({
    required this.id,
    required this.title,
    this.organizer,
    this.themes = const [],
    required this.mode,
    this.location,
    this.registrationUrl,
    required this.eventUrl,
    required this.sourceName,
    this.registrationDeadline,
    required this.status,
    this.isBookmarked = false,
  });

  factory Hackathon.fromJson(Map<String, dynamic> j) => Hackathon(
        id: j['id'],
        title: j['title'],
        organizer: j['organizer'],
        themes: (j['themes'] as List?)?.cast<String>() ?? [],
        mode: j['mode'] ?? 'online',
        location: j['location'],
        registrationUrl: j['registration_url'],
        eventUrl: j['event_url'],
        sourceName: j['source_name'],
        registrationDeadline: j['registration_deadline'] != null ? DateTime.parse(j['registration_deadline']) : null,
        status: j['status'] ?? 'upcoming',
      );
}
