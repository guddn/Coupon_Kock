import 'dart:async';
import 'dart:js_interop';
import 'dart:js_interop_unsafe';

import 'package:web/web.dart' as web;

Future<void> ensureGoogleMapsLoaded(String apiKey) async {
  if (apiKey.isEmpty || _mapsObjectExists()) return;
  final completer = Completer<void>();
  final script = web.HTMLScriptElement()
    ..src =
        'https://maps.googleapis.com/maps/api/js?key=${Uri.encodeQueryComponent(apiKey)}'
    ..async = true;
  script.addEventListener('load', ((web.Event _) => completer.complete()).toJS);
  script.addEventListener(
    'error',
    ((web.Event _) => completer.completeError(
      StateError('Google Maps SDK를 불러오지 못했습니다.'),
    )).toJS,
  );
  web.document.head?.append(script);
  await completer.future.timeout(const Duration(seconds: 15));
}

bool _mapsObjectExists() {
  final google = globalContext.getProperty<JSAny?>('google'.toJS);
  if (google == null || google.isUndefinedOrNull) return false;
  final maps = (google as JSObject).getProperty<JSAny?>('maps'.toJS);
  return maps != null && !maps.isUndefinedOrNull;
}
