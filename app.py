import os
import subprocess
import bcrypt
from datetime import datetime
import json
import logging

_log_handler = logging.FileHandler("seguridad_atm.log", encoding="utf-8")
_log_handler.setFormatter(logging.Formatter("[%(asctime)s - %(message)s]", datefmt="%Y-%m-%d %H:%M:%S"))
logger = logging.getLogger("ATM")
logger.setLevel(logging.INFO)
logger.addHandler(_log_handler)

class ATM:
    def __init__(self, account):
        self.account = account

    def show_balance(self):
        print(f"Your balance is: ${self.account.balance:.2f}")

    def deposit(self, amount):
        try:
            float_amount = self.string_to_float(amount)
            
            if float_amount == None:
                raise ValueError("Invalid input. Please enter a numeric value.")
            if float_amount <= 0:
                raise ValueError("Deposit amount must be greater than zero.")
            
            self.account.balance += float_amount
            self.account.add_transaction("Deposit", float_amount)
            logger.info(f"DEPOSITO - {self.account.account_number} - ${float_amount:.2f} | Balance: ${self.account.balance:.2f}")
            print(f"You have deposited: ${float_amount:.2f}")
            
        except ValueError as e:
            print(e)
        except Exception as e:
            print(e)

    def withdraw(self, amount):
        try:
            float_amount = self.string_to_float(amount)
            
            if float_amount == None:
                raise ValueError("Invalid input. Please enter a numeric value.")
            if float_amount <= 0:
                raise ValueError("Withdrawal amount must be greater than zero.")
            if float_amount > self.account.balance:
                logger.warning(f"FONDOS_INSUFICIENTES - {self.account.account_number} - Retiro ${float_amount:.2f} rechazado")
                raise ValueError("Insufficient funds.")

            remaining = self.account.DAILY_LIMIT - self.account.daily_withdrawn
            if float_amount > remaining:
                logger.warning(f"LIMITE_DIARIO - {self.account.account_number} - Retiro ${float_amount:.2f} rechazado. Restante: ${remaining:.2f}")
                raise ValueError(
                    f"Daily withdrawal limit of ${self.account.DAILY_LIMIT:.2f} exceeded. "
                    f"Remaining today: ${remaining:.2f}"
                )

            if float_amount > 0.8 * self.account.balance:
                logger.warning(f"ACTIVIDAD_SOSPECHOSA - {self.account.account_number} - Retiro ${float_amount:.2f} supera el 80% del saldo (${self.account.balance:.2f})")

            self.account.balance -= float_amount
            self.account.add_transaction("Withdrawal", float_amount)
            logger.info(f"RETIRO - {self.account.account_number} - ${float_amount:.2f} | Balance: ${self.account.balance:.2f}")
            print(f"Please take your cash: ${float_amount:.2f}")
        except ValueError as e:
            print(e)
        except Exception as e:
            print(e)
            print("Insufficient funds.")
            
    def string_to_float(self, value):
        try:
            return float(value)
        except ValueError:
            print("Invalid input. Please enter a numeric value.")
            return None

    def show_transactions(self):
        if not self.account.transactions:
            print("No transactions yet.")
            return

        for transaction in self.account.transactions:
            timestamp = transaction["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} | {transaction['type']:<10} | ${transaction['amount']:.2f} | Balance: ${transaction['balance_after']:.2f}")

class App:
    def __init__(self, atm):
        self.atm = atm

    def show_menu(self):
        self.clear_screen()
        print("==========================================")
        print("           🏦 Welcome to the bank!          ")
        print("==========================================")
        print("[1] 💸 Show balance")
        print("[2] 💰 Deposit")
        print("[3] 💳 Withdraw")
        print("[4] 📜 Transaction history")
        print("[5] 🚪 Exit")
        print("==========================================")
        
    def pause(self):
        input("Press Enter to continue...")
    
    def clear_screen(self):
        command = 'cls' if os.name == 'nt' else 'clear'
        subprocess.call(command, shell=True)
        
    def main():
        account = BankAccount.load()
        if account is None:
            account = BankAccount("4111111111111111", 1000.00, "1234")
            account.save()

        print("==========================================")
        print("           🏦 Welcome to the bank!          ")
        print("==========================================")

        authenticated = False
        while not account.locked and not authenticated:
            entered_number = input("Card number: ")

            if not BankAccount.luhn_check(entered_number):
                logger.warning(f"LUHN_INVALIDO - {entered_number} - Número de tarjeta no pasa validación Luhn")
                print("Invalid card number format.")
                continue

            if entered_number != account.account_number:
                logger.warning(f"TARJETA_NO_ENCONTRADA - {entered_number} - Número de tarjeta no encontrada")
                print("Card number not found.")
                continue

            entered_password = input("Password: ")
            authenticated = account.authenticate(entered_password)

        if not authenticated:
            print("Access denied. Goodbye.")
            return

        logger.info(f"SESION_INICIO - {account.account_number} - Sesión iniciada")
        atm = ATM(account)
        app = App(atm)

        while True:
            app.show_menu()
            option = input("Please choose an option: ")
            print("==========================================")
            
            match option:
   
    
                case "1":
                    atm.show_balance()
                    app.pause()
                case "2":
                    amount = input("Enter the amount to deposit: ")
                    atm.deposit(amount)
                    app.pause()
                case "3":
                    amount = input("Enter the amount to withdraw: ")
                    atm.withdraw(amount)
                    app.pause()
                case "4":
                    atm.show_transactions()
                    app.pause()
                case "5":
                    logger.info(f"SESION_FIN - {account.account_number} - Sesión cerrada")
                    app.clear_screen()
                    print("Thank you for using the bank. Goodbye 🖐️!")
                    break
                case _:        
                    print("⚠️Invalid option, please try again.")
                    app.pause()      
                    
                    
class BankAccount:
    DATA_FILE = "accounts.json"
    DAILY_LIMIT = 2000.0

    def __init__(self, account_number, balance, password=None, password_hash=None):
        self.account_number = account_number
        self.balance = balance
        self.password_hash = password_hash if password_hash else self._hash_password(password)
        self.failed_attempts = 0
        self.locked = False
        self.transactions = []

    @staticmethod
    def luhn_check(card_number: str) -> bool:
        digits = [int(d) for d in card_number if d.isdigit()]
        if not (13 <= len(digits) <= 19):
            return False
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 1:
                digit *= 2
                if digit > 9:
                    digit -= 9
            total += digit
        return total % 10 == 0

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def _verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

    def authenticate(self, password):
        if self.locked:
            logger.warning(f"BLOQUEO - {self.account_number} - Intento de acceso a cuenta bloqueada")
            print("Account locked due to too many failed attempts.")
            return False

        if self._verify_password(password):
            self.failed_attempts = 0
            self.save()
            logger.info(f"LOGIN_OK - {self.account_number} - Contraseña correcta")
            return True

        self.failed_attempts += 1
        if self.failed_attempts >= 3:
            self.locked = True
            logger.warning(f"BLOQUEO - {self.account_number} - Cuenta bloqueada por 3 intentos fallidos")
            print("Account locked due to too many failed attempts.")
        else:
            logger.warning(f"LOGIN_FAIL - {self.account_number} - Contraseña incorrecta. Intentos: {self.failed_attempts}/3")
            print(f"Incorrect password. Attempts remaining: {3 - self.failed_attempts}")
        self.save()
        return False

    @property
    def daily_withdrawn(self):
        today = datetime.now().date()
        return sum(
            t["amount"] for t in self.transactions
            if t["type"] == "Withdrawal" and t["timestamp"].date() == today
        )

    def add_transaction(self, transaction_type, amount):
        self.transactions.append({
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "timestamp": datetime.now()
        })
        self.save()

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "balance": self.balance,
            "password_hash": self.password_hash,
            "failed_attempts": self.failed_attempts,
            "locked": self.locked,
            "transactions": [
                {**t, "timestamp": t["timestamp"].isoformat()}
                for t in self.transactions
            ],
        }

    def save(self):
        with open(self.DATA_FILE, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data):
        account = cls(
            data["account_number"],
            data["balance"],
            password_hash=data["password_hash"]
        )
        account.failed_attempts = data["failed_attempts"]
        account.locked = data["locked"]
        account.transactions = [
            {**t, "timestamp": datetime.fromisoformat(t["timestamp"])}
            for t in data["transactions"]
        ]
        return account

    @classmethod
    def load(cls):
        if not os.path.exists(cls.DATA_FILE):
            return None
        with open(cls.DATA_FILE, "r") as f:
            return cls.from_dict(json.load(f))

if __name__ == "__main__":    App.main()
        
