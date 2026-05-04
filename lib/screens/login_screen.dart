import 'package:flutter/material.dart';
import '../services/data_service.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _passwordController = TextEditingController();
  bool _isLoading = false;
  String _error = '';

  @override
  void dispose() {
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (_passwordController.text.isEmpty) {
      setState(() => _error = 'Passwort darf nicht leer sein');
      return;
    }

    setState(() {
      _isLoading = true;
      _error = '';
    });

    try {
      final storedPassword = await DataService.getPassword();
      
      if (storedPassword == null) {
        // Erster Start - Passwort setzen
        await DataService.setPassword(_passwordController.text);
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const HomeScreen()),
          );
        }
      } else if (storedPassword == _passwordController.text) {
        // Korrektes Passwort
        if (mounted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (context) => const HomeScreen()),
          );
        }
      } else {
        // Falsches Passwort
        setState(() => _error = 'Falsches Passwort!');
      }
    } catch (e) {
      setState(() => _error = 'Fehler beim Login');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Login'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(
              Icons.account_balance_wallet,
              size: 100,
              color: Colors.blue,
            ),
            const SizedBox(height: 40),
            const Text(
              'Geld-Tracker',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 40),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'Passwort',
                border: OutlineInputBorder(),
              ),
              onSubmitted: (_) => _login(),
            ),
            const SizedBox(height: 20),
            if (_error.isNotEmpty)
              Text(
                _error,
                style: const TextStyle(color: Colors.red),
                textAlign: TextAlign.center,
              ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: _isLoading ? null : _login,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
