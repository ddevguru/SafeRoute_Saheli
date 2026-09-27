import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute_saheli/widgets/status_card.dart';
import 'package:saferoute_saheli/widgets/quick_action_tile.dart';
import 'package:saferoute_saheli/widgets/emergency_button.dart';

void main() {
  group('Phase 3 - Flutter UI Components Tests', () {
    testWidgets('StatusOverviewCard renders device, battery, score, and live indicators', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: StatusOverviewCard(
              isDeviceConnected: true,
              batteryPercent: 85,
              safetyScore: 92.0,
              guardianStatus: 'Mother ● Online',
              isCameraLive: true,
              currentLocationName: 'Safe Haven Area',
            ),
          ),
        ),
      );

      expect(find.text('Device Connected'), findsOneWidget);
      expect(find.text('85%'), findsOneWidget);
      expect(find.text('92/100'), findsOneWidget);
      expect(find.text('Mother ● Online'), findsOneWidget);
      expect(find.text('● Live'), findsOneWidget);
    });

    testWidgets('QuickActionTile renders title and triggers onTap callback', (WidgetTester tester) async {
      bool tapped = false;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: QuickActionTile(
              title: 'Safe Route',
              icon: Icons.alt_route_rounded,
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      expect(find.text('Safe Route'), findsOneWidget);
      expect(find.byIcon(Icons.alt_route_rounded), findsOneWidget);

      await tester.tap(find.text('Safe Route'));
      await tester.pump();
      expect(tapped, isTrue);
    });

    testWidgets('NearbyPlaceCard renders information, Navigate button, and Call button', (WidgetTester tester) async {
      bool navigated = false;
      bool called = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: NearbyPlaceCard(
              name: 'Central Women Police Booth',
              category: 'POLICE',
              distanceMeters: 350,
              onNavigate: () => navigated = true,
              onCall: () => called = true,
            ),
          ),
        ),
      );

      expect(find.text('Central Women Police Booth'), findsOneWidget);
      expect(find.text('350 m away'), findsOneWidget);
      expect(find.text('Navigate →'), findsOneWidget);
      expect(find.byIcon(Icons.phone_in_talk_rounded), findsOneWidget);

      await tester.tap(find.text('Navigate →'));
      expect(navigated, isTrue);

      await tester.tap(find.byIcon(Icons.phone_in_talk_rounded));
      expect(called, isTrue);
    });

    testWidgets('EmergencyButton renders with PRESS & HOLD label and instruction', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: EmergencyButton(
              onTrigger: () {},
            ),
          ),
        ),
      );

      expect(find.text('EMERGENCY'), findsOneWidget);
      expect(find.text('PRESS & HOLD'), findsOneWidget);
      expect(find.byIcon(Icons.warning_amber_rounded), findsOneWidget);
    });
  });
}
