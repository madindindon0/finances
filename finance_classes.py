"""Модель данных приложения «Учёт личных финансов».

Содержит три основных класса:
    * TransactionType — перечисление типов операций (доход/расход);
    * Category        — категория доходов или расходов;
    * Transaction     — отдельная финансовая операция;
    * FinanceManager  — управление операциями и сохранение данных в CSV.
"""

import csv
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Тип финансовой операции."""

    INCOME = "Доход"
    EXPENSE = "Расход"


class Category:
    """Категория доходов или расходов.

    Атрибуты:
        name (str): название категории;
        type (TransactionType): тип операций в категории.
    """

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.name} ({self.type.value})"

    def __repr__(self):
        return f"Category({self.name!r}, {self.type!r})"


class Transaction:
    """Одна финансовая операция.

    Атрибуты:
        amount (float): сумма операции (всегда положительная);
        category (Category): категория операции;
        date (str): дата в формате ГГГГ-ММ-ДД;
        description (str): описание операции.
    """

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(self, amount, category, date, description=""):
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def is_valid_date(self):
        """Проверяет, что дата задана в формате ГГГГ-ММ-ДД."""
        try:
            datetime.strptime(self.date, self.DATE_FORMAT)
            return True
        except (TypeError, ValueError):
            return False

    def is_valid_amount(self):
        """Проверяет, что сумма является положительным числом."""
        try:
            return float(self.amount) > 0
        except (TypeError, ValueError):
            return False

    def to_row(self):
        """Превращает операцию в строку для записи в CSV."""
        return [
            f"{float(self.amount):.2f}",
            self.category.name,
            self.category.type.value,
            self.date,
            self.description,
        ]

    @classmethod
    def from_row(cls, row, categories):
        """Восстанавливает операцию из строки CSV.

        Если категории из файла ещё нет в списке categories, она создаётся
        автоматически по типу операции, указанному в файле.
        """
        category_name = (row.get("Category") or "").strip()
        type_value = (row.get("Type") or "").strip()

        category = next((cat for cat in categories if cat.name == category_name), None)
        if category is None:
            try:
                category_type = TransactionType(type_value)
            except ValueError:
                category_type = (
                    TransactionType.INCOME
                    if float(row.get("Amount") or 0) >= 0
                    else TransactionType.EXPENSE
                )
            category = Category(category_name, category_type)
            categories.append(category)

        return cls(
            amount=float(row.get("Amount") or 0),
            category=category,
            date=(row.get("Date") or "").strip(),
            description=(row.get("Description") or "").strip(),
        )

    def __str__(self):
        sign = "+" if self.category.type == TransactionType.INCOME else "-"
        return f"{self.date} {self.category.name}: {sign}{self.amount:.2f} руб."


class FinanceManager:
    """Управляет списком операций и сохранением данных в CSV-файл."""

    FIELDNAMES = ["Amount", "Category", "Type", "Date", "Description"]

    def __init__(self, filename="transactions.csv"):
        self.filename = filename
        self.transactions = []
        self.categories = [
            Category("Зарплата", TransactionType.INCOME),
            Category("Инвестиции", TransactionType.INCOME),
            Category("Продукты", TransactionType.EXPENSE),
            Category("Транспорт", TransactionType.EXPENSE),
            Category("Развлечения", TransactionType.EXPENSE),
        ]
        self.load_from_file()

    # ------------------------------------------------------------------
    # Операции с транзакциями
    # ------------------------------------------------------------------
    def add_transaction(self, transaction):
        """Добавляет операцию и сохраняет изменения в файл."""
        self.transactions.append(transaction)
        self.save_to_file()

    def delete_transaction(self, index):
        """Удаляет операцию по индексу и сохраняет изменения в файл."""
        if 0 <= index < len(self.transactions):
            del self.transactions[index]
            self.save_to_file()
            return True
        return False

    def get_income(self):
        """Сумма всех доходов."""
        return sum(
            t.amount
            for t in self.transactions
            if t.category.type == TransactionType.INCOME
        )

    def get_expenses(self):
        """Сумма всех расходов."""
        return sum(
            t.amount
            for t in self.transactions
            if t.category.type == TransactionType.EXPENSE
        )

    def get_balance(self):
        """Текущий баланс: доходы минус расходы."""
        return self.get_income() - self.get_expenses()

    def get_category_summary(self):
        """Суммы по категориям.

        Расходы учитываются со знаком минус, доходы — со знаком плюс.
        """
        summary = {}
        for transaction in self.transactions:
            cat_name = transaction.category.name
            summary.setdefault(cat_name, 0.0)
            if transaction.category.type == TransactionType.INCOME:
                summary[cat_name] += transaction.amount
            else:
                summary[cat_name] -= transaction.amount
        return summary

    def get_category_type(self, name):
        """Возвращает тип категории по её названию (или None)."""
        category = next((cat for cat in self.categories if cat.name == name), None)
        return category.type if category else None

    # ------------------------------------------------------------------
    # Работа с файлом
    # ------------------------------------------------------------------
    def save_to_file(self):
        """Записывает все операции в CSV-файл."""
        with open(self.filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            for transaction in self.transactions:
                writer.writerow(
                    {
                        "Amount": f"{float(transaction.amount):.2f}",
                        "Category": transaction.category.name,
                        "Type": transaction.category.type.value,
                        "Date": transaction.date,
                        "Description": transaction.description,
                    }
                )

    def load_from_file(self):
        """Загружает операции из CSV-файла при запуске приложения."""
        self.transactions = []
        try:
            with open(self.filename, "r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not any((value or "").strip() for value in row.values()):
                        continue
                    try:
                        transaction = Transaction.from_row(row, self.categories)
                    except (TypeError, ValueError):
                        # Пропускаем повреждённую строку, не прерывая загрузку.
                        continue
                    self.transactions.append(transaction)
        except FileNotFoundError:
            self.transactions = []
