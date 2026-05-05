import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/expense.dart';

class DataService {
  static const String _expensesKey = 'expenses';
  static const String _passwordKey = 'password';

  static Future<List<Expense>> getExpenses() async {
    final prefs = await SharedPreferences.getInstance();
    final expensesJson = prefs.getString(_expensesKey) ?? '[]';
    
    final List<dynamic> expensesList = json.decode(expensesJson);
    return expensesList.map((json) => Expense.fromJson(json)).toList();
  }

  static Future<void> saveExpenses(List<Expense> expenses) async {
    final prefs = await SharedPreferences.getInstance();
    final expensesJson = json.encode(expenses.map((e) => e.toJson()).toList());
    await prefs.setString(_expensesKey, expensesJson);
  }

  static Future<Expense> addExpense(Expense expense) async {
    final expenses = await getExpenses();
    final newId = expenses.isEmpty ? 1 : expenses.map((e) => e.id).reduce((a, b) => a > b ? a : b) + 1;
    
    final newExpense = Expense(
      id: newId,
      date: expense.date,
      price: expense.price,
      description: expense.description,
    );
    
    expenses.add(newExpense);
    await saveExpenses(expenses);
    return newExpense;
  }

  static Future<void> updateExpense(Expense expense) async {
    final expenses = await getExpenses();
    final index = expenses.indexWhere((e) => e.id == expense.id);
    
    if (index != -1) {
      expenses[index] = expense;
      await saveExpenses(expenses);
    }
  }

  static Future<void> deleteExpense(int id) async {
    final expenses = await getExpenses();
    expenses.removeWhere((e) => e.id == id);
    await saveExpenses(expenses);
  }

  static Future<String?> getPassword() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_passwordKey);
  }

  static Future<void> setPassword(String password) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_passwordKey, password);
  }

  static Future<bool> isPasswordSet() async {
    final password = await getPassword();
    return password != null && password.isNotEmpty;
  }

  static Future<void> resetPassword() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_passwordKey);
  }

  static Future<void> resetAllData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_expensesKey);
    await prefs.remove(_passwordKey);
  }
}
