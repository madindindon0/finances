"""Графический интерфейс приложения «Учёт личных финансов» (Tkinter)."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from finance_classes import FinanceManager, Transaction


class FinanceApp:
    """Окно приложения: форма ввода, таблица операций и аналитика."""

    def __init__(self, root):
        self.root = root
        self.manager = FinanceManager()
        self.root.title("Учёт личных финансов")
        self.root.geometry("900x650")
        self.root.minsize(760, 520)
        self.setup_ui()

    # ------------------------------------------------------------------
    # Построение интерфейса
    # ------------------------------------------------------------------
    def setup_ui(self):
        """Создаёт все элементы окна."""
        self.setup_input_frame()
        self.setup_info_frame()
        self.setup_table_frame()

    def setup_input_frame(self):
        """Форма добавления операции."""
        input_frame = ttk.LabelFrame(self.root, text="Добавить операцию", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(3, weight=1)

        ttk.Label(input_frame, text="Сумма (руб.):").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 5), pady=3
        )
        self.amount_entry = ttk.Entry(input_frame)
        self.amount_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=3)

        ttk.Label(input_frame, text="Категория:").grid(
            row=0, column=2, sticky=tk.W, padx=(15, 5), pady=3
        )
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=[cat.name for cat in self.manager.categories],
            state="readonly",
        )
        self.category_combo.grid(row=0, column=3, sticky=tk.EW, padx=5, pady=3)
        if self.manager.categories:
            self.category_combo.current(0)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 5), pady=3
        )
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=3)

        ttk.Label(input_frame, text="Описание:").grid(
            row=1, column=2, sticky=tk.W, padx=(15, 5), pady=3
        )
        self.desc_entry = ttk.Entry(input_frame)
        self.desc_entry.grid(row=1, column=3, sticky=tk.EW, padx=5, pady=3)

        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))

        ttk.Button(
            button_frame, text="Добавить операцию", command=self.add_transaction
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="Удалить выбранную", command=self.delete_transaction
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame, text="Показать аналитику", command=self.show_analytics
        ).pack(side=tk.LEFT, padx=5)

        self.amount_entry.focus_set()
        self.root.bind("<Return>", lambda event: self.add_transaction())

    def setup_info_frame(self):
        """Панель с балансом и итогами."""
        info_frame = ttk.LabelFrame(self.root, text="Финансовая информация", padding=10)
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.balance_label = ttk.Label(info_frame, text="", font=("Arial", 13, "bold"))
        self.balance_label.pack(side=tk.LEFT, padx=5)

        self.count_label = ttk.Label(info_frame, text="", font=("Arial", 10))
        self.count_label.pack(side=tk.RIGHT, padx=5)

        self.update_balance()

    def setup_table_frame(self):
        """Таблица с историей операций."""
        table_frame = ttk.LabelFrame(self.root, text="История операций", padding=10)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        columns = ("date", "category", "type", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("category", text="Категория")
        self.tree.heading("type", text="Тип")
        self.tree.heading("amount", text="Сумма, руб.")
        self.tree.heading("description", text="Описание")

        self.tree.column("date", width=110, anchor=tk.CENTER)
        self.tree.column("category", width=150, anchor=tk.W)
        self.tree.column("type", width=90, anchor=tk.CENTER)
        self.tree.column("amount", width=120, anchor=tk.E)
        self.tree.column("description", width=300, anchor=tk.W)

        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Delete>", lambda event: self.delete_transaction())
        self.update_table()

    # ------------------------------------------------------------------
    # Действия пользователя
    # ------------------------------------------------------------------
    def add_transaction(self):
        """Читает форму, проверяет данные и добавляет операцию."""
        amount_text = self.amount_entry.get().strip().replace(",", ".")
        category_name = self.category_var.get().strip()
        date_text = self.date_entry.get().strip()
        description = self.desc_entry.get().strip()

        try:
            amount = float(amount_text)
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректную сумму!")
            return

        if amount <= 0:
            messagebox.showerror("Ошибка", "Сумма должна быть больше нуля!")
            return

        if not category_name:
            messagebox.showwarning("Ошибка", "Выберите категорию!")
            return

        category = next(
            (cat for cat in self.manager.categories if cat.name == category_name), None
        )
        if category is None:
            messagebox.showwarning("Ошибка", "Выберите корректную категорию!")
            return

        transaction = Transaction(amount, category, date_text, description)
        if not transaction.is_valid_date():
            messagebox.showerror("Ошибка", "Дата должна быть в формате ГГГГ-ММ-ДД!")
            return

        self.manager.add_transaction(transaction)
        self.update_table()
        self.update_balance()
        self.clear_inputs()

    def delete_transaction(self):
        """Удаляет выбранную в таблице операцию."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Удаление", "Выберите операцию в таблице.")
            return

        index = int(selected[0])
        transaction = self.manager.transactions[index]
        if messagebox.askyesno(
            "Удаление",
            f"Удалить операцию «{transaction.description or transaction.category.name}» "
            f"на сумму {transaction.amount:.2f} руб.?",
        ):
            self.manager.delete_transaction(index)
            self.update_table()
            self.update_balance()

    def show_analytics(self):
        """Открывает отдельное окно с аналитикой по категориям."""
        summary = self.manager.get_category_summary()
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Аналитика по категориям")
        analytics_window.geometry("460x420")
        analytics_window.transient(self.root)

        totals_frame = ttk.LabelFrame(
            analytics_window, text="Итоги", padding=10
        )
        totals_frame.pack(fill=tk.X, padx=10, pady=10)

        income = self.manager.get_income()
        expenses = self.manager.get_expenses()
        balance = self.manager.get_balance()

        ttk.Label(
            totals_frame, text=f"Доходы: {income:.2f} руб.", foreground="green"
        ).pack(anchor=tk.W)
        ttk.Label(
            totals_frame, text=f"Расходы: {expenses:.2f} руб.", foreground="red"
        ).pack(anchor=tk.W)
        ttk.Label(
            totals_frame,
            text=f"Баланс: {balance:.2f} руб.",
            font=("Arial", 11, "bold"),
            foreground="green" if balance >= 0 else "red",
        ).pack(anchor=tk.W, pady=(5, 0))

        table_frame = ttk.LabelFrame(
            analytics_window, text="Суммы по категориям", padding=10
        )
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        columns = ("category", "type", "amount")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        tree.heading("category", text="Категория")
        tree.heading("type", text="Тип")
        tree.heading("amount", text="Сумма, руб.")
        tree.column("category", width=180)
        tree.column("type", width=90, anchor=tk.CENTER)
        tree.column("amount", width=120, anchor=tk.E)
        tree.tag_configure("income", foreground="green")
        tree.tag_configure("expense", foreground="red")

        scrollbar = ttk.Scrollbar(
            table_frame, orient=tk.VERTICAL, command=tree.yview
        )
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)

        if not summary:
            ttk.Label(
                table_frame, text="Операций пока нет."
            ).pack(padx=10, pady=10)
        else:
            for category_name, amount in sorted(summary.items()):
                category_type = self.manager.get_category_type(category_name)
                type_name = category_type.value if category_type else ""
                tag = "income" if amount >= 0 else "expense"
                tree.insert(
                    "",
                    tk.END,
                    values=(category_name, type_name, f"{amount:.2f}"),
                    tags=(tag,),
                )

        ttk.Button(analytics_window, text="Закрыть", command=analytics_window.destroy).pack(
            pady=(0, 10)
        )

    # ------------------------------------------------------------------
    # Обновление интерфейса
    # ------------------------------------------------------------------
    def update_table(self):
        """Перерисовывает таблицу операций."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for index, transaction in enumerate(self.manager.transactions):
            self.tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    transaction.date,
                    transaction.category.name,
                    transaction.category.type.value,
                    f"{transaction.amount:.2f}",
                    transaction.description,
                ),
            )

    def update_balance(self):
        """Обновляет метку баланса и счётчик операций."""
        balance = self.manager.get_balance()
        color = "green" if balance >= 0 else "red"
        self.balance_label.config(
            text=f"Текущий баланс: {balance:.2f} руб.", foreground=color
        )
        self.count_label.config(text=f"Всего операций: {len(self.manager.transactions)}")

    def clear_inputs(self):
        """Очищает поля формы после добавления операции."""
        self.amount_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.amount_entry.focus_set()


def main():
    root = tk.Tk()
    FinanceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
