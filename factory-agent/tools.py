"""
tools.py — the actions Claude is actually allowed to take.

An "AI agent" isn't magic — it's a normal chat model (Claude) plus a list of
plain Python functions it's allowed to call, like log_interaction() below.
Claude never touches your files directly. Instead:

  1. You ask it something in agent.py's chat loop.
  2. Claude reads the docstrings and type hints below and decides which
     function (if any) would help, and what to pass in.
  3. Claude asks to run that function — agent.py actually runs it.
  4. Whatever the function returns gets shown back to Claude.
  5. Claude uses that result to answer you in plain English.

That's the whole trick. Every function below is decorated with @beta_tool,
which is what tells the Anthropic SDK "this is a tool Claude can use" — it
reads the function's name, its argument names/types, and its docstring to
build the description Claude sees. That means THIS DOCSTRING is basically
part of Claude's instructions, not just a comment for you — write it
clearly, because Claude reads it too.
"""

from datetime import date

from anthropic import beta_tool

from storage import (
    load_activity_log,
    save_activity_log,
    load_tasks,
    save_tasks,
    load_stores,
    find_column,
    _next_id,
)


def _today():
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# Activity log: interactions + orders with customers (stores)
# ---------------------------------------------------------------------------

@beta_tool
def log_interaction(store_name: str, notes: str, contact_person: str = "", date_str: str = "") -> str:
    """Record a non-order interaction with a store: a phone call, an email,
    a visit, a sample drop-off, a complaint, anything worth remembering.

    Args:
        store_name: The store or business this interaction was with.
        notes: What happened / what was discussed. Be specific — this is
            what shows up later when someone asks "what's the history here?"
        contact_person: Who you talked to at the store, if you know. Leave
            blank if you don't know or it wasn't a specific person.
        date_str: Date in YYYY-MM-DD format. Leave blank to use today's date.
    """
    records = load_activity_log()
    entry = {
        "id": _next_id(records),
        "date": date_str or _today(),
        "store_name": store_name,
        "kind": "interaction",
        "notes": notes,
        "contact_person": contact_person or None,
        "amount": None,
    }
    records.append(entry)
    save_activity_log(records)
    return f"Logged interaction #{entry['id']} with {store_name} on {entry['date']}."


@beta_tool
def log_order(store_name: str, notes: str, amount: float = 0.0, date_str: str = "") -> str:
    """Record an order placed by/for a store.

    Args:
        store_name: The store or business that ordered.
        notes: What was ordered (e.g. "12 jars mild salsa, 6 jars hot").
        amount: Dollar amount of the order, if known. Use 0 if unknown.
        date_str: Date in YYYY-MM-DD format. Leave blank to use today's date.
    """
    records = load_activity_log()
    entry = {
        "id": _next_id(records),
        "date": date_str or _today(),
        "store_name": store_name,
        "kind": "order",
        "notes": notes,
        "contact_person": None,
        "amount": amount,
    }
    records.append(entry)
    save_activity_log(records)
    return f"Logged order #{entry['id']} from {store_name} on {entry['date']} (${amount:.2f})."


@beta_tool
def get_activity(store_name: str = "", kind: str = "", limit: int = 20) -> str:
    """Look up recent activity log entries (interactions and/or orders).

    Args:
        store_name: Only show entries for this store. Leave blank for all stores.
        kind: Filter to "interaction" or "order" only. Leave blank for both.
        limit: Maximum number of entries to return, most recent first.
    """
    records = load_activity_log()
    if store_name:
        records = [r for r in records if r["store_name"].lower() == store_name.lower()]
    if kind:
        records = [r for r in records if r["kind"] == kind]
    if not records:
        return "No matching activity found."

    # Newest first, since that's almost always what you want to see.
    records = sorted(records, key=lambda r: (r["date"], r["id"]), reverse=True)[:limit]

    lines = []
    for r in records:
        if r["kind"] == "order":
            lines.append(f"[{r['date']}] ORDER — {r['store_name']}: {r['notes']} (${r['amount']:.2f})")
        else:
            who = f" (with {r['contact_person']})" if r["contact_person"] else ""
            lines.append(f"[{r['date']}] INTERACTION — {r['store_name']}{who}: {r['notes']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tasks / reminders
# ---------------------------------------------------------------------------

@beta_tool
def add_task(description: str, due_date: str = "", related_store: str = "") -> str:
    """Add a to-do / reminder.

    Args:
        description: What needs to get done.
        due_date: Date it's due, YYYY-MM-DD. Leave blank if there's no deadline.
        related_store: The store this task is about, if any. Leave blank otherwise.
    """
    tasks = load_tasks()
    task = {
        "id": _next_id(tasks),
        "description": description,
        "due_date": due_date or None,
        "related_store": related_store or None,
        "done": False,
        "created_date": _today(),
    }
    tasks.append(task)
    save_tasks(tasks)
    return f"Added task #{task['id']}: {description}"


@beta_tool
def list_tasks(only_open: bool = True) -> str:
    """List tasks/reminders.

    Args:
        only_open: If true (default), hide tasks already marked done.
    """
    tasks = load_tasks()
    if only_open:
        tasks = [t for t in tasks if not t["done"]]
    if not tasks:
        return "No tasks to show."

    tasks = sorted(tasks, key=lambda t: (t["due_date"] or "9999-99-99"))
    lines = []
    for t in tasks:
        status = "done" if t["done"] else "open"
        due = f" due {t['due_date']}" if t["due_date"] else ""
        store = f" [{t['related_store']}]" if t["related_store"] else ""
        lines.append(f"#{t['id']} ({status}){due}{store}: {t['description']}")
    return "\n".join(lines)


@beta_tool
def complete_task(task_id: int) -> str:
    """Mark a task as done, by its ID number (from list_tasks).

    Args:
        task_id: The numeric ID of the task to mark complete.
    """
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            t["done"] = True
            save_tasks(tasks)
            return f"Marked task #{task_id} as done."
    return f"No task with ID {task_id} found. Use list_tasks to see valid IDs."


# ---------------------------------------------------------------------------
# Segmentation / reporting over the Master Store List
# ---------------------------------------------------------------------------

@beta_tool
def segment_stores(by_column: str = "", value: str = "") -> str:
    """Group or filter stores from the Master Store List (data/stores.csv).

    If neither by_column nor value is given, this tries to group all stores
    by their status column (e.g. Active retailer / Prospect / Inactive /
    Out of business) and report counts for each group.

    Args:
        by_column: Exact or approximate column name to group/filter by
            (e.g. "Status", "City"). Leave blank to auto-detect a status-like column.
        value: If given, only count/list rows where by_column equals this value.
    """
    stores = load_stores()
    if not stores:
        return (
            "No store data found. Export the Master Store List from Google Sheets "
            "(File -> Download -> Comma Separated Values) and save it as "
            "factory-agent/data/stores.csv, then ask again."
        )

    fieldnames = list(stores[0].keys())

    if by_column:
        column = find_column(fieldnames, by_column)
        if not column:
            return f"Couldn't find a column matching '{by_column}'. Columns available: {', '.join(fieldnames)}"
    else:
        column = find_column(fieldnames, "Status", "Store Status", "State")
        if not column:
            return f"Couldn't auto-detect a status column. Columns available: {', '.join(fieldnames)}"

    if value:
        matches = [s for s in stores if s.get(column, "").strip().lower() == value.strip().lower()]
        names = [s.get(find_column(fieldnames, "Store Name", "Name", "Shopify Name") or fieldnames[0], "?") for s in matches]
        return f"{len(matches)} store(s) where {column} = '{value}':\n" + "\n".join(names[:50])

    # No specific value requested — report counts per group.
    counts = {}
    for s in stores:
        key = s.get(column, "").strip() or "(blank)"
        counts[key] = counts.get(key, 0) + 1
    lines = [f"{k}: {v}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])]
    return f"Store counts by {column}:\n" + "\n".join(lines)


@beta_tool
def summary_report() -> str:
    """Produce a quick overall snapshot: store counts by status, recent
    activity counts, and open task counts. Good for "what's going on"
    type questions with no specific filter.
    """
    parts = []

    stores = load_stores()
    if stores:
        fieldnames = list(stores[0].keys())
        column = find_column(fieldnames, "Status", "Store Status", "State")
        if column:
            counts = {}
            for s in stores:
                key = s.get(column, "").strip() or "(blank)"
                counts[key] = counts.get(key, 0) + 1
            parts.append("Stores by status: " + ", ".join(f"{k}={v}" for k, v in counts.items()))
        else:
            parts.append(f"{len(stores)} stores loaded (no status column detected).")
    else:
        parts.append("No stores.csv loaded yet — see NOTES in segment_stores.")

    activity = load_activity_log()
    orders = [a for a in activity if a["kind"] == "order"]
    interactions = [a for a in activity if a["kind"] == "interaction"]
    parts.append(f"Activity log: {len(orders)} orders, {len(interactions)} interactions logged total.")

    tasks = load_tasks()
    open_tasks = [t for t in tasks if not t["done"]]
    parts.append(f"Tasks: {len(open_tasks)} open, {len(tasks) - len(open_tasks)} done.")

    return "\n".join(parts)


# The full list of tools handed to the agent's tool_runner in agent.py.
ALL_TOOLS = [
    log_interaction,
    log_order,
    get_activity,
    add_task,
    list_tasks,
    complete_task,
    segment_stores,
    summary_report,
]
