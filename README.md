# 🎓 PocketTrack — Student Expense Tracker

A clean, fast, personal expense tracker for students. Track your pocket money, daily expenses, and money with friends — all stored locally on your laptop.

---

## ✨ Features

- **Dashboard** — Balance, safe daily spend, category breakdown, recent transactions
- **Smart Daily Budget** — "You can spend ₹___ per day safely" (Balance ÷ Days Left)
- **Friend Money Tracker** — Track who owes you & who you owe with partial payments
- **Fast Add** — Add an expense in under 3 seconds
- **Password Lock** — PIN/password protection on every launch
- **Monthly Backups** — Auto-exports SQL backup at month start, manual backup anytime
- **All data local** — Stored in your own PostgreSQL database on your laptop

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL (installed and running locally)

### Installation

```bash
# 1. Clone / download the project
cd student-expense-tracker

# 2. Run setup (installs deps, creates DB, initializes schema)
python setup.py

# 3. Start the app
python run.py

# 4. Open in browser
# http://localhost:5000
```

### First Launch
- You'll be prompted to **create a password** on first visit
- This password protects your data every time you open the app

---

## 📁 Project Structure

```
student-expense-tracker/
├── run.py                      # ← Start the app with this
├── setup.py                    # ← Run once for first-time setup
├── requirements.txt
│
├── config/
│   └── config.py               # Database credentials & settings
│
├── frontend/
│   ├── index.html              # Single-page app
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js              # All API calls
│       ├── ui.js               # Shared UI helpers
│       ├── dashboard.js        # Dashboard logic
│       ├── friends.js          # Friend pages logic
│       └── add.js              # Add page + auth
│
├── backend/
│   ├── app.py                  # Flask app setup
│   ├── models/
│   │   └── db.py               # Database connection
│   ├── routes/
│   │   ├── auth_routes.py      # /api/auth/*
│   │   ├── transaction_routes.py # /api/transactions/*
│   │   ├── friend_routes.py    # /api/friends/*
│   │   └── backup_routes.py    # /api/backup/*
│   └── services/
│       ├── auth_service.py     # Password logic
│       ├── transaction_service.py # Balance, category, daily spend
│       ├── friend_service.py   # Borrow/lend logic
│       └── backup_service.py   # pg_dump backups
│
├── database/
│   └── schema.sql              # PostgreSQL table definitions
│
└── backups/                    # Auto-saved monthly .sql files
    └── 2026_04.sql             # (created automatically)
```

---

## 📊 Database Tables

| Table | Purpose |
|-------|---------|
| `users` | Stores password hash |
| `transactions` | All income & expense entries |
| `friends` | Unique friend names |
| `friend_transactions` | Money owed/to-receive per friend |

---

## 💡 How It Works

### Daily Safe Spend
```
Safe Daily Spend = Remaining Balance / Days Left in Month
```
Updated live on every page load.

### Friend Logic
- Friends are stored **uniquely by name** — "Rahul" from different entries links to the same friend
- **Partial payments** supported: pay ₹30 of ₹100 owed, remaining = ₹70
- Status auto-updates to `completed` when remaining = 0

### Monthly Backup
- On the **1st of each month**, the app auto-creates a backup of the previous month
- Manual backup available anytime from Settings
- Saved as `/backups/YYYY_MM.sql` using `pg_dump`

---

## ⚙️ Configuration

Edit `config/config.py` to change database settings:

```python
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "student_expense_tracker"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
```

---

## 🔒 Security

- Password stored as **SHA-256 hash** (never plain text)
- Session-based authentication
- All data stays on your local machine — nothing is sent anywhere

---

## 🛠 Troubleshooting

**"Database connection failed"**
→ Make sure PostgreSQL is running: `pg_ctl start` or open pgAdmin

**"pg_dump not found" on backup**
→ Install PostgreSQL client tools, or add pg_dump to your PATH

**Port 5000 already in use**
→ Change port in `run.py`: `app.run(port=5001)`

**Forgot password**
→ Run in PostgreSQL: `DELETE FROM users;` — then restart the app to set a new one

---

## 📱 Usage Tips

- **Add an expense fast**: Tap `+` → type amount → select category → Done (3 taps)
- **Father sent money**: Tap `+` → Income tab → enter amount
- **Split with friend**: Tap `+` → Friend tab → fill details
- **Check how much to spend today**: Always visible on the Dashboard banner

---

Built with ❤️ for students who want to manage money without overcomplicating it.
