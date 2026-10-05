def classify_complaint(description):

    description = description.lower().strip()


    # =====================================================
    # ELECTRICITY
    # =====================================================

    electricity_keywords = [

        "streetlight",
        "street light",
        "street lamp",

        "electricity",
        "electric wire",
        "electrical wire",

        "power cut",
        "power outage",

        "electric pole",
        "electric pole damage",
        "electric pole broken",

        "light not working",
        "street light not working",
        "streetlight not working",

        "electric light",

        "electric issue",
        "electrical issue",
        "electric problem",
        "electrical problem"
    ]


    if any(
        keyword in description
        for keyword in electricity_keywords
    ):

        return "Electricity"


    # =====================================================
    # WATER SUPPLY
    # =====================================================

    water_keywords = [

        "water leakage",
        "water leak",
        "water leaking",
        "water leakage problem",

        "leakage",

        "leaking pipe",
        "broken water pipe",
        "broken pipe",

        "pipeline",
        "water pipeline",
        "water pipeline damage",

        "water supply",
        "no water",

        "water shortage",

        "pipe burst",
        "water pipe",

        "water problem",
        "water issue"
    ]


    if any(
        keyword in description
        for keyword in water_keywords
    ):

        return "Water Supply"


    # =====================================================
    # PUBLIC WORKS / ROAD
    # =====================================================

    public_works_keywords = [

        "pothole",
        "potholes",

        "road damage",
        "road damaged",
        "damaged road",

        "road surface",
        "damaged road surface",

        "broken road",
        "road is broken",

        "road issue",
        "road problem",

        "road damage problem",

        "road crack",
        "road cracks",
        "crack on road",
        "cracks on road",

        "uneven road",
        "uneven roads",

        "footpath",
        "damaged footpath",

        "pavement",
        "damaged pavement",

        "road infrastructure",

        "road condition",
        "bad road",

        "poor road condition"
    ]


    if any(
        keyword in description
        for keyword in public_works_keywords
    ):

        return "Public Works"


    # =====================================================
    # OTHER
    # =====================================================

    return "Other"