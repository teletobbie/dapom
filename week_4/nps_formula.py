def calculate_nps(g, b, u):
    # computes the Net promoter score in a range from 0 to 10
    value = (g / (g + b + u) - b / (g + b + u)) * 5.0 + 5.0
    return round(value, 1)