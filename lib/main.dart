import 'package:flutter/material.dart';
import 'screens/login_screen.dart';

void main() {
  runApp(const GeldApp());
}

class GeldApp extends StatelessWidget {
  const GeldApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Geld-Tracker',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
