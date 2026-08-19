from .types import Choice, VariantDefinition


def _color_choices(values: list[tuple[str, str]]) -> list[Choice]:
    return [
        {"value": color, "label": label, "color": color}
        for label, color in values
    ]


CLASSIC_6 = _color_choices(
    [
        ("Rouge", "#ef4444"),
        ("Bleu", "#3b82f6"),
        ("Vert", "#22c55e"),
        ("Jaune", "#eab308"),
        ("Violet", "#8b5cf6"),
        ("Orange", "#f97316"),
    ]
)

COLORS_5 = CLASSIC_6[:5]
COLORS_8 = CLASSIC_6 + _color_choices(
    [
        ("Turquoise", "#0f766e"),
        ("Rose", "#db2777"),
    ]
)

DIGITS_6: list[Choice] = [
    {"value": str(value), "label": str(value)} for value in range(1, 7)
]
DIGITS_10: list[Choice] = [
    {"value": str(value), "label": str(value)} for value in range(10)
]
LETTERS: list[Choice] = [
    {"value": chr(code), "label": chr(code)} for code in range(ord("A"), ord("Z") + 1)
]

SHAPES = [
    ("Cercle", "●"),
    ("Triangle", "▲"),
    ("Carré", "■"),
    ("Losange", "◆"),
    ("Étoile", "★"),
]
COLOR_SHAPES: list[Choice] = []
for color_choice in COLORS_5:
    for shape_name, symbol in SHAPES:
        COLOR_SHAPES.append(
            {
                "value": f"{color_choice['label']}:{shape_name}",
                "label": f"{color_choice['label']} {shape_name}",
                "color": color_choice["color"],
                "symbol": symbol,
            }
        )

ANIMALS: list[Choice] = [
    {"value": "dog", "label": "Chien", "symbol": "🐶"},
    {"value": "cat", "label": "Chat", "symbol": "🐱"},
    {"value": "rabbit", "label": "Lapin", "symbol": "🐰"},
    {"value": "bear", "label": "Ours", "symbol": "🐻"},
    {"value": "fox", "label": "Renard", "symbol": "🦊"},
    {"value": "panda", "label": "Panda", "symbol": "🐼"},
]

DISNEY_PLACEHOLDERS: list[Choice] = [
    {"value": f"character-{value}", "label": f"Personnage Disney {value}", "symbol": str(value)}
    for value in range(1, 6)
]


VARIANTS: dict[str, VariantDefinition] = {
    "mastermind-1972": {
        "label": "Mastermind",
        "year": "1972",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "Version originale : 6 couleurs et 4 positions.",
        "note": "Adaptation du jeu original.",
    },
    "bagels-1972": {
        "label": "Bagels",
        "year": "1972",
        "choices": DIGITS_10,
        "code_lengths": [3],
        "default_code_length": 3,
        "max_attempts": 10,
        "description": "10 chiffres et un code de 3 positions.",
        "note": "La page source mentionne aussi une forme papier avec nombres de 2 ou 3 chiffres.",
    },
    "royale-mastermind-1972": {
        "label": "Royale Mastermind",
        "year": "1972",
        "choices": COLOR_SHAPES,
        "code_lengths": [3],
        "default_code_length": 3,
        "max_attempts": 10,
        "description": "25 combinaisons couleur × forme, code de 3 positions.",
        "note": "Chaque pion combine une des 5 couleurs avec une des 5 formes.",
    },
    "mastermind44-1972": {
        "label": "Mastermind44",
        "year": "1972",
        "choices": CLASSIC_6,
        "code_lengths": [5],
        "default_code_length": 5,
        "max_attempts": 10,
        "description": "6 couleurs et 5 positions.",
        "note": "L’édition physique est prévue pour quatre joueurs ; ici le jeu reste en solo contre l’ordinateur.",
    },
    "grand-mastermind-1974": {
        "label": "Grand Mastermind",
        "year": "1974",
        "choices": COLOR_SHAPES,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "25 combinaisons couleur × forme et 4 positions.",
        "note": "Chaque pion combine une couleur et une forme.",
    },
    "super-mastermind-1972": {
        "label": "Super Mastermind / Deluxe / Advanced",
        "year": "1972",
        "choices": COLORS_8,
        "code_lengths": [5],
        "default_code_length": 5,
        "max_attempts": 10,
        "description": "8 couleurs et 5 positions.",
        "note": "Version plus difficile du Mastermind classique.",
    },
    "word-mastermind-1972": {
        "label": "Word Mastermind",
        "year": "1972",
        "choices": LETTERS,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "26 lettres et 4 positions.",
        "note": "L’édition originale impose des mots valides. Cette adaptation utilise les lettres librement et n’impose pas de dictionnaire.",
    },
    "mini-mastermind-1976": {
        "label": "Mini Mastermind",
        "year": "1976",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 6,
        "description": "6 couleurs, 4 positions et seulement 6 essais.",
        "note": "Version de voyage.",
    },
    "number-mastermind-1976": {
        "label": "Number Mastermind",
        "year": "1976",
        "choices": DIGITS_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "6 chiffres et 4 positions.",
        "note": "L’édition permet au créateur du code de donner facultativement la somme des chiffres comme indice supplémentaire.",
    },
    "electronic-mastermind-1977": {
        "label": "Electronic Mastermind (Invicta)",
        "year": "1977",
        "choices": DIGITS_10,
        "code_lengths": [3, 4, 5],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "10 chiffres avec un code de 3, 4 ou 5 positions.",
        "note": "Adaptation du modèle électronique portable Invicta.",
    },
    "super-sonic-1979": {
        "label": "Super-Sonic Electronic Mastermind",
        "year": "1979",
        "choices": DIGITS_10,
        "code_lengths": [3, 4, 5, 6],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "10 chiffres avec un code de 3 à 6 positions.",
        "note": "L’édition physique ajoute notamment le code à 6 positions, un signal sonore et l’affichage du temps et des essais.",
    },
    "walt-disney-mastermind-1978": {
        "label": "Walt Disney Mastermind",
        "year": "1978",
        "choices": DISNEY_PLACEHOLDERS,
        "code_lengths": [3],
        "default_code_length": 3,
        "max_attempts": 10,
        "description": "5 personnages et 3 positions.",
        "note": "L’édition physique utilise des personnages Disney. L’application utilise des marqueurs textuels sans reproduire d’illustrations propriétaires.",
    },
    "mini-mastermind-1988": {
        "label": "Mini / Travel Mastermind",
        "year": "1988",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 6,
        "description": "6 couleurs, 4 positions et 6 essais.",
        "note": "Version de voyage.",
    },
    "mastermind-challenge-1993": {
        "label": "Mastermind Challenge",
        "year": "1993",
        "choices": COLORS_8,
        "code_lengths": [5],
        "default_code_length": 5,
        "max_attempts": 10,
        "description": "8 couleurs et 5 positions.",
        "note": "L’édition à deux joueurs fait jouer simultanément les rôles de créateur et de décodeur ; ici le mode reste en solo.",
    },
    "parker-mastermind-1993": {
        "label": "Parker Mastermind",
        "year": "1993",
        "choices": COLORS_8,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "8 couleurs et 4 positions.",
        "note": "Édition Parker Brothers.",
    },
    "mastermind-kids-1996": {
        "label": "Mastermind for Kids",
        "year": "1996",
        "choices": ANIMALS,
        "code_lengths": [3],
        "default_code_length": 3,
        "max_attempts": 10,
        "description": "6 animaux et 3 positions.",
        "note": "Adaptation numérique du thème animal de l’édition enfant.",
    },
    "secret-search-1997": {
        "label": "Mastermind Secret Search",
        "year": "1997",
        "choices": LETTERS,
        "code_lengths": [3, 4, 5, 6],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "26 lettres et un code de 3 à 6 positions.",
        "note": "Les indices indiquent position par position si la lettre secrète se trouve plus tôt ou plus tard dans l’alphabet. Le dictionnaire n’est pas imposé dans cette adaptation.",
        "feedback_kind": "alphabet",
    },
    "electronic-handheld-1997": {
        "label": "Electronic Hand-Held Mastermind (Hasbro)",
        "year": "1997",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "6 couleurs et 4 positions.",
        "note": "Adaptation du modèle électronique portable Hasbro.",
    },
    "new-mastermind-2004": {
        "label": "New Mastermind",
        "year": "2004",
        "choices": COLORS_8,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "8 couleurs et 4 positions.",
        "note": "L’édition physique accepte jusqu’à cinq joueurs ; ici le mode reste en solo.",
    },
    "mini-mastermind-2004": {
        "label": "Mini Mastermind",
        "year": "2004",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 8,
        "description": "6 couleurs, 4 positions et 8 essais.",
        "note": "Version de voyage autonome.",
    },
    "super-code": {
        "label": "Super Code (VEB Plasticart)",
        "year": "RDA",
        "choices": CLASSIC_6,
        "code_lengths": [4],
        "default_code_length": 4,
        "max_attempts": 10,
        "description": "Édition est-allemande citée comme variante de Mastermind.",
        "note": "La page source ne précise pas ses paramètres ; l’application utilise ici la configuration classique 6 couleurs × 4 positions.",
    },
}


def get_variant(mode: str) -> VariantDefinition | None:
    """Retourne une variante moderne ou la variante correspondant à un ancien mode."""
    aliases = {
        "colors": "mastermind-1972",
        "digits": "number-mastermind-1976",
    }
    return VARIANTS.get(aliases.get(mode, mode))


def max_attempts_for(mode: str) -> int:
    variant = get_variant(mode)
    return variant["max_attempts"] if variant else 10
