import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/expense.dart';
import '../services/data_service.dart';
import 'edit_expense_screen.dart';

class MonthScreen extends StatefulWidget {
  final String month;
  final List<Expense> expenses;

  const MonthScreen({
    super.key,
    required this.month,
    required this.expenses,
  });

  @override
  State<MonthScreen> createState() => _MonthScreenState();
}

class _MonthScreenState extends State<MonthScreen> {
  List<Expense> _expenses = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _expenses = List.from(widget.expenses);
    _expenses.sort((a, b) => a.date.compareTo(b.date));
  }

  String _formatMonthFull(String monthKey) {
    final parts = monthKey.split('-');
    final year = parts[0];
    final month = int.parse(parts[1]);
    final monthNames = [
      'Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
      'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'
    ];
    return '${monthNames[month - 1]} $year';
  }

  Future<void> _deleteExpense(Expense expense) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Löschen bestätigen'),
        content: Text('Möchten Sie diese Ausgabe wirklich löschen?\n\n${expense.description}\n${expense.price.toStringAsFixed(2)} CHF'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Abbrechen'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Löschen'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      setState(() => _isLoading = true);
      try {
        await DataService.deleteExpense(expense.id);
        setState(() {
          _expenses.removeWhere((e) => e.id == expense.id);
          _isLoading = false;
        });
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Ausgabe gelöscht')),
          );
        }
      } catch (e) {
        setState(() => _isLoading = false);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Fehler beim Löschen')),
          );
        }
      }
    }
  }

  Future<void> _editExpense(Expense expense) async {
    final result = await Navigator.of(context).push(
      MaterialPageRoute(
        builder: (context) => EditExpenseScreen(expense: expense),
      ),
    );

    if (result == true && mounted) {
      // Daten neu laden
      final allExpenses = await DataService.getExpenses();
      setState(() {
        _expenses = allExpenses
            .where((e) => '${e.date.year}-${e.date.month.toString().padLeft(2, '0')}' == widget.month)
            .toList();
        _expenses.sort((a, b) => a.date.compareTo(b.date));
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final total = _expenses.fold<double>(0, (sum, expense) => sum + expense.price);

    return Scaffold(
      appBar: AppBar(
        title: Text(_formatMonthFull(widget.month)),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // Zusammenfassung
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16.0),
                  color: Colors.grey[100],
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Monatssumme: ${total.toStringAsFixed(2)} CHF',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: total < 0 ? Colors.red : Colors.green,
                        ),
                      ),
                      Text(
                        '${_expenses.length} Einträge',
                        style: TextStyle(
                          fontSize: 14,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                // Eintragsliste
                Expanded(
                  child: _expenses.isEmpty
                      ? const Center(
                          child: Text('Keine Einträge für diesen Monat'),
                        )
                      : ListView.builder(
                          itemCount: _expenses.length,
                          itemBuilder: (context, index) {
                            final expense = _expenses[index];
                            return Card(
                              margin: const EdgeInsets.symmetric(
                                horizontal: 8.0,
                                vertical: 4.0,
                              ),
                              child: ListTile(
                                leading: Icon(
                                  expense.isCashWithdrawal
                                      ? Icons.money
                                      : Icons.shopping_cart,
                                  color: expense.isCashWithdrawal
                                      ? Colors.green
                                      : Colors.blue,
                                ),
                                title: Text(expense.description),
                                subtitle: Text(
                                  DateFormat('dd.MM.yyyy').format(expense.date),
                                ),
                                trailing: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Text(
                                      '${expense.price.toStringAsFixed(2)} CHF',
                                      style: TextStyle(
                                        fontWeight: FontWeight.bold,
                                        color: expense.price < 0
                                            ? Colors.red
                                            : Colors.green,
                                      ),
                                    ),
                                    PopupMenuButton<String>(
                                      onSelected: (value) {
                                        if (value == 'edit') {
                                          _editExpense(expense);
                                        } else if (value == 'delete') {
                                          _deleteExpense(expense);
                                        }
                                      },
                                      itemBuilder: (context) => [
                                        const PopupMenuItem(
                                          value: 'edit',
                                          child: Row(
                                            children: [
                                              Icon(Icons.edit),
                                              SizedBox(width: 8),
                                              Text('Ändern'),
                                            ],
                                          ),
                                        ),
                                        const PopupMenuItem(
                                          value: 'delete',
                                          child: Row(
                                            children: [
                                              Icon(Icons.delete),
                                              SizedBox(width: 8),
                                              Text('Löschen'),
                                            ],
                                          ),
                                        ),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
    );
  }
}
