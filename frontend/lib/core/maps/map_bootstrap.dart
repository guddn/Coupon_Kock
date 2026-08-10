import 'map_bootstrap_stub.dart'
    if (dart.library.js_interop) 'map_bootstrap_web.dart'
    as platform;

Future<void> ensureGoogleMapsLoaded(String apiKey) =>
    platform.ensureGoogleMapsLoaded(apiKey);
