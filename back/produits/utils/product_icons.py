"""
Utilitaire pour obtenir l'icône intelligente d'un produit
basé sur son nom et ses catégories
"""

# Mapping intelligent des mots-clés vers des emojis
# Organisé par catégorie pour une meilleure reconnaissance
PRODUCT_ICONS = {
    # Fruits
    '🍎': ['pomme', 'golden', 'gala', 'reinette'],
    '🍊': ['orange', 'mandarine', 'clémentine', 'clementine', 'agrume'],
    '🍋': ['citron', 'lime'],
    '🍌': ['banane', 'plantain'],
    '🍇': ['raisin', 'vigne'],
    '🍓': ['fraise', 'framboise'],
    '🍑': ['pêche', 'peche', 'abricot', 'nectarine'],
    '🍒': ['cerise'],
    '🍐': ['poire', 'williams'],
    '🥝': ['kiwi'],
    '🍉': ['pastèque', 'pasteque', 'melon'],
    '🥭': ['mangue'],
    '🍍': ['ananas'],

    # Légumes
    '🥕': ['carotte'],
    '🥔': ['pomme de terre', 'patate'],
    '🧅': ['oignon', 'échalote', 'echalote'],
    '🧄': ['ail'],
    '🥒': ['concombre', 'cornichon'],
    '🥬': ['salade', 'laitue', 'endive', 'mâche', 'mache', 'roquette'],
    '🥦': ['brocoli', 'chou-fleur', 'chou'],
    '🍅': ['tomate'],
    '🌶️': ['piment'],
    '🫑': ['poivron'],
    '🥑': ['avocat'],
    '🍆': ['aubergine'],
    '🌽': ['maïs', 'mais'],
    '🥗': ['mesclun', 'mix'],

    # Pain et boulangerie
    '🥖': ['baguette', 'ficelle'],
    '🥐': ['croissant', 'viennoiserie'],
    '🥯': ['bagel'],
    '🍞': ['pain', 'pain de mie', 'pain complet', 'pain de campagne', 'brioche'],
    '🧇': ['gaufre'],
    '🥞': ['crêpe', 'crepe', 'pancake'],

    # Pâtisserie
    '🍰': ['gâteau', 'gateau', 'tarte', 'pâtisserie', 'patisserie'],
    '🧁': ['cupcake', 'muffin'],
    '🍪': ['cookie', 'biscuit', 'sablé', 'sable'],
    '🎂': ['génoise', 'genoise'],

    # Produits laitiers
    '🥛': ['lait', 'yaourt', 'yogourt'],
    '🧀': ['fromage', 'comté', 'comte', 'camembert', 'brie', 'roquefort', 'chèvre', 'chevre', 'emmental', 'gruyère', 'gruyere'],
    '🧈': ['beurre', 'crème', 'creme'],

    # Viandes et poissons
    '🥩': ['viande', 'bœuf', 'boeuf', 'steak', 'côte', 'cote', 'haché', 'hache'],
    '🍗': ['poulet', 'volaille', 'canard', 'dinde', 'escalope'],
    '🥓': ['bacon', 'lard', 'jambon', 'saucisson', 'charcuterie', 'pâté', 'pate', 'rillettes'],
    '🍖': ['côtelette', 'cotelette', 'agneau', 'mouton'],
    '🐟': ['poisson', 'truite', 'saumon', 'arc-en-ciel'],
    '🦐': ['crevette', 'gambas', 'roses'],
    '🦞': ['homard', 'langouste'],
    '🦑': ['calamar', 'encornet', 'seiche'],
    '🦪': ['huître', 'huitre', 'coquillage'],

    # Œufs
    '🥚': ['œuf', 'oeuf'],

    # Pâtes et céréales
    '🍝': ['pâte', 'pate', 'spaghetti', 'tagliatelle', 'penne', 'fusilli', 'macaroni'],
    '🍚': ['riz', 'risotto'],
    '🥣': ['céréale', 'cereale', 'muesli', 'flocon'],

    # Sauces et condiments
    '🫙': ['conserve', 'boîte', 'boite'],
    '🫗': ['huile', 'vinaigre', 'vinaigrette'],
    '🍯': ['miel'],
    '🧂': ['sel', 'épice', 'epice', 'poivre'],

    # Conserves
    '🥫': ['haricot', 'sauce tomate', 'concentré', 'concentrate'],

    # Boissons
    '🧃': ['jus', 'nectar'],
    '☕': ['café', 'cafe', 'expresso', 'arabica'],
    '🍵': ['thé', 'the', 'tisane', 'infusion', 'verveine', 'vert', 'détox', 'detox'],
    '🥤': ['soda', 'limonade', 'sirop'],
    '💧': ['eau', 'minérale', 'minerale', 'gazeuse'],
    '🍷': ['vin', 'rouge', 'blanc', 'rosé', 'rose'],
    '🍺': ['bière', 'biere', 'artisanale'],
    '🥂': ['champagne', 'mousseux', 'brut'],
    '🍾': ['cidre'],

    # Snacks et sucreries
    '🍫': ['chocolat', 'cacao', 'tablette', 'noir', 'lait'],
    '🍬': ['bonbon', 'gélifiés', 'gelifie', 'caramel'],
    '🍭': ['lollipop', 'sucette'],
    '🍩': ['donut', 'beignet'],
    '🥜': ['cacahuète', 'cacahuete', 'arachide', 'noisette', 'amande', 'noix', 'cajou', 'grillées', 'grillees', 'salées', 'salees'],
    '🍿': ['pop-corn', 'maïs soufflé', 'mais souffle'],

    # Plats préparés
    '🍕': ['pizza', 'margherita'],
    '🌮': ['taco', 'burrito'],
    '🌯': ['wrap'],
    '🥙': ['kebab'],
    '🥪': ['sandwich'],
    '🌭': ['hot dog', 'saucisse'],
    '🍔': ['burger', 'hamburger'],
    '🍟': ['frite', 'frites'],
    '🍲': ['soupe', 'potage', 'bouillon', 'lasagnes', 'ratatouille'],

    # Desserts
    '🍨': ['glace', 'sorbet', 'crème glacée', 'creme glacee'],
    '🍧': ['granité', 'granite'],
    '🍮': ['flan', 'crème caramel', 'creme caramel'],

    # Fruits secs
    '🌰': ['châtaigne', 'chataigne', 'marron'],
    '🥥': ['noix de coco', 'coco'],

    # Herbes et aromates
    '🌿': ['herbe', 'persil', 'basilic', 'coriandre', 'menthe', 'thym', 'romarin'],

    # Surgelés
    '❄️': ['surgelé', 'surgele', 'petits pois', 'épinards', 'epinards'],

    # Bio et diététique
    '🌱': ['bio', 'quinoa', 'chia', 'graines', 'tofu', 'végétal', 'vegetal', 'vegan', 'végétarien', 'vegetarien'],
    '🌾': ['gluten', 'sarrasin', 'muesli'],
    '💊': ['spiruline', 'vitamine', 'complément', 'complement', 'protéinées', 'proteinees', 'comprimés', 'comprimes'],

    # Pâtisserie supplémentaire
    '🥮': ['madeleine', 'sablé', 'sable', 'breton'],

    # Chips et apéritifs
    '🥨': ['chips', 'apéritif', 'aperitif', 'barbecue', 'nature'],

    # Matériaux de construction
    '🌾': ['paille', 'bottes', 'construction', 'chanvre isolant'],
    '🧱': ['brique', 'terre crue', 'monomur', 'torchis'],
    '🪨': ['pierre', 'ardoise', 'naturelle', 'taille'],
    '🪵': ['bois', 'charpente', 'poutre', 'planche', 'madrier', 'chêne', 'pin', 'douglas'],
    '🏗️': ['tuile', 'terre cuite', 'enduit', 'chaux', 'plâtre', 'platre', 'mortier'],

    # Isolation
    '🧊': ['laine de bois', 'ouate', 'cellulose', 'liège', 'liege', 'expansé', 'expanse', 'isolant'],

    # Énergie et écologie
    '☀️': ['panneau solaire', 'solaire', 'photovoltaïque', 'photovoltaique', 'monocristallin', 'kit solaire'],
    '💨': ['éolienne', 'eolienne', 'éolien', 'eolien', 'micro-éolienne', 'micro-eolienne'],
    '🔋': ['batterie', 'lithium', 'gel', 'stockage', 'convertisseur', 'régulateur', 'regulateur'],
    '🔥': ['poêle', 'poele', 'granulés', 'granules', 'chaudière', 'chaudiere', 'biomasse', 'insert', 'récupérateur', 'recuperateur'],
    '⚡': ['onduleur', 'charge', 'solaire'],
    '💧': ['chauffe-eau', 'pompe à chaleur', 'pompe a chaleur', 'ballon', 'thermodynamique'],
}


def get_smart_product_icon(nom: str, description: str = "") -> str:
    """
    Fonction principale pour obtenir l'icône intelligente d'un produit

    Args:
        nom: Le nom du produit
        description: La description du produit (optionnel)

    Returns:
        L'emoji correspondant au produit
    """
    # Normaliser le nom et la description pour la recherche
    normalized_name = nom.lower() if nom else ""
    normalized_desc = description.lower() if description else ""
    search_text = f"{normalized_name} {normalized_desc}"

    # Chercher une correspondance dans le mapping
    for emoji, keywords in PRODUCT_ICONS.items():
        for keyword in keywords:
            if keyword in search_text:
                return emoji

    # Icône par défaut si aucune correspondance
    return '📦'
