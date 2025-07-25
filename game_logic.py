"""
Game Logic and Mechanics for Hand Hockey Discord Bot
Handles range calculations and action evaluations
"""
from typing import Tuple, Dict, Any
from config import Config

class GameLogic:
    """Core game logic for Hand Hockey"""
    
    @staticmethod
    def get_action_range(attacker_role: str, defender_role: str, scenario: str) -> Tuple[int, int]:
        """Get valid action range based on roles and scenario"""
        ranges = {
            ("ST", "DEF", "dribbling"): (1, 3),
            ("ST", "MF", "dribbling"): (1, 3),
            ("MF", "DEF", "passing"): (1, 3),
            ("ST", "GK", "shooting"): (1, 6),
            ("ST", "MF", "quick_pass"): (1, 2),
            ("ST", "DEF", "corner_kick"): (4, 6),
            ("GK", "ANY", "interception"): (1, 3),
            ("MF", "GK", "long_shot"): (2, 5),
            ("DEF", "ST", "tackle"): (1, 4),
            ("ANY", "ANY", "default"): (1, 3)
        }
        
        key = (attacker_role.upper(), defender_role.upper(), scenario.lower())
        return ranges.get(key, ranges[("ANY", "ANY", "default")])
    
    @staticmethod
    def evaluate_action(attacker_action: int, defender_action: int, 
                       attacker_role: str, defender_role: str, scenario: str = "default") -> Dict[str, Any]:
        """Evaluate the outcome of actions"""
        
        # Validate action ranges first
        valid_range = GameLogic.get_action_range(attacker_role, defender_role, scenario)
        if not (valid_range[0] <= attacker_action <= valid_range[1]):
            return {
                "result": "invalid_action",
                "description": f"Invalid action for {attacker_role}. Must be between {valid_range[0]}-{valid_range[1]}",
                "success": False
            }
        
        if not (valid_range[0] <= defender_action <= valid_range[1]):
            return {
                "result": "invalid_action", 
                "description": f"Invalid action for {defender_role}. Must be between {valid_range[0]}-{valid_range[1]}",
                "success": False
            }
        
        # Same number scenarios
        if attacker_action == defender_action:
            if defender_role.upper() == "GK":
                return {
                    "result": "save",
                    "description": "Goalkeeper makes a crucial save!",
                    "success": False,
                    "next_action": "corner_kick"
                }
            elif attacker_role.upper() == "ST" and defender_role.upper() == "DEF":
                return {
                    "result": "foul",
                    "description": "Defensive foul committed!",
                    "success": True,
                    "next_action": "free_kick"
                }
            else:
                return {
                    "result": "interception",
                    "description": "Ball intercepted! Possession changes.",
                    "success": False,
                    "next_action": "possession_change"
                }
        
        # Attacker wins
        elif attacker_action > defender_action:
            if scenario == "shooting" and defender_role.upper() == "GK":
                return {
                    "result": "goal",
                    "description": "GOAL! What a fantastic strike!",
                    "success": True,
                    "next_action": "kickoff"
                }
            else:
                return {
                    "result": "success",
                    "description": "Action successful! Attacker advances.",
                    "success": True,
                    "next_action": "continue_attack"
                }
        
        # Defender wins
        else:
            if defender_role.upper() == "GK":
                return {
                    "result": "save",
                    "description": "Great save by the goalkeeper!",
                    "success": False,
                    "next_action": "goalkeeper_possession"
                }
            else:
                return {
                    "result": "blocked",
                    "description": "Action blocked by defender!",
                    "success": False,
                    "next_action": "possession_change"
                }
    
    @staticmethod
    def calculate_success_probability(attacker_role: str, defender_role: str, scenario: str) -> float:
        """Calculate probability of attack success based on roles and scenario"""
        
        # Base probabilities
        role_advantages = {
            ("ST", "DEF"): 0.6,  # Striker vs Defender
            ("ST", "MF"): 0.7,   # Striker vs Midfielder  
            ("ST", "GK"): 0.4,   # Striker vs Goalkeeper
            ("MF", "DEF"): 0.5,  # Midfielder vs Defender
            ("MF", "GK"): 0.3,   # Midfielder vs Goalkeeper
            ("DEF", "ST"): 0.4,  # Defender vs Striker (tackles)
        }
        
        # Scenario modifiers
        scenario_modifiers = {
            "shooting": -0.1,      # Shooting is harder
            "dribbling": 0.0,      # Neutral
            "passing": 0.1,        # Passing is easier
            "corner_kick": 0.2,    # Corner kicks have advantage
            "free_kick": 0.15,     # Free kicks have slight advantage
            "penalty": 0.8,        # Penalties heavily favor attacker
        }
        
        key = (attacker_role.upper(), defender_role.upper())
        base_prob = role_advantages.get(key, 0.5)  # Default 50/50
        
        scenario_mod = scenario_modifiers.get(scenario.lower(), 0.0)
        
        final_prob = max(0.1, min(0.9, base_prob + scenario_mod))
        return final_prob
    
    @staticmethod
    def get_scenario_description(scenario: str) -> str:
        """Get human-readable description of scenario"""
        descriptions = {
            "dribbling": "Player attempts to dribble past opponent",
            "passing": "Player attempts to pass the ball",
            "shooting": "Player takes a shot on goal",
            "corner_kick": "Corner kick situation",
            "free_kick": "Free kick awarded",
            "penalty": "Penalty kick situation",
            "tackle": "Defender attempts to tackle",
            "interception": "Player attempts to intercept pass",
            "long_shot": "Long-range shot attempt",
            "quick_pass": "Quick pass attempt",
            "default": "General gameplay situation"
        }
        
        return descriptions.get(scenario.lower(), descriptions["default"])
    
    @staticmethod
    def validate_team_formation(team_players: Dict[str, str]) -> Tuple[bool, str]:
        """Validate team formation has required positions"""
        required_positions = {"GK": 1, "DEF": 1, "MF": 1, "ST": 1}
        position_counts = {}
        
        for player_id, position in team_players.items():
            position = position.upper()
            position_counts[position] = position_counts.get(position, 0) + 1
        
        # Check if all required positions are filled
        for position, required_count in required_positions.items():
            if position_counts.get(position, 0) < required_count:
                return False, f"Team needs at least {required_count} {position}"
        
        return True, "Formation is valid"

class MatchState:
    """Manages the state of an active match"""
    
    def __init__(self, match_id: str):
        self.match_id = match_id
        self.score = {"A": 0, "B": 0}
        self.possession = "A"  # Which team has possession
        self.current_scenario = "kickoff"
        self.turn_count = 0
        self.match_time = 0  # In minutes
        self.status = "active"
        
        # Statistics tracking
        self.stats = {
            "A": {"shots": 0, "saves": 0, "fouls": 0, "corners": 0},
            "B": {"shots": 0, "saves": 0, "fouls": 0, "corners": 0}
        }
    
    def update_score(self, team: str, points: int = 1):
        """Update team score"""
        if team in self.score:
            self.score[team] += points
    
    def switch_possession(self):
        """Switch possession to the other team"""
        self.possession = "B" if self.possession == "A" else "A"
    
    def update_stats(self, team: str, stat_type: str, value: int = 1):
        """Update team statistics"""
        if team in self.stats and stat_type in self.stats[team]:
            self.stats[team][stat_type] += value
    
    def get_match_summary(self) -> Dict[str, Any]:
        """Get current match summary"""
        return {
            "match_id": self.match_id,
            "score": self.score.copy(),
            "possession": self.possession,
            "scenario": self.current_scenario,
            "time": self.match_time,
            "status": self.status,
            "stats": self.stats.copy(),
            "turn_count": self.turn_count
        }
