records = []

def save_record(data):
    records.append(data)

def get_records():
    return records

def get_dashboard():
    total = len(records)
    cows = sum(1 for r in records if r["class"] == "cow")
    buffalos = sum(1 for r in records if r["class"] == "buffalo")

    return {
        "total": total,
        "cows": cows,
        "buffalos": buffalos
    }