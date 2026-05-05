import 'package:flutter/material.dart';
import '../models/expense.dart';
import '../services/data_service.dart';
import 'month_screen.dart';
import 'add_expense_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Expense> _expenses = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadExpenses();
  }

  Future<void> _loadExpenses() async {
    setState(() => _isLoading = true);
    try {
      final expenses = await DataService.getExpenses();
      setState(() {
        _expenses = expenses;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Fehler beim Laden der Daten')),
        );
      }
    }
  }

  Map<String, double> _getMonthlyTotals() {
    final Map<String, double> monthlyTotals = {};
    
    for (final expense in _expenses) {
      if (expense.isCashWithdrawal) continue;
      
      final monthKey = '${expense.date.year}-${expense.date.month.toString().padLeft(2, '0')}';
      monthlyTotals[monthKey] = (monthlyTotals[monthKey] ?? 0) + expense.price;
    }
    
    return monthlyTotals;
  }

  Map<String, Map<String, dynamic>> _getCashStats() {
    final Map<String, Map<String, dynamic>> cashStats = {};
    
    for (final expense in _expenses) {
      if (!expense.isCashWithdrawal) continue;
      
      final monthKey = '${expense.date.year}-${expense.date.month.toString().padLeft(2, '0')}';
      final current = cashStats[monthKey] ?? {'count': 0, 'sum': 0.0};
      cashStats[monthKey] = {
        'count': current['count'] + 1,
        'sum': current['sum'] + expense.price,
      };
    }
    
    return cashStats;
  }

  String _formatMonth(String monthKey) {
    final parts = monthKey.split('-');
    final year = parts[0];
    final month = int.parse(parts[1]);
    final monthNames = ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'];
    return '${monthNames[month - 1]} $year';
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final monthlyTotals = _getMonthlyTotals();
    final cashStats = _getCashStats();
    final sortedMonths = monthlyTotals.keys.toList()..sort();
    final sortedCashMonths = cashStats.keys.toList()..sort();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Geld-Tracker'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadExpenses,
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (context) => const SettingsScreen()),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Neue Ausgabe erfassen
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Neue Ausgabe erfassen',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton.icon(
                      onPressed: () async {
                        await Navigator.of(context).push(
                          MaterialPageRoute(builder: (context) => const AddExpenseScreen()),
                        );
                        _loadExpenses();
                      },
                      icon: const Icon(Icons.add),
                      label: const Text('Ausgabe hinzufügen'),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size.fromHeight(48),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // Monatsübersicht
            const Text(
              'Monatsübersicht (ohne Bargeldbezüge)',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            if (sortedMonths.isEmpty)
              const Text('Keine Ausgaben vorhanden')
            else
              ...sortedMonths.map((month) {
                final total = monthlyTotals[month]!;
                return Card(
                  margin: const EdgeInsets.only(bottom: 8.0),
                  child: ListTile(
                    title: Text(_formatMonth(month)),
                    trailing: Text(
                      '${total.toStringAsFixed(2)} CHF',
                      style: TextStyle(
                        color: total < 0 ? Colors.red : Colors.green,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    onTap: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => MonthScreen(
                            month: month,
                            expenses: _expenses.where((e) => 
                              '${e.date.year}-${e.date.month.toString().padLeft(2, '0')}' == month
                            ).toList(),
                          ),
                        ),
                      );
                    },
                  ),
                );
              }),
            
            const SizedBox(height: 24),
            
            // Bargeldbezüge
            const Text(
              'Bargeldbezüge',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            if (sortedCashMonths.isEmpty)
              const Text('Keine Bargeldbezüge vorhanden')
            else
              Card(
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Monat')),
                    DataColumn(label: Text('Anzahl')),
                    DataColumn(label: Text('Summe CHF')),
                  ],
                  rows: sortedCashMonths.map((month) {
                    final stats = cashStats[month]!;
                    return DataRow(
                      cells: [
                        DataCell(Text(_formatMonth(month))),
                        DataCell(Text(stats['count'].toString())),
                        DataCell(Text(
                          stats['sum']!.toStringAsFixed(2),
                          style: TextStyle(
                            color: stats['sum']! < 0 ? Colors.red : Colors.green,
                            fontWeight: FontWeight.bold,
                          ),
                        )),
                      ],
                    );
                  }).toList(),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
