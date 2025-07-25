from Agents.actions import Actions
from Agents.actions import CompleteUnitAction

class ScoreAgent:
    def choose_best_actions(player_id, game_state, game_manager):
        while True:
            if ScoreAgent.choose_best_action(player_id, game_state, game_manager) == False:
                return

    def choose_best_action(player_id, game_state, game_manager):
        print("action", player_id)

        legal_actions = Actions.get_actions(player_id, game_state)
        if legal_actions == []:
            return False
        best_action = None
        for action in legal_actions:
            if best_action == None or action.score > best_action.score:
                best_action = action
        print(best_action.type, best_action.unit.id, best_action.score, best_action.target)
        if best_action.type == "Move" or best_action.type == "Swap":
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
        elif best_action.type == "Attack":
            CompleteUnitAction.attack(best_action.unit, best_action.target)
            game_manager.check_win()
        elif best_action.type == "Fortify":
            CompleteUnitAction.fortify(best_action.unit)

        best_action.unit.AI_last_move = best_action.type
        return True
    

            
            
            

