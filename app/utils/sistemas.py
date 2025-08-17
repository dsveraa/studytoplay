# sistemas.py

sistemas = {
    "CL": {
        "valores": [round(x * 0.1, 1) for x in range(10, 71)],
        "orden": None
    },
    "USA": {
        "valores": ["A", "B", "C", "D", "E", "F"],
        "orden": ["F", "E", "D", "C", "B", "A"]
    },
    "AR": {
        "valores": [x for x in range(1,11)],
        "orden": None
    },
    "BR": {
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    "MX": {
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    "CO": {
        "valores": [x for x in range(0,6)],
        "orden": None
    },
    "PE": {
        "valores": [x for x in range(0,21)],
        "orden": None
    },
    "UY": {
        "valores": [x for x in range(1,13)],
        "orden": None
    },
    "PY": {
        "valores": [x for x in range(1,6)],
        "orden": None
    },
    "EC": {
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    "VZ": {
        "valores": [x for x in range(1,21)],
        "orden": None
    },
    "CH": {
        "valores": [x for x in range(0,101)],
        "orden": None
    },
    "JP1": {
        "valores": [x for x in range(0,101)],
        "orden": None
    },
    "JP2": {
        "valores": [x for x in range(1,6)],
        "orden": None
    },
    "UK": {
        "valores": [x for x in range(1,10)],
        "orden": None
    },
    "GER": {
        "valores": [x for x in range(1,7)], # menor número es mejor calificación (considerar)
        "orden": None
    },
    "CA": {
        "valores": ["A+", "A", "B", "C", "D", "E", "F"],
        "orden": ["F", "E", "D", "C", "B", "A", "A+"]
    },
    "COR": {
        "valores": [x for x in range(0,10)],
        "orden": None
    },
    "FR": {
        "valores": [x for x in range(0,21)],
        "orden": None
    },
    "ES": {
        "valores": [x for x in range(0,10)],
        "orden": None
    }
}
