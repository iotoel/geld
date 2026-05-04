import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/expense.dart';
import '../services/data_service.dart';

class EditExpenseScreen extends StatefulWidget {
  final Expense expense;

  const EditExpenseScreen({super.key, required this.expense});

  @override
  State<EditExpenseScreen> createState() => _EditExpenseScreenState();
}

class _EditExpenseScreenState extends State<EditExpenseScreen> {
  late final TextEditingController _dateController;
  late final TextEditingController _priceController;
  late final TextEditingController _descriptionController;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _dateController = TextEditingController(
      text: DateFormat('dd.MM.yyyy').format(widget.expense.date),
    );
    _priceController = TextEditingController(
      text: widget.expense.price.toString(),
    );
    _descriptionController = TextEditingController(
      text: widget.expense.description,
    );
  }

  @override
  void dispose() {
    _dateController.dispose();
    _priceController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  double _roundToNearest05(double value) {
    return (value * 20).round() / 20;
  }

  Future<void> _saveExpense() async {
    final dateText = _dateController.text.trim();
    final priceText = _priceController.text.trim();
    final description = _descriptionController.text.trim();

    if (dateText.isEmpty || priceText.isEmpty || description.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Alle Felder müssen ausgefüllt sein')),
      );
      return;
    }

    try {
      final date = DateFormat('dd.MM.yyyy').parseStrict(dateText);
      final price = _roundToNearest05(double.parse(priceText));

      setState(() => _isLoading = true);

      final updatedExpense = Expense(
        id: widget.expense.id,
        date: date,
        price: price,
        description: description,
      );

      await DataService.updateExpense(updatedExpense);

      if (mounted) {
        Navigator.of(context).pop(true);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ausgabe aktualisiert')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Fehler beim Speichern')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Ausgabe bearbeiten'),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveExpense,
            child: _isLoading
                ? const CircularProgressIndicator()
                : const Text('Speichern'),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _dateController,
              decoration: const InputDecoration(
                labelText: 'Datum (TT.MM.JJJJ)',
                border: OutlineInputBorder(),
                helperText: 'Format: 31.12.2025',
              ),
              onTap: () async {
                final date = await showDatePicker(
                  context: context,
                  initialDate: widget.expense.date,
                  firstDate: DateTime(2020),
                  lastDate: DateTime(2030),
                );
                if (date != null) {
                  _dateController.text = DateFormat('dd.MM.yyyy').format(date);
                }
              },
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _priceController,
              keyboardType: TextInputType.numberWithOptions(decimal: true),
              decoration: const InputDecoration(
                labelText: 'Preis in CHF',
                border: OutlineInputBorder(),
                helperText: 'Negative Zahlen für Ausgaben, positive für Einnahmen',
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Beschreibung',
                border: OutlineInputBorder(),
                helperText: '"Bezug" für Bargeldbezüge',
              ),
            ),
            const Spacer(),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Abbrechen'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
