import os, random
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "game.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -------------------------------
# Configuration for Base Stats & Abilities
# -------------------------------
RACE_STATS = {
    "Human":    {"base_health": 100, "mana": 100, "strength": 10, "intelligence": 10, "wisdom": 10, "constitution": 10, "speed": 100, "ability": "Inspiring Strike"},
    "Dwarf":    {"base_health": 100, "mana": 100, "strength": 12, "intelligence": 8,  "wisdom": 10, "constitution": 14, "speed": 50,  "ability": "Stout Resolve"},
    "Elf":      {"base_health": 50,  "mana": 120, "strength": 8,  "intelligence": 14, "wisdom": 12, "constitution": 6,  "speed": 100, "ability": "Swift Arrow"},
    "Demon":    {"base_health": 666, "mana": 150, "strength": 15, "intelligence": 12, "wisdom": 8,  "constitution": 12, "speed": 666, "ability": "Infernal Rage"},
    "Angel":    {"base_health": 333, "mana": 200, "strength": 10, "intelligence": 12, "wisdom": 16, "constitution": 12, "speed": 333, "ability": "Heavenly Grace"},
    "Demigod":  {"base_health": 500, "mana": 120, "strength": 14, "intelligence": 10, "wisdom": 10, "constitution": 15, "speed": 500, "ability": "Divine Charge"},
    "Messiah":  {"base_health": 100, "mana": 300, "strength": 10, "intelligence": 20, "wisdom": 20, "constitution": 10, "speed": 100, "ability": "Miraculous Touch"},
    "Dragon":   {"base_health": 500, "mana": 100, "strength": 18, "intelligence": 12, "wisdom": 12, "constitution": 20, "speed": 500, "ability": "Searing Flames"},
    "Beastman": {"base_health": 200, "mana": 80,  "strength": 16, "intelligence": 8,  "wisdom": 8,  "constitution": 13, "speed": 500, "ability": "Savage Bite"},
    "Kaosborne": {"base_health": 1000, "mana": 100, "strength": 10, "intelligence": 10, "wisdom": 10, "constitution": 10, "speed": 100, "ability": "Wild Anarchy"}
}

# -------------------------------
# Variance Configuration (min and max bonus for each stat per race)
# -------------------------------
STAT_VARIANCE = {
    "Human":    {"strength": (0, 2),  "intelligence": (0, 1), "wisdom": (0, 1), "constitution": (0, 2), "speed": (0, 0), "mana": (0, 0)},
    "Dwarf":    {"strength": (1, 3),  "intelligence": (-1, 1), "wisdom": (0, 2), "constitution": (2, 4), "speed": (-5, 0), "mana": (0, 0)},
    "Elf":      {"strength": (-1, 1), "intelligence": (1, 3),  "wisdom": (0, 2), "constitution": (-2, 0), "speed": (0, 5), "mana": (0, 0)},
    "Demon":    {"strength": (0, 5),  "intelligence": (0, 3),  "wisdom": (-1, 2), "constitution": (0, 3), "speed": (0, 10), "mana": (0, 0)},
    "Angel":    {"strength": (0, 3),  "intelligence": (1, 4),  "wisdom": (2, 4),  "constitution": (0, 2), "speed": (0, 5), "mana": (0, 0)},
    "Demigod":  {"strength": (1, 4),  "intelligence": (0, 3),  "wisdom": (0, 3),  "constitution": (1, 4), "speed": (0, 5), "mana": (0, 0)},
    "Messiah":  {"strength": (-1, 2), "intelligence": (2, 5),  "wisdom": (2, 5),  "constitution": (-1, 2), "speed": (0, 0), "mana": (0, 0)},
    "Dragon":   {"strength": (2, 5),  "intelligence": (0, 3),  "wisdom": (0, 3),  "constitution": (2, 5), "speed": (0, 5), "mana": (0, 0)},
    "Beastman": {"strength": (1, 4),  "intelligence": (-2, 1), "wisdom": (-2, 1), "constitution": (1, 3), "speed": (0, 10), "mana": (0, 0)},
    "Kaosborne": {"strength": (-9, 40), "intelligence": (-9, 40), "wisdom": (-9, 40), "constitution": (-9, 40), "speed": (-99, 1000), "mana": (-99, 10000)},
}

# -------------------------------
# Ability Descriptions
# -------------------------------
ABILITY_DESCRIPTIONS = {
    "Inspiring Strike": "A powerful blow that rallies allies and bolsters morale while damaging the enemy.",
    "Stout Resolve": "A defensive maneuver that steadies the fighter, reducing incoming damage and healing minor wounds.",
    "Swift Arrow": "A rapid, precise attack that strikes the enemy quickly before they can react.",
    "Infernal Rage": "Unleashes demonic fury to deal heavy damage at the cost of some mana.",
    "Heavenly Grace": "Calls upon divine favor to gently heal and protect the user during battle.",
    "Divine Charge": "A forceful, sacrificial charge that delivers extra damage to the foe.",
    "Miraculous Touch": "A unique attack that simultaneously harms the enemy and restores the user’s health.",
    "Searing Flames": "Engulfs the target in intense fire, causing burning damage over time.",
    "Savage Bite": "A ferocious, animalistic attack that rips into the enemy with raw power.",
    "Wild Anarchy": "A chaotic assault with unpredictable effects—it may damage foes or even heal the user.",
    # Evolved Form Abilities (or the evolved versions’ names)
    "Heroic Rally": "Inspires allies and boosts overall strength, making every strike count.",
    "Guardian's Shield": "Conjures a protective barrier that absorbs a portion of incoming damage.",
    "Stalwart Fortress": "Reinforces defenses to regenerate health quickly during combat.",
    "Mountain's Might": "Unleashes earth-shattering power, overwhelming foes with brute force.",
    "Elven Grace": "An elegant, swift attack that often doubles its damage on a successful hit.",
    "Mystic Arrow": "Fires an enchanted projectile that homes in on and pierces the enemy.",
    "Hellfire Blast": "Releases a concentrated burst of infernal fire that incinerates adversaries.",
    "Demonic Frenzy": "Channels unbridled fury to increase attack speed and strike multiple times.",
    "Divine Intervention": "Summons celestial aid to dramatically heal and protect in critical moments.",
    "Celestial Light": "Bathes the battlefield in radiant light, stunning or weakening enemies temporarily.",
    "Celestial Smite": "Delivers a devastating blow infused with heavenly power, punishing the enemy severely.",
    "Olympian Might": "Calls upon the power of the gods to unleash a colossal, crushing strike.",
    "Miraculous Salvation": "A wondrous ability that can heal and even revive the user in desperate times.",
    "Blessed Strike": "An attack imbued with holy energy that deals additional divine damage.",
    "Dragon's Fury": "Unleashes the wrath of ancient dragons to scorch and devastate opponents.",
    "Ancient Roar": "Emits a fearsome roar that terrifies and damages all nearby foes.",
    "Feral Roar": "A primal, bone-chilling roar that boosts the user's attack while intimidating the enemy.",
    "Savage Charge": "A full-force, unstoppable charge that overwhelms the target with raw aggression.",
    "Chaotic Surge": "An unpredictable burst of energy that randomly inflicts damage or healing effects.",
    "Anarchic Onslaught": "Launches a frenzied barrage of wild attacks that leave enemies reeling from the chaos."
}

# -------------------------------
# Evolved Race Stats & Abilities (including a secondary ability)
# -------------------------------
EVOLUTION_MAP = {
    "Human": {
         "race": "Champion Human",
         "base_health": lambda base: base + 50,
         "mana": lambda mana: mana + 20,
         "strength": lambda s: s + 5,
         "intelligence": lambda i: i + 3,
         "wisdom": lambda w: w + 3,
         "constitution": lambda c: c + 5,
         "speed": lambda spd: spd + 10,
         "ability": "Heroic Rally",
         "secondary_ability": "Guardian's Shield"
    },
    "Dwarf": {
         "race": "Dwarven Lord",
         "base_health": lambda base: base + 60,
         "mana": lambda mana: mana + 10,
         "strength": lambda s: s + 5,
         "intelligence": lambda i: i + 2,
         "wisdom": lambda w: w + 4,
         "constitution": lambda c: c + 6,
         "speed": lambda spd: spd,  # remains slow
         "ability": "Stalwart Fortress",
         "secondary_ability": "Mountain's Might"
    },
    "Elf": {
         "race": "High Elf",
         "base_health": lambda base: base + 40,
         "mana": lambda mana: mana + 30,
         "strength": lambda s: s + 3,
         "intelligence": lambda i: i + 6,
         "wisdom": lambda w: w + 5,
         "constitution": lambda c: c + 2,
         "speed": lambda spd: spd + 20,
         "ability": "Elven Grace",
         "secondary_ability": "Mystic Arrow"
    },
    "Demon": {
         "race": "Archdemon",
         "base_health": lambda base: base,  # HP remains unchanged
         "mana": lambda mana: mana + 50,
         "strength": lambda s: s + 10,
         "intelligence": lambda i: i + 5,
         "wisdom": lambda w: w + 5,
         "constitution": lambda c: c + 5,
         "speed": lambda spd: spd + 20,
         "ability": "Hellfire Blast",
         "secondary_ability": "Demonic Frenzy"
    },
    "Angel": {
         "race": "Archangel",
         "base_health": lambda base: base,  # HP remains unchanged
         "mana": lambda mana: mana + 60,
         "strength": lambda s: s + 8,
         "intelligence": lambda i: i + 8,
         "wisdom": lambda w: w + 12,
         "constitution": lambda c: c + 4,
         "speed": lambda spd: spd + 15,
         "ability": "Divine Intervention",
         "secondary_ability": "Celestial Light"
    },
    "Demigod": {
         "race": "Ascended Demigod",
         "base_health": lambda base: base + 70,
         "mana": lambda mana: mana + 40,
         "strength": lambda s: s + 7,
         "intelligence": lambda i: i + 7,
         "wisdom": lambda w: w + 7,
         "constitution": lambda c: c + 7,
         "speed": lambda spd: spd + 15,
         "ability": "Celestial Smite",
         "secondary_ability": "Olympian Might"
    },
    "Messiah": {
         "race": "Divine Messiah",
         "base_health": lambda base: base + 50,
         "mana": lambda mana: mana + 80,
         "strength": lambda s: s + 5,
         "intelligence": lambda i: i + 15,
         "wisdom": lambda w: w + 15,
         "constitution": lambda c: c + 5,
         "speed": lambda spd: spd + 10,
         "ability": "Miraculous Salvation",
         "secondary_ability": "Blessed Strike"
    },
    "Dragon": {
         "race": "Ancient Dragon",
         "base_health": lambda base: base + 100,
         "mana": lambda mana: mana + 20,
         "strength": lambda s: s + 12,
         "intelligence": lambda i: i + 6,
         "wisdom": lambda w: w + 6,
         "constitution": lambda c: c + 12,
         "speed": lambda spd: spd + 20,
         "ability": "Dragon's Fury",
         "secondary_ability": "Ancient Roar"
    },
    "Beastman": {
         "race": "Alpha Beastman",
         "base_health": lambda base: base + 80,
         "mana": lambda mana: mana + 10,
         "strength": lambda s: s + 10,
         "intelligence": lambda i: i + 4,
         "wisdom": lambda w: w + 4,
         "constitution": lambda c: c + 8,
         "speed": lambda spd: spd + 30,
         "ability": "Feral Roar",
         "secondary_ability": "Savage Charge"
    },
    "Kaosborne": {
         "race": "Anarchic Kaosborne",
         "base_health": lambda base: base + random(0,1)*100,
         "mana": lambda mana: mana + random(0,1)*100,
         "strength": lambda s: s + random(0,1)*100,
         "intelligence": lambda i: i + random(0,1)*100,
         "wisdom": lambda w: w + random(0,1)*100,
         "constitution": lambda c: c + random(0,1)*100,
         "speed": lambda spd: spd + random(0,1)*100,
         "ability": "Chaotic Surge",
         "secondary_ability": "Anarchic Onslaught"
    }
}

# -------------------------------
# Function to Calculate Kaosborne Stats
# -------------------------------
def calculate_kaosborne_stat():
    mult = random.randint(1, 101)
    div = random.randint(1, 3)
    if div == 1:
        value = 100 * mult
    elif div == 2 and mult == 0:
        value = 99999999999999
    else:
        value = 100 // max(mult, 1)
    return value

# -------------------------------
# Function for Type Advantages (Multiplier based on matchup)
# -------------------------------
def type_multiplier(attacker, defender):
    multiplier = 1.0
    # Use the first word of the race name (if evolved, this should reflect its base type)
    attacker_base = attacker.race.split()[0]
    defender_base = defender.race.split()[0]
    if attacker_base == "Demon" and defender_base == "Angel":
        multiplier = 1.5
    elif attacker_base == "Angel" and defender_base == "Demon":
        multiplier = 1.5
    elif attacker_base == "Dwarf" and defender_base == "Dragon":
        multiplier = 1.3
    elif attacker_base == "Elf" and defender_base == "Beastman":
        multiplier = 1.3
    elif attacker_base == "Demigod" and defender_base == "Human":
        multiplier = 1.2
    # You can add more rules here
    return multiplier

# -------------------------------
# Character Model
# -------------------------------
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    race = db.Column(db.String(50))
    level = db.Column(db.Integer, default=1)
    exp = db.Column(db.Integer, default=0)
    base_health = db.Column(db.Integer)
    current_health = db.Column(db.Integer)
    mana = db.Column(db.Integer)
    strength = db.Column(db.Integer)
    intelligence = db.Column(db.Integer)
    wisdom = db.Column(db.Integer)
    constitution = db.Column(db.Integer)
    speed = db.Column(db.Integer)
    potions = db.Column(db.Integer, default=3)
    gold = db.Column(db.Integer, default=100)
    evolved = db.Column(db.Boolean, default=False)
    ability = db.Column(db.String(200), default="")  # Will store one or two abilities

    def __init__(self):
        self.race = self.choose_race()
        self.level = 1
        self.exp = 0
        stats = RACE_STATS[self.race]
        # For Kaosborne, use special calculations
        if self.race == "Kaosborne":
            self.base_health = calculate_kaosborne_stat()
            self.speed = calculate_kaosborne_stat()
        else:
            self.base_health = stats["base_health"]
            self.speed = stats["speed"]
        self.current_health = self.base_health
        self.mana = stats["mana"]
        self.strength = stats["strength"]
        self.intelligence = stats["intelligence"]
        self.wisdom = stats["wisdom"]
        self.constitution = stats["constitution"]
        self.potions = 3
        self.gold = 100
        self.evolved = False
        self.ability = stats["ability"]

        # Apply stat variance unique to each race
        if self.race in STAT_VARIANCE:
            var = STAT_VARIANCE[self.race]
            self.strength += random.randint(*var["strength"])
            self.intelligence += random.randint(*var["intelligence"])
            self.wisdom += random.randint(*var["wisdom"])
            self.constitution += random.randint(*var["constitution"])
            self.speed += random.randint(*var["speed"])
            self.mana += random.randint(*var["mana"])

    def choose_race(self):
        roll = random.randint(1, 10)
        races = list(RACE_STATS.keys())
        return races[roll - 1]

    def gain_exp(self, amount):
        self.exp += amount
        leveled_up = False
        while self.exp >= self.level * 100:
            self.exp -= self.level * 100
            self.level += 1
            # Increase stats on level up (non-evolved)
            self.strength += 2
            self.intelligence += 2
            self.wisdom += 2
            self.constitution += 2
            self.base_health += 20
            self.current_health = self.base_health  # Heal fully on level up
            leveled_up = True
            flash(f"You leveled up! You are now level {self.level}.", "success")
        # Evolve automatically at level 10 (if not already evolved)
        if self.level >= 10 and not self.evolved:
            self.evolve()
        if leveled_up:
            db.session.commit()

    def evolve(self):
        if self.race in EVOLUTION_MAP:
            evolution = EVOLUTION_MAP[self.race]
            old_race = self.race
            self.race = evolution["race"]
            self.base_health = evolution["base_health"](self.base_health)
            # For demons and angels, HP remains unchanged per specification
            if old_race in ["Demon", "Angel"]:
                self.base_health = RACE_STATS[old_race]["base_health"]
            self.mana = evolution["mana"](self.mana)
            self.strength = evolution["strength"](self.strength)
            self.intelligence = evolution["intelligence"](self.intelligence)
            self.wisdom = evolution["wisdom"](self.wisdom)
            self.constitution = evolution["constitution"](self.constitution)
            self.speed = evolution["speed"](self.speed)
            # Set two abilities for evolved forms
            primary = evolution["ability"]
            secondary = evolution.get("secondary_ability", "")
            self.ability = f"{primary} | {secondary}" if secondary else primary
            self.evolved = True
            flash(f"Evolution complete! You have evolved into a {self.race}!", "info")

# -------------------------------
# Database Table Creation
# -------------------------------
# @app.before_first_request
# def create_tables():
#     db.create_all()

# -------------------------------
# Enemy Generation (using defined races and applying level scaling)
# -------------------------------
def generate_enemy(player_level):
    enemy_race = random.choice(list(RACE_STATS.keys()))
    base_stats = RACE_STATS[enemy_race].copy()
    if enemy_race == "Kaosborne":
        base_health = calculate_kaosborne_stat()
        speed = calculate_kaosborne_stat()
    else:
        base_health = base_stats["base_health"]
        speed = base_stats["speed"]
    enemy_level = random.randint(max(1, player_level - 1), player_level + 1)
    enemy = {
        "race": enemy_race,
        "level": enemy_level,
        "base_health": base_health + (enemy_level - 1) * 20,
        "current_health": base_health + (enemy_level - 1) * 20,
        "mana": base_stats["mana"],
        "strength": base_stats["strength"] + (enemy_level - 1) * 2,
        "intelligence": base_stats["intelligence"] + (enemy_level - 1) * 2,
        "wisdom": base_stats["wisdom"] + (enemy_level - 1) * 2,
        "constitution": base_stats["constitution"] + (enemy_level - 1) * 2,
        "speed": speed,
        "ability": base_stats["ability"]
    }
    enemy["attack_min"] = enemy["strength"]
    enemy["attack_max"] = enemy["strength"] + 10
    return enemy

# -------------------------------
# Damage Calculation (includes reduction from constitution)
# -------------------------------
def calculate_damage(damage, defense_constitution):
    reduction = defense_constitution // 2
    effective_damage = max(1, damage - reduction)
    return effective_damage

# -------------------------------
# Ability Effects (for PvE and PvP)
# -------------------------------
def use_ability(attacker, defender):
    log = ""
    damage = 0
    # Effects vary based on the ability text (we check for key words)
    ability_text = attacker.ability.split(" | ")[0]  # Use primary ability for effect
    if ability_text in ["Inspiring Strike", "Heroic Rally", "Champion Human"]:
        bonus = random.randint(10, 20)
        damage = attacker.strength + bonus
        heal = bonus // 2
        attacker.current_health = min(attacker.base_health, attacker.current_health + heal)
        log = f"{attacker.race} used {ability_text}, dealing {damage} damage and healing for {heal} HP!"
    elif ability_text in ["Stout Resolve", "Dwarven Lord", "Stalwart Fortress"]:
        heal = random.randint(5, 15)
        attacker.current_health = min(attacker.base_health, attacker.current_health + heal)
        log = f"{attacker.race} used {ability_text} and fortified their defenses, healing for {heal} HP!"
    elif ability_text in ["Swift Arrow", "High Elf", "Elven Grace"]:
        damage = (attacker.strength + random.randint(5, 15)) * 2
        log = f"{attacker.race} unleashed {ability_text}, striking for {damage} damage!"
    elif ability_text in ["Infernal Rage", "Archdemon", "Hellfire Blast"]:
        if attacker.mana >= 20:
            attacker.mana -= 20
            damage = attacker.strength + 30
            log = f"{attacker.race} invoked {ability_text}, dealing {damage} searing damage!"
        else:
            log = f"{attacker.race} tried to use {ability_text} but lacked enough mana!"
    elif ability_text in ["Heavenly Grace", "Archangel", "Divine Intervention"]:
        heal = random.randint(20, 30)
        attacker.current_health = min(attacker.base_health, attacker.current_health + heal)
        damage = 0
        log = f"{attacker.race} used {ability_text} to heal for {heal} HP!"
    elif ability_text in ["Divine Charge", "Demigod", "Celestial Smite"]:
        damage = attacker.strength + random.randint(15, 25)
        log = f"{attacker.race} used {ability_text}, charging for {damage} damage!"
    elif ability_text in ["Miraculous Touch", "Messiah", "Miraculous Salvation"]:
        damage = attacker.strength + 10
        heal = random.randint(10, 20)
        attacker.current_health = min(attacker.base_health, attacker.current_health + heal)
        log = f"{attacker.race} used {ability_text}, dealing {damage} damage and healing for {heal} HP!"
    elif ability_text in ["Searing Flames", "Dragon", "Dragon's Fury"]:
        damage = attacker.strength + random.randint(20, 30)
        log = f"{attacker.race} unleashed {ability_text} for {damage} damage!"
    elif ability_text in ["Savage Bite", "Beastman", "Feral Roar"]:
        damage = attacker.strength + random.randint(10, 20)
        log = f"{attacker.race} used {ability_text} and bit fiercely for {damage} damage!"
    elif ability_text in ["Wild Anarchy", "Kaosborne", "Chaotic Surge"]:
        if random.choice([True, False]):
            damage = attacker.strength + random.randint(5, 15)
            log = f"{attacker.race} channeled chaos via {ability_text}, dealing {damage} damage!"
        else:
            heal = random.randint(5, 15)
            attacker.current_health = min(attacker.base_health, attacker.current_health + heal)
            log = f"{attacker.race} let loose {ability_text} and healed for {heal} HP!"
    else:
        damage = attacker.strength + random.randint(1, 10)
        log = f"{attacker.race} performed a basic attack for {damage} damage."
    return log, damage

# -------------------------------
# Routes
# -------------------------------

# Dice Roll Route (animation before character creation)
@app.route("/roll")
def roll_dice():
    # Create a new character if not already in session or if the stored character cannot be found.
    char_id = session.get("char_id")
    character = None
    if char_id:
        character = Character.query.get(char_id)
    if character is None:
        # Create a new character and store its ID in the session.
        character = Character()
        db.session.add(character)
        db.session.commit()
        session["char_id"] = character.id
    return render_template("dice.html")

# Main Index: Show character info.
@app.route("/")
def index():
    char_id = session.get("char_id")
    character = None
    if char_id:
        character = Character.query.get(char_id)
    if character is None:
        # If no valid character exists, redirect to the dice roll so one is created.
        return redirect(url_for("roll_dice"))
    return render_template("index.html", character=character, ability_descriptions=ABILITY_DESCRIPTIONS)




# PvE Battle Route
@app.route("/battle", methods=["GET", "POST"])
def battle():
    char_id = session.get("char_id", None)
    if not char_id:
        return redirect(url_for("index"))
    character = Character.query.get(char_id)
    if "enemy" not in session:
        enemy = generate_enemy(character.level)
        session["enemy"] = enemy
    else:
        enemy = session["enemy"]

    battle_log = session.get("battle_log", [])

    if request.method == "POST":
        action = request.form.get("action")
        if action == "attack":
            base_damage = character.strength + random.randint(1, 10)
            # Apply type advantage multiplier
            mult = type_multiplier(character, type("dummy", (), {"race": enemy["race"]}))
            damage = int(base_damage * mult)
            enemy["current_health"] -= damage
            battle_log.append(f"You attacked the {enemy['race']} for {damage} damage!")
            if enemy["current_health"] <= 0:
                battle_log.append(f"You defeated the {enemy['race']}!")
                exp_gain = enemy["level"] * 50
                gold_gain = enemy["level"] * 20
                battle_log.append(f"You gained {exp_gain} EXP and {gold_gain} gold!")
                character.gain_exp(exp_gain)
                character.gold += gold_gain
                db.session.commit()
                session.pop("enemy", None)
                session["battle_log"] = battle_log
                return redirect(url_for("battle"))
            else:
                enemy_damage = random.randint(enemy["attack_min"], enemy["attack_max"])
                effective_damage = calculate_damage(enemy_damage, character.constitution)
                character.current_health -= effective_damage
                battle_log.append(f"The {enemy['race']} attacked you for {effective_damage} damage!")
                if character.current_health <= 0:
                    character.current_health = 0
                    battle_log.append("You have been defeated!")
                    db.session.commit()
                    session["battle_log"] = battle_log
                    return render_template("battle.html", character=character, enemy=enemy,
                                           battle_log=battle_log, game_over=True)
        elif action == "defend":
            enemy_damage = random.randint(enemy["attack_min"], enemy["attack_max"])
            reduced_damage = max(1, enemy_damage - (character.constitution // 2) - 5)
            character.current_health -= reduced_damage
            battle_log.append(f"You defended! The {enemy['race']} attacked for {reduced_damage} damage after reduction.")
            if character.current_health <= 0:
                character.current_health = 0
                battle_log.append("You have been defeated!")
                db.session.commit()
                session["battle_log"] = battle_log
                return render_template("battle.html", character=character, enemy=enemy,
                                           battle_log=battle_log, game_over=True)
        elif action == "use_potion":
            if character.potions > 0:
                heal_amount = random.randint(30, 50)
                character.current_health = min(character.base_health, character.current_health + heal_amount)
                character.potions -= 1
                battle_log.append(f"You used a potion and healed for {heal_amount} HP!")
                enemy_damage = random.randint(enemy["attack_min"], enemy["attack_max"])
                effective_damage = calculate_damage(enemy_damage, character.constitution)
                character.current_health -= effective_damage
                battle_log.append(f"While using a potion, the {enemy['race']} attacked you for {effective_damage} damage!")
                if character.current_health <= 0:
                    character.current_health = 0
                    battle_log.append("You have been defeated!")
                    db.session.commit()
                    session["battle_log"] = battle_log
                    return render_template("battle.html", character=character, enemy=enemy,
                                           battle_log=battle_log, game_over=True)
            else:
                battle_log.append("You have no potions left!")
        db.session.commit()
        session["enemy"] = enemy
        session["battle_log"] = battle_log

    return render_template("battle.html", character=character, enemy=enemy,
                           battle_log=battle_log, game_over=False)

# Shop Route
@app.route("/shop", methods=["GET", "POST"])
def shop():
    char_id = session.get("char_id", None)
    if not char_id:
        return redirect(url_for("index"))
    character = Character.query.get(char_id)
    message = ""
    if request.method == "POST":
        cost_per_potion = 20
        try:
            quantity = int(request.form.get("quantity", 0))
        except ValueError:
            quantity = 0
        total_cost = cost_per_potion * quantity
        if quantity > 0 and character.gold >= total_cost:
            character.gold -= total_cost
            character.potions += quantity
            message = f"You purchased {quantity} potion(s) for {total_cost} gold."
            db.session.commit()
        else:
            message = "Not enough gold or invalid quantity."
    return render_template("shop.html", character=character, message=message)

# Local PvP Route
@app.route("/pvp", methods=["GET", "POST"])
def pvp():
    p1_id = session.get("pvp_p1_id", None)
    p2_id = session.get("pvp_p2_id", None)
    if not p1_id or not p2_id:
        player1 = Character()
        player2 = Character()
        db.session.add(player1)
        db.session.add(player2)
        db.session.commit()
        session["pvp_p1_id"] = player1.id
        session["pvp_p2_id"] = player2.id
    else:
        player1 = Character.query.get(p1_id)
        player2 = Character.query.get(p2_id)
    pvp_turn = session.get("pvp_turn", 1)
    pvp_log = session.get("pvp_log", [])
    p1_defend = session.get("p1_defend", False)
    p2_defend = session.get("p2_defend", False)

    if request.method == "POST":
        action = request.form.get("action")
        if pvp_turn == 1:
            attacker = player1
            defender = player2
            defending_flag = p2_defend
        else:
            attacker = player2
            defender = player1
            defending_flag = p1_defend

        if action == "attack":
            base_damage = attacker.strength + random.randint(1, 10)
            # Apply type advantage multiplier
            mult = type_multiplier(attacker, defender)
            if defending_flag:
                base_damage //= 2
            damage = int(base_damage * mult)
            defender.current_health -= damage
            pvp_log.append(f"{attacker.race} attacked {defender.race} for {damage} damage!")
        elif action == "defend":
            if pvp_turn == 1:
                session["p1_defend"] = True
            else:
                session["p2_defend"] = True
            pvp_log.append(f"{attacker.race} is defending this turn!")
        elif action == "ability":
            log_text, ability_damage = use_ability(attacker, defender)
            defender.current_health -= ability_damage
            pvp_log.append(log_text)
        if defender.current_health <= 0:
            pvp_log.append(f"{defender.race} has been defeated! {attacker.race} wins!")
            db.session.commit()
            session["pvp_log"] = pvp_log
            return render_template("pvp.html", player1=player1, player2=player2, pvp_log=pvp_log, game_over=True, turn=pvp_turn)
        pvp_turn = 2 if pvp_turn == 1 else 1
        session["pvp_turn"] = pvp_turn
        session["p1_defend"] = False
        session["p2_defend"] = False
        db.session.commit()
        session["pvp_log"] = pvp_log

    return render_template("pvp.html", player1=player1, player2=player2, pvp_log=pvp_log, game_over=False, turn=session.get("pvp_turn", 1))

# Restart Route (clears sessions)
@app.route("/restart")
def restart():
    session.pop("char_id", None)
    session.pop("enemy", None)
    session.pop("battle_log", None)
    session.pop("pvp_p1_id", None)
    session.pop("pvp_p2_id", None)
    session.pop("pvp_turn", None)
    session.pop("pvp_log", None)
    session.pop("p1_defend", None)
    session.pop("p2_defend", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
