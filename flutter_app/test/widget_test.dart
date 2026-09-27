import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute_saheli/main.dart';

void main() {
  testWidgets('SafeRoute Saheli App boots to SplashScreen and displays tagline', (WidgetTester tester) async {
    // Build our app and trigger an initial frame.
    await tester.pumpWidget(const SafeRouteSaheliApp());

    // Verify initial splash state
    expect(find.text('SafeRoute Saheli'), findsOneWidget);
    expect(find.text('"Stay Connected. Stay Aware. Stay Safe."'), findsOneWidget);

    // Advance beyond splash animation and timer to Onboarding
    await tester.pump(const Duration(seconds: 3));
    await tester.pumpAndSettle();

    // Verify transition to Onboarding
    expect(find.text('Your Safety, Always Connected'), findsOneWidget);
  });
}
