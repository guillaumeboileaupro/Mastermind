const VARIANT_RULES = {
    "mastermind-1972": {
        title: "Mastermind original · 1972",
        short: "Trouve un code de 4 couleurs parmi 6. Après chaque essai, le score indique combien de couleurs sont bien placées puis combien sont présentes mais mal placées.",
        steps: [
            "Compose une proposition de 4 couleurs. Une couleur peut être utilisée plusieurs fois dans cette adaptation.",
            "Lis le résultat à deux chiffres : le premier compte les couleurs bien placées, le second les bonnes couleurs placées ailleurs.",
            "Trouve les 4 positions en 10 essais maximum pour marquer des points."
        ]
    },
    "bagels-1972": {
        title: "Bagels · 1972",
        short: "Cherche un nombre secret de 3 chiffres parmi 0 à 9. Cette version numérique conserve le principe de déduction avec position correcte ou chiffre présent ailleurs.",
        steps: [
            "Propose 3 chiffres pour retrouver le nombre secret.",
            "L’édition Bagels est traditionnellement connue pour ses indices Fermi, Pico et Bagels. Dans cette adaptation, le retour est présenté avec le score Mastermind : bien placé puis mal placé.",
            "Utilise les indices successifs pour réduire les possibilités et trouver les 3 chiffres en 10 essais avec score."
        ]
    },
    "royale-mastermind-1972": {
        title: "Royale Mastermind · 1972",
        short: "Chaque pion combine une couleur et une forme. Il faut retrouver 3 combinaisons parmi 25 possibilités.",
        steps: [
            "Choisis 3 pions ; chaque pion associe une des 5 couleurs à une des 5 formes.",
            "Après validation, le premier chiffre indique les pions couleur-forme exactement placés et le second ceux présents à une autre position.",
            "Retrouve les 3 combinaisons secrètes en 10 essais maximum pour conserver un score."
        ]
    },
    "mastermind44-1972": {
        title: "Mastermind44 · 1972",
        short: "Une version étendue à 5 positions avec 6 couleurs. L’édition physique vise quatre joueurs ; ici tu joues seul contre l’ordinateur.",
        steps: [
            "Construis une proposition de 5 couleurs parmi les 6 disponibles.",
            "Le résultat compte d’abord les couleurs à la bonne position, puis les bonnes couleurs placées ailleurs.",
            "Le matériel original est multijoueur ; cette adaptation conserve le puzzle de décodage en solo avec 10 essais donnant des points."
        ]
    },
    "grand-mastermind-1974": {
        title: "Grand Mastermind · 1974",
        short: "Retrouve 4 pions définis chacun par une couleur et une forme, soit 25 types de pions possibles.",
        steps: [
            "Choisis 4 combinaisons couleur-forme parmi les 25 proposées.",
            "Un pion n’est exactement correct que si sa couleur, sa forme et sa position correspondent au secret.",
            "Le score à deux chiffres indique les pions bien placés puis les pions corrects placés ailleurs ; tu disposes de 10 essais avec score."
        ]
    },
    "super-mastermind-1972": {
        title: "Super Mastermind / Deluxe / Advanced",
        short: "Une version plus difficile : 8 couleurs à combiner sur 5 positions.",
        steps: [
            "Propose une combinaison de 5 pions parmi 8 couleurs.",
            "Le premier chiffre du résultat correspond aux couleurs bien placées ; le second aux couleurs présentes au mauvais endroit.",
            "Les 8 couleurs et les 5 positions augmentent fortement le nombre de codes possibles ; trouve le secret en 10 essais avec score."
        ]
    },
    "word-mastermind-1972": {
        title: "Word Mastermind · 1972",
        short: "Le principe du Mastermind est appliqué aux lettres : retrouve une séquence de 4 lettres.",
        steps: [
            "Propose 4 lettres parmi A à Z.",
            "Le résultat indique le nombre de lettres exactement placées puis le nombre de bonnes lettres situées ailleurs.",
            "L’édition physique demande des mots valides ; cette adaptation n’impose pas de dictionnaire et accepte toute combinaison de lettres."
        ]
    },
    "mini-mastermind-1976": {
        title: "Mini Mastermind · 1976",
        short: "Le Mastermind classique en format voyage, mais avec seulement 6 essais donnant des points.",
        steps: [
            "Retrouve un code de 4 positions à partir de 6 couleurs.",
            "Chaque résultat donne le nombre de couleurs bien placées puis présentes mais mal placées.",
            "La contrainte principale de cette édition est la limite de 6 essais : après celle-ci tu peux continuer, mais sans score."
        ]
    },
    "number-mastermind-1976": {
        title: "Number Mastermind · 1976",
        short: "Les couleurs sont remplacées par 6 chiffres. Le code secret comporte 4 positions.",
        steps: [
            "Propose 4 chiffres parmi 1 à 6.",
            "Le résultat indique combien de chiffres sont à la bonne place puis combien sont présents à une autre place.",
            "L’édition physique permet aussi au créateur de donner la somme des chiffres comme indice facultatif ; cet indice supplémentaire n’est pas utilisé ici."
        ]
    },
    "electronic-mastermind-1977": {
        title: "Electronic Mastermind (Invicta) · 1977",
        short: "Version électronique à 10 chiffres avec une longueur de code réglable sur 3, 4 ou 5 positions.",
        steps: [
            "Choisis d’abord une longueur de 3, 4 ou 5 positions dans les paramètres.",
            "Compose ensuite chaque tentative avec les chiffres de 0 à 9.",
            "Le retour reprend le principe Mastermind : positions exactes puis chiffres corrects ailleurs, avec 10 essais donnant des points."
        ]
    },
    "super-sonic-1979": {
        title: "Super-Sonic Electronic Mastermind · 1979",
        short: "Une édition électronique plus étendue : 10 chiffres et des codes de 3 à 6 positions.",
        steps: [
            "Sélectionne une longueur de code entre 3 et 6 positions.",
            "Propose des chiffres de 0 à 9 et utilise le score de position pour corriger la tentative suivante.",
            "L’app conserve le temps et le nombre d’essais, deux éléments caractéristiques de cette famille d’éditions électroniques."
        ]
    },
    "walt-disney-mastermind-1978": {
        title: "Walt Disney Mastermind · 1978",
        short: "Version enfant à 3 positions utilisant 5 personnages à la place des couleurs.",
        steps: [
            "Choisis 3 personnages parmi les 5 marqueurs disponibles.",
            "Le score indique combien de personnages sont correctement placés puis combien doivent changer de position.",
            "Le jeu physique utilise des personnages Disney ; l’application emploie des marqueurs neutres numérotés et ne reproduit pas les illustrations propriétaires."
        ]
    },
    "mini-mastermind-1988": {
        title: "Mini / Travel Mastermind · 1988",
        short: "Une autre édition de voyage du jeu classique : 6 couleurs, 4 positions et 6 essais avec score.",
        steps: [
            "Propose 4 couleurs parmi les 6 disponibles.",
            "Utilise les deux nombres du résultat pour distinguer les bonnes positions des bonnes couleurs mal placées.",
            "Cette édition privilégie les parties courtes : la limite de score est fixée à 6 essais."
        ]
    },
    "mastermind-challenge-1993": {
        title: "Mastermind Challenge · 1993",
        short: "Une variante avancée avec 8 couleurs et 5 positions, conçue à l’origine pour une confrontation simultanée entre deux joueurs.",
        steps: [
            "Cherche une combinaison de 5 pions parmi 8 couleurs.",
            "Chaque tentative reçoit le nombre de pions bien placés puis de bonnes couleurs placées ailleurs.",
            "Le jeu physique fait jouer simultanément les deux adversaires ; cette adaptation conserve le décodage en solo contre l’ordinateur."
        ]
    },
    "parker-mastermind-1993": {
        title: "Parker Mastermind · 1993",
        short: "Une édition Parker à 8 couleurs mais conservant un code de 4 positions.",
        steps: [
            "Compose 4 positions en choisissant parmi 8 couleurs.",
            "Le résultat distingue les couleurs exactement placées de celles qui appartiennent au code mais doivent être déplacées.",
            "Tu as 10 essais avec score pour retrouver la combinaison entière."
        ]
    },
    "mastermind-kids-1996": {
        title: "Mastermind for Kids · 1996",
        short: "Une version enfant : 6 animaux remplacent les couleurs et le code ne comporte que 3 positions.",
        steps: [
            "Choisis 3 animaux parmi les 6 proposés.",
            "Après chaque essai, utilise les indications de position pour savoir quels animaux conserver ou déplacer.",
            "Le mode « Facile enfant » peut en plus afficher un indice directement sous chaque animal."
        ]
    },
    "secret-search-1997": {
        title: "Mastermind Secret Search · 1997",
        short: "Retrouve des lettres grâce à des flèches qui disent, position par position, si la lettre secrète se trouve plus tôt ou plus tard dans l’alphabet.",
        steps: [
            "Choisis une longueur de 3 à 6 positions puis propose une lettre A–Z pour chaque emplacement.",
            "✓ signifie que la lettre est exacte ; ↑ indique qu’il faut chercher plus tard dans l’alphabet ; ↓ qu’il faut chercher plus tôt.",
            "L’édition originale travaille avec des mots ; cette adaptation n’impose pas de dictionnaire afin de conserver une partie jouable pour toutes les longueurs."
        ]
    },
    "electronic-handheld-1997": {
        title: "Electronic Hand-Held Mastermind (Hasbro) · 1997",
        short: "Adaptation du Mastermind électronique portable Hasbro : 6 couleurs et 4 positions.",
        steps: [
            "Propose une combinaison de 4 couleurs parmi 6.",
            "Le résultat indique les couleurs exactement placées puis les couleurs correctes à déplacer.",
            "L’interface numérique remplace le boîtier électronique d’origine tout en conservant la règle de décodage classique."
        ]
    },
    "new-mastermind-2004": {
        title: "New Mastermind · 2004",
        short: "Une édition modernisée à 8 couleurs et 4 positions, prévue physiquement pour plusieurs joueurs.",
        steps: [
            "Compose 4 positions parmi 8 couleurs.",
            "Lis le score pour connaître le nombre de couleurs exactes puis les couleurs correctes mais mal placées.",
            "L’édition physique accepte jusqu’à cinq joueurs ; l’application transforme cette règle en défi solo contre un code généré automatiquement."
        ]
    },
    "mini-mastermind-2004": {
        title: "Mini Mastermind · 2004",
        short: "Une version compacte autonome : 6 couleurs, 4 positions et 8 essais avec score.",
        steps: [
            "Propose 4 couleurs parmi les 6 disponibles.",
            "À chaque validation, compare les couleurs bien placées et les bonnes couleurs à déplacer.",
            "Cette édition donne 8 essais avec score, entre la limite courte des anciens Mini et les 10 essais du Mastermind classique."
        ]
    },
    "super-code": {
        title: "Super Code · VEB Plasticart",
        short: "Variante est-allemande citée avec Mastermind. Les paramètres détaillés n’étant pas précisés par la source, l’application utilise la règle classique.",
        steps: [
            "Cherche un code de 4 positions parmi 6 couleurs.",
            "Le résultat indique les couleurs bien placées puis les bonnes couleurs situées ailleurs.",
            "Cette configuration est une adaptation explicite : elle n’est pas présentée comme une reconstitution certaine des paramètres matériels de Super Code."
        ]
    }
};

function selectedVariantRules() {
    const select = document.querySelector("#mode");
    if (!select) return null;
    return VARIANT_RULES[select.value] || null;
}

function ensureVariantRulesCard() {
    let card = document.querySelector("#variant-rules-card");
    if (card) return card;
    const grid = document.querySelector(".help-grid");
    if (!grid) return null;

    card = document.createElement("article");
    card.id = "variant-rules-card";
    card.className = "variant-rules-card";
    card.innerHTML = `
        <strong id="variant-rules-title">Règle de la variante</strong>
        <p id="variant-rules-intro"></p>
        <ol id="variant-rules-list"></ol>
    `;
    grid.prepend(card);
    return card;
}

function renderVariantRules() {
    const rules = selectedVariantRules();
    if (!rules) return;

    const meta = document.querySelector("#variant-meta");
    if (meta) meta.textContent = rules.short;

    const card = ensureVariantRulesCard();
    if (!card) return;
    card.querySelector("#variant-rules-title").textContent = rules.title;
    card.querySelector("#variant-rules-intro").textContent = rules.short;
    const list = card.querySelector("#variant-rules-list");
    list.innerHTML = "";
    rules.steps.forEach((step) => {
        const item = document.createElement("li");
        item.textContent = step;
        list.appendChild(item);
    });
}

const variantSelect = document.querySelector("#mode");
const codeLengthSelect = document.querySelector("#code-length");
const helpButton = document.querySelector("#open-help");

variantSelect?.addEventListener("change", renderVariantRules);
codeLengthSelect?.addEventListener("change", renderVariantRules);
helpButton?.addEventListener("click", renderVariantRules);

if (variantSelect) {
    const observer = new MutationObserver(() => renderVariantRules());
    observer.observe(variantSelect, { childList: true });
}

renderVariantRules();
