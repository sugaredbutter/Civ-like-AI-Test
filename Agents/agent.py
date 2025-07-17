from Agents.actions import Actions
from Agents.actions import CompleteUnitAction

class ScoreAgent:
    def choose_best_actions(player_id, game_state):
        while True:
            if ScoreAgent.choose_best_action(player_id, game_state) == False:
                return

    def choose_best_action(player_id, game_state):
        legal_actions = Actions.get_actions(player_id, game_state)
        if legal_actions == []:
            return False
        best_action = None
        for action in legal_actions:
            if best_action == None or action.score > best_action.score:
                best_action = action
        print(best_action.type, best_action.target, best_action.score)
        if best_action.type == "Move":
            CompleteUnitAction.move_unit(best_action.unit, best_action.target)
        return True
    

            
            
            

