def compute_atc_score(m):
    # m = measurements in cm

    rump_angle = m["height_cm"] * 0.1
    rump_width = m["rump_width_cm"] * 0.2
    body_depth = m["body_depth_cm"] * 0.5
    dairy_character = m["chest_girth_cm"] * 0.05
    feet_legs = m["height_cm"] * 0.08
    udder = m["rump_width_cm"] * 0.07

    score = (
        0.15*m["body_length_cm"] +
        0.15*m["height_cm"] +
        0.15*m["chest_girth_cm"] +
        0.10*rump_angle +
        0.10*rump_width +
        0.10*body_depth +
        0.10*dairy_character +
        0.075*feet_legs +
        0.075*udder
    )

    value = min(100, score/10)

    grade = (
        "Excellent" if value >= 85 else
        "Good Plus" if value >= 70 else
        "Good" if value >= 50 else
        "Average"
    )

    return value, grade