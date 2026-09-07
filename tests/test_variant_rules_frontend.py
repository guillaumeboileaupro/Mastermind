from pathlib import Path

from app.variants import VARIANTS


STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


def test_every_variant_has_a_frontend_rules_entry() -> None:
    """Chaque variante exposée par l'API possède une explication dédiée dans l'interface."""
    rules_script = (STATIC_DIR / "variant-rules.js").read_text(encoding="utf-8")

    for variant_id in VARIANTS:
        assert f'"{variant_id}"' in rules_script


def test_variant_rules_are_loaded_after_main_application() -> None:
    """Les règles sont chargées après le script principal pour enrichir l'interface existante."""
    page = (STATIC_DIR / "index.html").read_text(encoding="utf-8")

    main_position = page.index('/static/app.js')
    rules_position = page.index('/static/variant-rules.js')

    assert rules_position > main_position


def test_variant_help_contains_three_rule_steps() -> None:
    """Le composant d'aide prévoit un résumé et trois étapes de règle."""
    rules_script = (STATIC_DIR / "variant-rules.js").read_text(encoding="utf-8")

    assert 'card.id = "variant-rules-card"' in rules_script
    assert 'id="variant-rules-list"' in rules_script
    assert 'rules.steps.forEach' in rules_script
