class ActionsStack:
    """Class to keep track of actions performed in a gui, also allows removing actions etc"""

    def __init__(self):
        self.actions: list[tuple[str, object]] = []
        self.building_priority: list[str] = []
        self.drone_priority: list[str] = []

    def add_action(self, action_type: str, action):
        """Adds action to action_stack
        Vars:
        action_type: "building" or "drone"
        action: building or drone object"""
        if action == "building":
            pass
        self.actions.append((action_type, action))

    def remove_action(self, action_type: str, action):
        self.actions.remove((action_type, action))

    def retrieve_last_action(self):
        if self.actions:
            return self.actions.pop()

    def clear(self):
        self.actions = []
        return None
