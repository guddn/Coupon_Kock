import 'package:flutter/material.dart';

import 'app.dart';
import 'core/config/app_config.dart';
import 'core/maps/map_bootstrap.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await ensureGoogleMapsLoaded(AppConfig.googleMapsApiKey);
  runApp(CouponKockApp());
}
