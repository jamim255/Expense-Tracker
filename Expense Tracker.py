import os
import csv
import calendar
import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

class Expense:
    def __init__(self, name, category, amount, date):
        self.name = name
        self.category = category
        self.amount = amount
        self.date = date

class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("700x550")

        self.expenses = []
        self.budget = 0.0
        self.expense_file_path = None

        self.create_ui()

    def create_ui(self):
        # Action buttons
        frame_btn = tk.Frame(self.root)
        frame_btn.pack(pady=10)
        tk.Button(frame_btn, text="Create New List", width=20, command=self.create_file).grid(row=0, column=0, padx=6)
        tk.Button(frame_btn, text="Add Expense to Existing List", width=22, command=self.load_file_and_add_expense).grid(row=0, column=1, padx=6)
        tk.Button(frame_btn, text="Summarize Expenses", width=20, command=self.summarize_expenses).grid(row=0, column=2, padx=6)

        # Expense table
        columns = ("Name", "Category", "Amount", "Date")
        self.expense_table = ttk.Treeview(self.root, columns=columns, show="headings", height=15)
        for col in columns:
            self.expense_table.heading(col, text=col)
            self.expense_table.column(col, width=130)
        self.expense_table.pack(pady=16, fill=tk.X)

        # Summary Label
        self.summary_label = tk.Label(self.root, text="", justify="left", font=("Arial", 12), fg="#1f7ed7")
        self.summary_label.pack(pady=6)

    def create_file(self):
        file_name = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_name:
            if os.path.exists(file_name):
                overwrite = messagebox.askyesno("File Exists", "File already exists. Overwrite?")
                if not overwrite:
                    return
            with open(file_name, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Category", "Amount", "Date"])
            budget = simpledialog.askfloat("Budget", "Enter your budget for this file (BDT):")
            if budget is not None:
                self.budget = budget
                with open(file_name, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Budget", self.budget])
                self.expense_file_path = file_name
                self.expenses = []
                self.update_expense_table()
                self.update_summary()
                messagebox.showinfo("File Created", f"File created with budget: BDT {self.budget}")
            else:
                messagebox.showerror("Error", "Budget not set.")

    def load_file_and_add_expense(self):
        file_name = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_name:
            self.expense_file_path = file_name
            self.budget = self.load_budget_from_file()
            self.load_expenses_from_file()
            self.update_expense_table()
            self.update_summary()
            self.add_expense()

    def add_expense(self):
        if not self.expense_file_path:
            messagebox.showerror("Error", "Please create or load a file first.")
            return

        name = simpledialog.askstring("Expense", "Enter expense name:")
        if not name:
            return
        try:
            amount = float(simpledialog.askfloat("Expense", "Enter expense amount (BDT):"))
        except Exception:
            messagebox.showerror("Error", "Invalid amount.")
            return
        categories = ["Food", "Home", "Work", "Fun", "Misc"]
        category = simpledialog.askstring("Expense", f"Enter category ({', '.join(categories)}):")
        if not category or category not in categories:
            messagebox.showerror("Error", f"Invalid category! Choose from {', '.join(categories)}.")
            return
        date = str(datetime.date.today())
        expense = Expense(name=name, category=category, amount=amount, date=date)
        self.expenses.append(expense)
        with open(self.expense_file_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([expense.name, expense.category, expense.amount, expense.date])
        self.update_expense_table()
        self.update_summary()
        messagebox.showinfo("Success", "Expense added successfully!")

    def summarize_expenses(self):
        file_name = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_name:
            self.expense_file_path = file_name
            self.budget = self.load_budget_from_file()
            self.load_expenses_from_file()
            self.update_expense_table()
            self.update_summary()

    def update_expense_table(self):
        for row in self.expense_table.get_children():
            self.expense_table.delete(row)
        for expense in self.expenses:
            self.expense_table.insert("", tk.END, values=(expense.name, expense.category, f"{expense.amount:.2f}", expense.date))

    def update_summary(self):
        total_spent = sum(exp.amount for exp in self.expenses)
        remaining_budget = self.budget - total_spent
        now = datetime.datetime.now()
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        remaining_days = days_in_month - now.day
        daily_budget = remaining_budget / remaining_days if remaining_days > 0 else 0.0
        summary_text = (
            f"Total Spent: BDT {total_spent:.2f}\n"
            f"Remaining Budget: BDT {remaining_budget:.2f}\n"
            f"Daily Budget: BDT {daily_budget:.2f} (for remaining {remaining_days} days)"
        )
        self.summary_label.config(text=summary_text)

    def load_expenses_from_file(self):
        self.expenses = []
        if self.expense_file_path and os.path.exists(self.expense_file_path):
            with open(self.expense_file_path, "r") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) == 4:
                        name, category, amount, date = row
                        if name != "Budget":
                            try:
                                amount = float(amount)
                                self.expenses.append(Expense(name, category, amount, date))
                            except ValueError:
                                continue

    def load_budget_from_file(self):
        if self.expense_file_path and os.path.exists(self.expense_file_path):
            with open(self.expense_file_path, "r") as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and row[0] == "Budget":
                        try:
                            return float(row[1])
                        except ValueError:
                            return 0.0
        return 0.0

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()
