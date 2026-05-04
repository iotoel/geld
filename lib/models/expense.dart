class Expense {
  final int id;
  final DateTime date;
  final double price;
  final String description;

  Expense({
    required this.id,
    required this.date,
    required this.price,
    required this.description,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'date': '${date.year.toString().padLeft(4, '0')}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}',
      'price': price,
      'desc': description,
    };
  }

  factory Expense.fromJson(Map<String, dynamic> json) {
    return Expense(
      id: json['id'],
      date: DateTime.parse(json['date']),
      price: json['price'].toDouble(),
      description: json['desc'],
    );
  }

  bool get isCashWithdrawal => description == 'Bezug';
}
