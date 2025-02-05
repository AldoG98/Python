import random
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class StatusEffect(Enum):
    BURN = "Burn"
    FREEZE = "Freeze"
    PARALYZE = "Paralyze"
    POISON = "Poison"
    NONE = None

@dataclass
class Move:
    name: str
    type: str
    power: int
    accuracy: int
    pp: int
    max_pp: int
    status_effect: Optional[StatusEffect] = None
    status_chance: float = 0.0
    
    def __str__(self) -> str:
        return f"{self.name} (PP: {self.pp}/{self.max_pp})"

class PokemonType(Enum):
    FIRE = "Fire"
    WATER = "Water"
    GRASS = "Grass"
    ELECTRIC = "Electric"
    NORMAL = "Normal"

class Item:
    def __init__(self, name: str, effect_value: int, quantity: int):
        self.name = name
        self.effect_value = effect_value
        self.quantity = quantity

class Pokemon:
    def __init__(self, name: str, type1: PokemonType, hp: int, moves: Dict[str, Move]):
        self.name = name
        self.type1 = type1
        self.max_hp = hp
        self.current_hp = hp
        self.moves = moves
        self.status = StatusEffect.NONE
        self.items = {
            'Potion': Item('Potion', 20, 2),
            'Super Potion': Item('Super Potion', 50, 1),
            'Full Restore': Item('Full Restore', 999, 1)
        }
        self.stats = {
            'accuracy': 100,
            'evasion': 100
        }
    
    def is_fainted(self) -> bool:
        return self.current_hp <= 0
    
    def can_move(self) -> bool:
        if self.status == StatusEffect.FREEZE and random.random() < 0.8:
            print(f"{self.name} is frozen and couldn't move!")
            return False
        if self.status == StatusEffect.PARALYZE and random.random() < 0.25:
            print(f"{self.name} is paralyzed and couldn't move!")
            return False
        return True
    
    def apply_status_effects(self):
        if self.status == StatusEffect.BURN:
            damage = max(1, self.max_hp // 16)
            self.current_hp = max(0, self.current_hp - damage)
            print(f"{self.name} was hurt by its burn!")
        elif self.status == StatusEffect.POISON:
            damage = max(1, self.max_hp // 8)
            self.current_hp = max(0, self.current_hp - damage)
            print(f"{self.name} was hurt by poison!")
    
    def use_item(self, item_name: str) -> bool:
        if item_name not in self.items or self.items[item_name].quantity <= 0:
            print(f"{self.name} has no {item_name} left!")
            return False
        
        item = self.items[item_name]
        if item_name == 'Full Restore':
            self.current_hp = self.max_hp
            self.status = StatusEffect.NONE
            print(f"{self.name} used a Full Restore! HP fully restored and status cleared!")
        else:
            heal_amount = min(item.effect_value, self.max_hp - self.current_hp)
            self.current_hp += heal_amount
            print(f"{self.name} used a {item_name}! HP restored by {heal_amount}!")
        
        item.quantity -= 1
        return True

class BattleSystem:
    def __init__(self):
        self.type_effectiveness = {
            PokemonType.FIRE: {PokemonType.GRASS: 2.0, PokemonType.WATER: 0.5, PokemonType.ELECTRIC: 1.0, PokemonType.FIRE: 0.5},
            PokemonType.WATER: {PokemonType.FIRE: 2.0, PokemonType.GRASS: 0.5, PokemonType.ELECTRIC: 0.5, PokemonType.WATER: 0.5},
            PokemonType.GRASS: {PokemonType.WATER: 2.0, PokemonType.FIRE: 0.5, PokemonType.ELECTRIC: 1.0, PokemonType.GRASS: 0.5},
            PokemonType.ELECTRIC: {PokemonType.WATER: 2.0, PokemonType.GRASS: 1.0, PokemonType.FIRE: 1.0, PokemonType.ELECTRIC: 0.5}
        }
    
    def calculate_accuracy(self, move: Move, attacker: Pokemon, defender: Pokemon) -> bool:
        if move.accuracy == 100:
            return True
        
        accuracy = move.accuracy * (attacker.stats['accuracy'] / 100)
        evasion = defender.stats['evasion'] / 100
        hit_chance = accuracy * evasion / 100
        
        return random.random() < hit_chance
    
    def calculate_damage(self, move: Move, attacker: Pokemon, defender: Pokemon) -> int:
        if move.pp <= 0:
            print(f"{attacker.name} is out of PP for {move.name}!")
            return 0
        
        if not self.calculate_accuracy(move, attacker, defender):
            print(f"{attacker.name}'s attack missed!")
            move.pp -= 1
            return 0
        
        move.pp -= 1
        
        # Base damage calculation
        damage = move.power
        
        # Type effectiveness
        if isinstance(move.type, PokemonType) and isinstance(defender.type1, PokemonType):
            if move.type in self.type_effectiveness and defender.type1 in self.type_effectiveness[move.type]:
                effectiveness = self.type_effectiveness[move.type][defender.type1]
                damage *= effectiveness
                if effectiveness > 1:
                    print("It's super effective!")
                elif effectiveness < 1:
                    print("It's not very effective...")
        
        # Critical hit
        if random.random() < 0.0625:  # 1/16 chance
            damage *= 1.5
            print("A critical hit!")
        
        # Status effect application
        if move.status_effect and random.random() < move.status_chance:
            if defender.status == StatusEffect.NONE:
                defender.status = move.status_effect
                print(f"{defender.name} was {move.status_effect.value.lower()}ed!")
        
        # STAB (Same Type Attack Bonus)
        if move.type == attacker.type1:
            damage *= 1.5
        
        # Burn damage reduction
        if attacker.status == StatusEffect.BURN and move.type != PokemonType.NORMAL:
            damage *= 0.5
        
        return int(damage * random.uniform(0.85, 1.0))

def create_pokemon_roster() -> Dict[str, Pokemon]:
    return {
        'Charizard': Pokemon('Charizard', PokemonType.FIRE, 120, {
            'Flamethrower': Move('Flamethrower', PokemonType.FIRE, 35, 95, 10, 10, StatusEffect.BURN, 0.1),
            'Dragon Claw': Move('Dragon Claw', PokemonType.NORMAL, 30, 100, 15, 15),
            'Air Slash': Move('Air Slash', PokemonType.NORMAL, 25, 90, 15, 15),
            'Fire Blast': Move('Fire Blast', PokemonType.FIRE, 45, 85, 5, 5, StatusEffect.BURN, 0.3),
        }),
        'Blastoise': Pokemon('Blastoise', PokemonType.WATER, 110, {
            'Hydro Pump': Move('Hydro Pump', PokemonType.WATER, 45, 85, 5, 5),
            'Surf': Move('Surf', PokemonType.WATER, 35, 95, 10, 10),
            'Ice Beam': Move('Ice Beam', PokemonType.WATER, 35, 95, 10, 10, StatusEffect.FREEZE, 0.1),
            'Water Pulse': Move('Water Pulse', PokemonType.WATER, 30, 100, 15, 15),
        }),
        'Venusaur': Pokemon('Venusaur', PokemonType.GRASS, 115, {
            'Solar Beam': Move('Solar Beam', PokemonType.GRASS, 45, 85, 5, 5),
            'Razor Leaf': Move('Razor Leaf', PokemonType.GRASS, 30, 95, 15, 15),
            'Poison Powder': Move('Poison Powder', PokemonType.GRASS, 0, 75, 10, 10, StatusEffect.POISON, 1.0),
            'Vine Whip': Move('Vine Whip', PokemonType.GRASS, 25, 100, 20, 20),
        }),
        'Pikachu': Pokemon('Pikachu', PokemonType.ELECTRIC, 90, {
            'Thunderbolt': Move('Thunderbolt', PokemonType.ELECTRIC, 40, 95, 10, 10, StatusEffect.PARALYZE, 0.1),
            'Quick Attack': Move('Quick Attack', PokemonType.NORMAL, 20, 100, 20, 20),
            'Thunder Wave': Move('Thunder Wave', PokemonType.ELECTRIC, 0, 85, 15, 15, StatusEffect.PARALYZE, 1.0),
            'Thunder': Move('Thunder', PokemonType.ELECTRIC, 50, 70, 5, 5, StatusEffect.PARALYZE, 0.3),
        })
    }

def display_health_bar(pokemon: Pokemon) -> str:
    health_percentage = pokemon.current_hp / pokemon.max_hp
    bar_length = 20
    filled_length = int(bar_length * health_percentage)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    status_text = f" [{pokemon.status.value}]" if pokemon.status != StatusEffect.NONE else ""
    return f"{pokemon.name} HP: {bar} ({pokemon.current_hp}/{pokemon.max_hp}){status_text}"

def display_menu(options: List[str]) -> int:
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): "))
            if 1 <= choice <= len(options):
                return choice - 1
            print("Invalid choice! Please try again.")
        except ValueError:
            print("Please enter a valid number!")

def get_computer_move(pokemon: Pokemon) -> Move:
    # Simple AI to choose moves
    available_moves = [move for move in pokemon.moves.values() if move.pp > 0]
    if not available_moves:
        return random.choice(list(pokemon.moves.values()))
    
    # Prioritize moves with status effects if Pokemon is healthy
    if pokemon.current_hp > pokemon.max_hp * 0.7:
        status_moves = [move for move in available_moves if move.status_effect]
        if status_moves:
            return random.choice(status_moves)
    
    # Prioritize powerful moves if Pokemon is low on health
    if pokemon.current_hp < pokemon.max_hp * 0.3:
        powerful_moves = [move for move in available_moves if move.power >= 40]
        if powerful_moves:
            return random.choice(powerful_moves)
    
    return random.choice(available_moves)

def main():
    print("\n=== Welcome to Pokémon Battle Simulator! ===\n")
    battle_system = BattleSystem()
    pokemon_roster = create_pokemon_roster()
    
    print("Available Pokémon:")
    pokemon_names = list(pokemon_roster.keys())
    player_pokemon = pokemon_roster[pokemon_names[display_menu(pokemon_names)]]
    
    computer_pokemon = random.choice([p for p in pokemon_roster.values() if p != player_pokemon])
    print(f"\nYou chose {player_pokemon.name}! Opponent chose {computer_pokemon.name}!")
    
    while not (player_pokemon.is_fainted() or computer_pokemon.is_fainted()):
        print("\n" + "="*50)
        print(display_health_bar(player_pokemon))
        print(display_health_bar(computer_pokemon))
        
        # Player turn
        print(f"\n{player_pokemon.name}'s turn!")
        options = ["Fight", "Use Item"]
        choice = display_menu(options)
        
        turn_completed = False
        
        if choice == 0:  # Fight
            print(f"\n{player_pokemon.name}'s moves:")
            moves = list(player_pokemon.moves.values())
            move = moves[display_menu([str(move) for move in moves])]
            
            if player_pokemon.can_move():
                print(f"\n{player_pokemon.name} used {move.name}!")
                damage = battle_system.calculate_damage(move, player_pokemon, computer_pokemon)
                computer_pokemon.current_hp = max(0, computer_pokemon.current_hp - damage)
                turn_completed = True
        else:  # Use Item
            items = [f"{item.name} (x{item.quantity})" for item in player_pokemon.items.values() if item.quantity > 0]
            if items:
                item_name = list(player_pokemon.items.keys())[display_menu(items)]
                if player_pokemon.use_item(item_name):
                    turn_completed = True
            else:
                print("No items left!")
        
        if not turn_completed:
            continue  # If turn wasn't completed (e.g., no items available), player gets another chance to choose
        
        if computer_pokemon.is_fainted():
            print(f"\n{computer_pokemon.name} fainted! You win!")
            break
        
        # Computer turn
        print(f"\n{computer_pokemon.name}'s turn!")
        time.sleep(1)  # Add dramatic pause
        
        if computer_pokemon.current_hp < computer_pokemon.max_hp * 0.3:
            # Try to use a healing item
            for item_name, item in computer_pokemon.items.items():
                if item.quantity > 0:
                    computer_pokemon.use_item(item_name)
                    break
        
        if computer_pokemon.can_move():
            computer_move = get_computer_move(computer_pokemon)
            print(f"\n{computer_pokemon.name} used {computer_move.name}!")
            damage = battle_system.calculate_damage(computer_move, computer_pokemon, player_pokemon)
            player_pokemon.current_hp = max(0, player_pokemon.current_hp - damage)
        
        # Apply status effects at end of turn
        player_pokemon.apply_status_effects()
        computer_pokemon.apply_status_effects()
        
        if player_pokemon.is_fainted():
            print(f"\n{player_pokemon.name} fainted! You lose!")
            break

if __name__ == "__main__":
    main()
