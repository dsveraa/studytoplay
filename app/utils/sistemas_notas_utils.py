# sistemas.py

sistemas = {
    1: {
        "id": 1,
        "valores": ["A", "B", "C", "D", "E", "F"],
        "orden": ["F", "E", "D", "C", "B", "A"]
    },
    2: {
        "id": 2,
        "valores": ["A+", "A", "B", "C", "D", "E", "F"],
        "orden": ["F", "E", "D", "C", "B", "A", "A+"]
    },
    12: {
        "id": 12,
        "valores": [x for x in range(1,11)],
        "orden": None
    },
    9: {
        "id": 9,
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    13: {
        "id": 13,
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    14: {
        "id": 14,
        "valores": [x for x in range(0,6)],
        "orden": None
    },
    15: {
        "id": 15,
        "valores": [x for x in range(0,21)],
        "orden": None
    },
    16: {
        "id": 16,
        "valores": [x for x in range(1,13)],
        "orden": None
    },
    17: {
        "id": 17,
        "valores": [x for x in range(1,6)],
        "orden": None
    },
    18: {
        "id": 18,
        "valores": [x for x in range(0,11)],
        "orden": None
    },
    19: {
        "id": 19,
        "valores": [x for x in range(1,21)],
        "orden": None
    },
    3: {
        "id": 3,
        "valores": [x for x in range(0,101)],
        "orden": None
    },
    4: {
        "id": 4,
        "valores": [x for x in range(1,6)],
        "orden": None
    },
    5: {
        "id": 5,
        "valores": [x for x in range(1,10)],
        "orden": None
    },
    6: {
        "id": 6,
        "valores": [x for x in range(1,7)], # menor número es mejor calificación (considerar)
        "orden": None
    },    
    7: {
        "id": 7,
        "valores": [x for x in range(0,10)],
        "orden": None
    },
    8: {
        "id": 8,
        "valores": [x for x in range(0,21)],
        "orden": None
    },
    10: {
        "id": 10,
        "valores": [x for x in range(0,10)],
        "orden": None
    },
    11: {
        "id": 11,
        "valores": [round(x * 0.1, 1) for x in range(10, 71)],
        "orden": None
    }
}
