
from flask import (
    Flask, request, redirect, url_for,
    render_template_string, send_from_directory
)
from datetime import datetime
from itertools import count
from pathlib import Path

app = Flask(__name__, static_folder="static", template_folder=".")

# --------------------------------------------------
# BoliBiz AI - Demo data
# Note: In-memory data resets when the server restarts.
# --------------------------------------------------

transactions = [
    {
        "id": 1,
        "type": "Income",
        "description": "Product Sales",
        "amount": 2500.00,
        "date": datetime.now().strftime("%Y-%m-%d")
    },
    {
        "id": 2,
        "type": "Expense",
        "description": "Shop Supplies",
        "amount": 600.00,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
]

proposals = []
transaction_ids = count(3)
proposal_ids = count(1)


# --------------------------------------------------
# Shared design and navigation
# --------------------------------------------------

BASE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{{ title }} | BoliBiz AI</title>

    <meta name="theme-color" content="#17663d">
    <meta name="description"
          content="BoliBiz AI helps small businesses manage sales,
                   expenses, reports and business proposals.">

    <link rel="manifest" href="/manifest.json">
    <link rel="icon" href="/static/icon-192.png" type="image/png">

    <style>
        :root {
            --green: #17663d;
            --green-dark: #104b2c;
            --green-light: #e6f4e9;
            --cream: #f5f7f0;
            --white: #ffffff;
            --text: #23352b;
            --muted: #718076;
            --border: #e2e9e1;
            --red: #c0392b;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: var(--cream);
            color: var(--text);
        }

        header {
            background: var(--white);
            border-bottom: 1px solid var(--border);
            padding: 16px 5%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
        }

        .brand {
            color: var(--green);
            font-size: 23px;
            font-weight: 800;
            text-decoration: none;
        }

        .brand span {
            color: #d89b28;
        }

        nav {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }

        nav a {
            text-decoration: none;
            color: var(--text);
            padding: 9px 12px;
            border-radius: 9px;
            font-size: 14px;
        }

        nav a:hover, nav a.active {
            background: var(--green-light);
            color: var(--green);
        }

        main {
            max-width: 1150px;
            margin: 30px auto;
            padding: 0 20px;
        }

        h1 {
            font-size: 30px;
            margin: 0 0 8px;
        }

        h2 {
            font-size: 20px;
        }

        .muted {
            color: var(--muted);
            line-height: 1.6;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin: 25px 0;
        }

        .card {
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(20, 60, 35, 0.03);
        }

        .stat-label {
            color: var(--muted);
            font-size: 14px;
        }

        .stat-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 10px;
            overflow-wrap: anywhere;
        }

        .positive {
            color: var(--green);
        }

        .negative {
            color: var(--red);
        }

        .button, button {
            display: inline-block;
            background: var(--green);
            color: white;
            border: none;
            padding: 12px 17px;
            border-radius: 9px;
            text-decoration: none;
            cursor: pointer;
            font-size: 14px;
        }

        .button:hover, button:hover {
            background: var(--green-dark);
        }

        .button.secondary {
            background: var(--green-light);
            color: var(--green);
        }

        .button.danger {
            background: #fdebea;
            color: var(--red);
        }

        .actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 18px;
        }

        form {
            display: grid;
            gap: 14px;
        }

        label {
            font-weight: 600;
            font-size: 14px;
        }

        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #d8e1d7;
            border-radius: 9px;
            background: white;
            font: inherit;
            margin-top: 7px;
        }

        textarea {
            resize: vertical;
        }

        .table-wrap {
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            min-width: 540px;
        }

        th, td {
            padding: 14px 10px;
            text-align: left;
            border-bottom: 1px solid var(--border);
            font-size: 14px;
        }

        th {
            color: var(--muted);
        }

        .tag {
            display: inline-block;
            padding: 5px 9px;
            border-radius: 20px;
            background: var(--green-light);
            color: var(--green);
            font-size: 12px;
        }

        .message {
            background: var(--green-light);
            padding: 15px;
            border-radius: 10px;
            line-height: 1.7;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }

        footer {
            padding: 25px 20px;
            text-align: center;
            color: var(--muted);
            font-size: 13px;
        }

        #installBtn {
            display: none;
            margin-left: 5%;
            margin-top: 12px;
        }

        @media (max-width: 720px) {
            header {
                padding: 15px 20px;
            }

            nav {
                width: 100%;
            }

            nav a {
                padding: 8px;
                font-size: 13px;
            }

            main {
                margin-top: 22px;
                padding: 0 15px;
            }

            h1 {
                font-size: 25px;
            }

            .grid {
                grid-template-columns: 1fr;
                gap: 12px;
            }

            .stat-value {
                font-size: 25px;
            }
        }
    </style>
</head>

<body>
<header>
    <a class="brand" href="{{ url_for('dashboard') }}">
        BoliBiz <span>AI</span>
    </a>

    <nav>
        <a href="{{ url_for('dashboard') }}">Dashboard</a>
        <a href="{{ url_for('transactions_page') }}">Transactions</a>
        <a href="{{ url_for('reports') }}">Reports</a>
        <a href="{{ url_for('proposals_page') }}">Proposals</a>
        <a href="{{ url_for('assistant') }}">AI Assistant</a>
    </nav>
</header>

<button id="installBtn" type="button">Install BoliBiz AI</button>

<main>
    {{ content|safe }}
</main>

<footer>
    BoliBiz AI · Your small-business companion
</footer>

<script>
    // Register the service worker for supported browsers.
    if ("serviceWorker" in navigator) {
        window.addEventListener("load", function () {
            navigator.serviceWorker.register("/service-worker.js")
                .catch(function (error) {
                    console.log("Service worker registration failed:", error);
                });
        });
    }

    // Show the install button when the browser supports installation.
    let installPrompt = null;
    const installButton = document.getElementById("installBtn");

    window.addEventListener("beforeinstallprompt", function (event) {
        event.preventDefault();
        installPrompt = event;
        installButton.style.display = "inline-block";
    });

    installButton.addEventListener("click", async function () {
        if (!installPrompt) {
            alert(
                "If installation is supported, use your browser menu " +
                "and choose Install app or Add to Home screen."
            );
            return;
        }

        installPrompt.prompt();
        await installPrompt.userChoice;
        installPrompt = null;
        installButton.style.display = "none";
    });
</script>
</body>
</html>
"""


def page(title, content):
    return render_template_string(
        BASE,
        title=title,
        content=content
    )


def money(value):
    return f"₹{value:,.2f}"


def totals():
    income = sum(
        t["amount"] for t in transactions if t["type"] == "Income"
    )
    expenses = sum(
        t["amount"] for t in transactions if t["type"] == "Expense"
    )
    return income, expenses, income - expenses


# --------------------------------------------------
# PWA files
# --------------------------------------------------

@app.route("/manifest.json")
def manifest():
    return send_from_directory(".", "manifest.json")


@app.route("/service-worker.js")
def service_worker():
    response = send_from_directory(".", "service-worker.js")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache"
    return response


# --------------------------------------------------
# Home and dashboard
# --------------------------------------------------

@app.route("/")
def home():
    content = """
    <h1>Welcome to BoliBiz AI 👋</h1>
    <p class="muted">
        Your smart business assistant for tracking sales, expenses,
        reports, and business proposals.
    </p>

    <div class="actions">
        <a class="button" href="/dashboard">Open dashboard</a>
        <a class="button secondary" href="/transactions">Manage transactions</a>
    </div>
    """
    return page("Home", content)


@app.route("/dashboard")
def dashboard():
    income, expenses, balance = totals()
    recent = sorted(
        transactions,
        key=lambda t: (t["date"], t["id"]),
        reverse=True
    )[:5]

    rows = "".join(
        f"""
        <tr>
            <td>{t['date']}</td>
            <td>{t['description']}</td>
            <td><span class="tag">{t['type']}</span></td>
            <td>{money(t['amount'])}</td>
        </tr>
        """
        for t in recent
    )

    if not rows:
        rows = '<tr><td colspan="4">No transactions yet.</td></tr>'

    content = f"""
    <h1>Your business at a glance 👋</h1>
    <p class="muted">
        Manage your income, expenses and business ideas in one place.
    </p>

    <div class="grid">
        <section class="card">
            <div class="stat-label">Total Income</div>
            <div class="stat-value positive">{money(income)}</div>
        </section>

        <section class="card">
            <div class="stat-label">Total Expenses</div>
            <div class="stat-value negative">{money(expenses)}</div>
        </section>

        <section class="card">
            <div class="stat-label">Net Balance</div>
            <div class="stat-value">{money(balance)}</div>
        </section>
    </div>

    <section class="card">
        <h2>Quick actions</h2>
        <p class="muted">Choose what you want to do next.</p>
        <div class="actions">
            <a class="button" href="{url_for('transactions_page')}">
                Add transaction
            </a>
            <a class="button secondary" href="{url_for('reports')}">
                View reports
            </a>
            <a class="button secondary" href="{url_for('proposals_page')}">
                Create proposal
            </a>
            <a class="button secondary" href="{url_for('assistant')}">
                Ask AI Assistant
            </a>
        </div>
    </section>

    <section class="card">
        <h2>Recent transactions</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </section>
    """
    return page("Dashboard", content)


# --------------------------------------------------
# Transactions
# --------------------------------------------------

@app.route("/transactions", methods=["GET", "POST"])
def transactions_page():
    if request.method == "POST":
        description = request.form.get("description", "").strip()
        transaction_type = request.form.get("type", "")
        date = request.form.get("date", "").strip()

        try:
            amount = float(request.form.get("amount", "0"))
        except ValueError:
            amount = 0

        if (
            description
            and transaction_type in ("Income", "Expense")
            and amount > 0
            and date
        ):
            transactions.append({
                "id": next(transaction_ids),
                "type": transaction_type,
                "description": description,
                "amount": amount,
                "date": date
            })

        return redirect(url_for("transactions_page"))

    rows = "".join(
        f"""
        <tr>
            <td>{t['date']}</td>
            <td>{t['description']}</td>
            <td><span class="tag">{t['type']}</span></td>
            <td>{money(t['amount'])}</td>
            <td>
                <form method="POST"
                      action="{url_for('delete_transaction',
                                       transaction_id=t['id'])}"
                      onsubmit="return confirm('Delete this transaction?')">
                    <button class="button danger" type="submit">
                        Delete
                    </button>
                </form>
            </td>
        </tr>
        """
        for t in sorted(
            transactions,
            key=lambda t: (t["date"], t["id"]),
            reverse=True
        )
    )

    if not rows:
        rows = '<tr><td colspan="5">No transactions recorded.</td></tr>'

    today = datetime.now().strftime("%Y-%m-%d")

    content = f"""
    <h1>Transactions</h1>
    <p class="muted">Record and review your business income and expenses.</p>

    <section class="card">
        <h2>Add a transaction</h2>
        <form method="POST">
            <label>
                Description
                <input name="description" required maxlength="120"
                       placeholder="e.g. Product sales">
            </label>

            <label>
                Transaction type
                <select name="type" required>
                    <option value="Income">Income</option>
                    <option value="Expense">Expense</option>
                </select>
            </label>

            <label>
                Amount (₹)
                <input type="number" name="amount" min="0.01"
                       step="0.01" required placeholder="e.g. 500">
            </label>

            <label>
                Date
                <input type="date" name="date" value="{today}" required>
            </label>

            <button type="submit">Save transaction</button>
        </form>
    </section>

    <section class="card">
        <h2>All transactions</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Description</th>
                        <th>Type</th>
                        <th>Amount</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </section>
    """
    return page("Transactions", content)


@app.route("/transactions/<int:transaction_id>/delete", methods=["POST"])
def delete_transaction(transaction_id):
    transactions[:] = [
        t for t in transactions if t["id"] != transaction_id
    ]
    return redirect(url_for("transactions_page"))


# --------------------------------------------------
# Reports
# --------------------------------------------------

@app.route("/reports")
def reports():
    income, expenses, balance = totals()

    income_percent = (
        min(100, income / max(income + expenses, 1) * 100)
    )
    expense_percent = (
        min(100, expenses / max(income + expenses, 1) * 100)
    )

    content = f"""
    <h1>Business reports</h1>
    <p class="muted">A simple summary of your recorded finances.</p>

    <div class="grid">
        <section class="card">
            <div class="stat-label">Income</div>
            <div class="stat-value positive">{money(income)}</div>
        </section>
        <section class="card">
            <div class="stat-label">Expenses</div>
            <div class="stat-value negative">{money(expenses)}</div>
        </section>
        <section class="card">
            <div class="stat-label">Net balance</div>
            <div class="stat-value">{money(balance)}</div>
        </section>
    </div>

    <section class="card">
        <h2>Income vs. expenses</h2>

        <p>Income — {money(income)}</p>
        <div style="height:14px;background:#edf0eb;border-radius:10px;
                    overflow:hidden">
            <div style="height:100%;width:{income_percent:.2f}%;
                        background:#17663d"></div>
        </div>

        <p>Expenses — {money(expenses)}</p>
        <div style="height:14px;background:#edf0eb;border-radius:10px;
                    overflow:hidden">
            <div style="height:100%;width:{expense_percent:.2f}%;
                        background:#d89b28"></div>
        </div>

        <p class="muted">
            These totals include all transactions currently stored in
            this running demo.
        </p>
    </section>

    <section class="card">
        <h2>Business insight</h2>
        <p>
            {"Your recorded income is higher than your expenses."
             if balance > 0 else
             "Your recorded expenses are equal to or higher than income."
             if balance <= 0 else ""}
        </p>
        <p class="muted">
            This is a basic bookkeeping summary, not a tax or accounting report.
        </p>
    </section>
    """
    return page("Reports", content)


# --------------------------------------------------
# Business proposals
# --------------------------------------------------

@app.route("/proposals", methods=["GET", "POST"])
def proposals_page():
    if request.method == "POST":
        business_name = request.form.get("business_name", "").strip()
        service = request.form.get("service", "").strip()
        budget_text = request.form.get("budget", "0").strip()
        customer = request.form.get("customer", "").strip()

        try:
            budget = float(budget_text)
        except ValueError:
            budget = 0

        if business_name and service and budget > 0:
            proposal = {
                "id": next(proposal_ids),
                "business_name": business_name,
                "service": service,
                "budget": budget,
                "customer": customer,
                "date": datetime.now().strftime("%Y-%m-%d")
            }
            proposals.append(proposal)
            return redirect(
                url_for("view_proposal", proposal_id=proposal["id"])
            )

    rows = "".join(
        f"""
        <tr>
            <td>{p['business_name']}</td>
            <td>{p['service']}</td>
            <td>{money(p['budget'])}</td>
            <td>
                <a class="button secondary"
                   href="{url_for('view_proposal', proposal_id=p['id'])}">
                    View
                </a>
            </td>
        </tr>
        """
        for p in reversed(proposals)
    )

    if not rows:
        rows = '<tr><td colspan="4">No proposals created yet.</td></tr>'

    content = f"""
    <h1>Business proposals</h1>
    <p class="muted">
        Create a simple proposal for your customers.
    </p>

    <section class="card">
        <h2>Create a proposal</h2>
        <form method="POST">
            <label>
                Business name
                <input name="business_name" required maxlength="120"
                       placeholder="Your business name">
            </label>

            <label>
                Customer name (optional)
                <input name="customer" maxlength="120"
                       placeholder="Customer name">
            </label>

            <label>
                Product or service
                <textarea name="service" rows="3" required maxlength="1000"
                          placeholder="Describe your offer"></textarea>
            </label>

            <label>
                Proposed budget (₹)
                <input name="budget" type="number" min="0.01"
                       step="0.01" required placeholder="e.g. 5000">
            </label>

            <button type="submit">Create proposal</button>
        </form>
    </section>

    <section class="card">
        <h2>Saved proposals</h2>
        <div class="table-wrap">
            <table>
                <thead>
                    <tr>
                        <th>Business</th>
                        <th>Service</th>
                        <th>Budget</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
    </section>
    """
    return page("Proposals", content)


@app.route("/proposals/<int:proposal_id>")
def view_proposal(proposal_id):
    proposal = next(
        (p for p in proposals if p["id"] == proposal_id),
        None
    )

    if proposal is None:
        return "Proposal not found.", 404

    # Escape user-provided text before placing it in HTML.
    from markupsafe import escape

    business = escape(proposal["business_name"])
    customer = escape(proposal["customer"] or "Customer")
    service = escape(proposal["service"])

    content = f"""
    <h1>Business proposal</h1>

    <section class="card">
        <p class="muted">Date: {proposal['date']}</p>
        <h2>{business}</h2>
        <p><strong>Prepared for:</strong> {customer}</p>

        <h3>Proposed service</h3>
        <div class="message">{service}</div>

        <h3>Proposed budget</h3>
        <div class="stat-value positive">{money(proposal['budget'])}</div>

        <p class="muted">
            This proposal is a draft. Confirm the scope, terms and
            payment arrangements with the customer before accepting it.
        </p>

        <div class="actions">
            <button onclick="window.print()">Print / Save as PDF</button>
            <a class="button secondary"
               href="{url_for('proposals_page')}">Back to proposals</a>
        </div>
    </section>
    """
    return page("View Proposal", content)


# --------------------------------------------------
# Simple rule-based business assistant
# --------------------------------------------------

def assistant_answer(question):
    q = question.lower()
    income, expenses, balance = totals()

    if any(word in q for word in ["profit", "balance", "earning"]):
        return (
            f"Your recorded income is {money(income)}. "
            f"Your recorded expenses are {money(expenses)}. "
            f"Your net balance is {money(balance)}. "
            "This is based only on transactions stored in this demo."
        )

    if any(word in q for word in ["expense", "expenses", "cost"]):
        return (
            f"Your recorded expenses total {money(expenses)}. "
            "Review your transaction list and look for costs that can "
            "be reduced without affecting product quality or customers."
        )

    if any(word in q for word in ["sales", "sell", "customer"]):
        return (
            "To improve sales, understand what customers need, display "
            "clear prices, offer reliable service, and encourage repeat "
            "purchases. Track your sales to find your best-selling items."
        )

    if any(word in q for word in ["marketing", "promotion", "advertise"]):
        return (
            "Start with a simple marketing plan: identify your target "
            "customers, post useful product photos, share prices clearly, "
            "ask satisfied customers for referrals, and track which "
            "promotions generate sales."
        )

    if any(word in q for word in ["save", "saving", "budget"]):
        return (
            "Set a weekly budget, record every expense, separate business "
            "money from personal spending, and review recurring costs. "
            "Keep an emergency reserve when possible."
        )

    if any(word in q for word in ["proposal", "quotation"]):
        return (
            "Open the Proposals section to prepare a basic business "
            "proposal. Include the customer's name, scope of work, price, "
            "delivery timeline and payment terms."
        )

    return (
        "I can help with basic ideas for sales, marketing, expenses, "
        "budgeting and proposals. Ask a specific question, such as "
        "'How can I improve sales?' or 'What are my recorded expenses?' "
        "This version uses simple rules and is not connected to a live AI API."
    )


@app.route("/assistant", methods=["GET", "POST"])
def assistant():
    answer = None
    question = ""

    if request.method == "POST":
        question = request.form.get("question", "").strip()
        if question:
            answer = assistant_answer(question)

    answer_html = ""
    if answer is not None:
        from markupsafe import escape
        answer_html = (
            '<section class="card"><h2>Assistant response</h2>'
            f'<div class="message">{escape(answer)}</div></section>'
        )

    content = f"""
    <h1>BoliBiz AI Assistant</h1>
    <p class="muted">
        Get basic suggestions for managing your small business.
    </p>

    <section class="card">
        <h2>Ask a question</h2>
        <form method="POST">
            <label>
                Your question
                <textarea name="question" rows="4" required
                          maxlength="1000"
                          placeholder="How can I improve my sales?">{question}</textarea>
            </label>
            <button type="submit">Get suggestion</button>
        </form>
    </section>

    {answer_html}

    <section class="card">
        <h2>Example questions</h2>
        <ul>
            <li>What is my current balance?</li>
            <li>How can I reduce expenses?</li>
            <li>How can I improve sales?</li>
            <li>How can I promote my business?</li>
            <li>How do I prepare a proposal?</li>
        </ul>
    </section>
    """
    return page("AI Assistant", content)


# --------------------------------------------------
# Run the application
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
