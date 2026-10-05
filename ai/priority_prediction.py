def predict_priority(category, description, location=""):
    """
    Predict complaint priority using:

    1. Complaint category
    2. Complaint description / severity
    3. Complaint location / area impact

    Final result:
        High
        Medium
        Low
    """

    # =========================================
    # CLEAN INPUTS
    # =========================================

    category = str(category or "").lower().strip()
    description = str(description or "").lower().strip()
    location = str(location or "").lower().strip()

    # =========================================
    # PRIORITY SCORE
    # =========================================

    score = 0

    # =========================================
    # 1. HIGH SEVERITY PROBLEMS
    # =========================================

    high_severity_keywords = [
        "accident",
        "danger",
        "dangerous",
        "fire",
        "flood",
        "electric shock",
        "electric shock risk",
        "broken electric wire",
        "fallen electric wire",
        "fallen wire",
        "live wire",
        "open manhole",
        "sewage overflow",
        "major leakage",
        "gas leak",
        "building collapse",
        "wall collapse",
        "road collapse",
        "life threatening",
        "emergency",
        "fatal",
        "injury",
        "injured",
        "death",
        "risk to life"
    ]

    # =========================================
    # 2. MEDIUM SEVERITY PROBLEMS
    # =========================================

    medium_severity_keywords = [
        "large pothole",
        "big pothole",
        "pothole",
        "water leakage",
        "water leak",
        "garbage overflow",
        "garbage accumulation",
        "street light failure",
        "streetlight failure",
        "street light not working",
        "streetlight not working",
        "road damage",
        "damaged road",
        "blocked drain",
        "drainage problem",
        "drainage issue",
        "sewage problem",
        "water supply problem",
        "water shortage",
        "broken road",
        "broken pipe",
        "overflow"
    ]

    # =========================================
    # 3. LOW SEVERITY PROBLEMS
    # =========================================

    low_severity_keywords = [
        "small pothole",
        "minor pothole",
        "minor leakage",
        "small leakage",
        "minor damage",
        "small damage",
        "small garbage",
        "light not working",
        "minor road damage",
        "small crack",
        "minor issue"
    ]

    # =========================================
    # CHECK SEVERITY
    # =========================================

    if any(
        keyword in description
        for keyword in high_severity_keywords
    ):
        score += 6

    elif any(
        keyword in description
        for keyword in medium_severity_keywords
    ):
        score += 3

    elif any(
        keyword in description
        for keyword in low_severity_keywords
    ):
        score += 1

    else:
        # If no specific severity keyword is found,
        # give a small base score.
        score += 1

    # =========================================
    # 4. CATEGORY IMPACT
    # =========================================

    high_impact_categories = [
        "fire",
        "electricity",
        "emergency",
        "public safety",
        "gas",
        "accident"
    ]

    medium_impact_categories = [
        "water supply",
        "drainage",
        "sewage",
        "road",
        "roads",
        "garbage",
        "sanitation",
        "street light",
        "streetlight"
    ]

    if category in high_impact_categories:
        score += 3

    elif category in medium_impact_categories:
        score += 2

    # =========================================
    # 5. HIGH IMPACT LOCATION
    # =========================================
    #
    # Problems in these areas affect more people
    # and therefore receive higher priority.
    #

    high_impact_locations = [
        "main road",
        "main street",
        "highway",
        "national highway",
        "state highway",
        "school",
        "school road",
        "college",
        "hospital",
        "hospital road",
        "bus stand",
        "bus stop",
        "railway station",
        "railway road",
        "market",
        "market road",
        "junction",
        "traffic signal",
        "public place",
        "government office",
        "government hospital",
        "temple",
        "mosque",
        "church"
    ]

    if any(
        keyword in location
        for keyword in high_impact_locations
    ):
        score += 4

    # =========================================
    # 6. MEDIUM IMPACT LOCATION
    # =========================================

    medium_impact_locations = [
        "residential area",
        "residential",
        "village",
        "street",
        "road",
        "colony",
        "apartment",
        "housing area",
        "town"
    ]

    elif_medium_location = any(
        keyword in location
        for keyword in medium_impact_locations
    )

    if elif_medium_location:
        score += 2

    # =========================================
    # 7. PUBLIC SAFETY COMBINATION
    # =========================================
    #
    # If a dangerous problem occurs in a
    # high-impact public location, increase
    # the priority further.
    #

    is_high_severity = any(
        keyword in description
        for keyword in high_severity_keywords
    )

    is_high_impact_location = any(
        keyword in location
        for keyword in high_impact_locations
    )

    if (
        is_high_severity
        and is_high_impact_location
    ):
        score += 3

    # =========================================
    # 8. FINAL PRIORITY
    # =========================================

    if score >= 8:
        priority = "High"

    elif score >= 4:
        priority = "Medium"

    else:
        priority = "Low"

    # =========================================
    # DEBUG INFORMATION
    # =========================================

    print(
        f"[Priority Prediction] "
        f"Category: {category} | "
        f"Location: {location} | "
        f"Score: {score} | "
        f"Priority: {priority}"
    )

    return priority