def route_complaint(department):

    if not department:
        return "Unassigned"

    department = department.strip().lower()

    if department == "public works":
        return "Public Works"

    if department == "water supply":
        return "Water Supply"

    if department == "electricity":
        return "Electricity"

    return "Unassigned"