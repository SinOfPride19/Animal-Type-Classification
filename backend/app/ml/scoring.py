def compute_scores(m):
    # normalize into 0–100 scale roughly
    bl = min(m["body_length"] / 200 * 100, 100)
    ht = min(m["height"] / 150 * 100, 100)
    cg = min(m["chest_girth"] / 250 * 100, 100)

    # heuristic components
    rump_angle = 70
    rump_width = m["chest_width"] / 100 * 100
    body_depth = (m["chest_girth"] / m["height"]) * 50
    dairy = (cg + body_depth) / 2
    feet = 65
    udder = 75

    final = (
        0.15*bl + 0.15*ht + 0.15*cg +
        0.10*rump_angle + 0.10*rump_width +
        0.10*body_depth + 0.10*dairy +
        0.075*feet + 0.075*udder
    )

    if final >= 85:
        grade = "Excellent"
    elif final >= 70:
        grade = "Good"
    elif final >= 50:
        grade = "Average"
    else:
        grade = "Poor"

    return {
        "final_score": round(final),
        "grade": grade,
        "components": {
            "rump_angle": round(rump_angle/10),
            "rump_width": round(rump_width/10),
            "body_depth": round(body_depth/10),
            "dairy": round(dairy/10),
            "feet": round(feet/10),
            "udder": round(udder/10)
        }
    }