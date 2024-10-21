import json
import llm_api
import colorama

# Initialize colorama
colorama.init()

class WorldModel:
    def __init__(self, json_file='world_state.json', initial_description=None):
        self.json_file = json_file
        self.world_state = self.load_or_create_world(initial_description)

    def load_or_create_world(self, initial_description):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                world_state = json.load(f)
                if 'description' not in world_state:
                    world_state['description'] = self.generate_world_description(world_state)
                return world_state
        except FileNotFoundError:
            return self.create_initial_world(initial_description)

    def create_initial_world(self, initial_description):
        world_state = self.extract_world_state_from_description(initial_description)
        world_state['description'] = initial_description
        self.save_world_state(world_state)
        return world_state

    def extract_world_state_from_description(self, description):
        prompt = f"""
        Based on the following description, please extract a detailed world state and return it in JSON format:

        Description:
        {description}

        Please return a JSON with the following structure, describing each object's state, attributes, and positional relationships in as much detail as possible:
        {{
            "objects": [
                {{
                    "name": "Object name",
                    "description": "Detailed description of the object, including color, size, material, etc.",
                    "state": "Current state of the object, including its interaction state with other objects",
                    "location": "Specific location of the object, including its position relative to other objects",
                    "attributes": ["List of special attributes of the object, such as movable, openable, etc."]
                }}
            ],
            "robot": {{
                "name": "Robot",
                "description": "Detailed description of the robot, including appearance, functions, etc.",
                "state": "Current state of the robot, including whether it's performing tasks, holding items, etc.",
                "location": "Specific location of the robot, including its position relative to other objects",
                "capabilities": ["List of robot's abilities, such as moving, grasping, opening doors, etc."]
            }},
            "environment": {{
                "description": "Overall description of the environment, including room size, lighting, temperature, etc.",
                "features": ["List of special features of the environment, such as doors, windows, walls, etc."]
            }}
        }}
        """
        response = llm_api.llm_api(prompt, model="gpt-4o-mini", temperature=0.7, is_visual=False)
        return response if isinstance(response, dict) else {}

    def generate_world_description(self, world_state):
        prompt = f"""
        Please generate a natural language description based on the following detailed world state:

        {json.dumps(world_state, ensure_ascii=False, indent=2)}

        Please generate a fluent, vivid, and detailed description that includes the following elements:
        1. Overall atmosphere and characteristics of the environment
        2. Detailed state, attributes, and positional relationships of all objects
        3. Current state, position, and capabilities of the robot
        4. Interrelationships between objects and possible interactions
        5. Any potential changes or dynamic elements

        The description should allow readers to clearly imagine the entire scene. Avoid using adjectives or attribute information in the description, only describe states, positions, relationships, etc.
        Return in the following format:
        Environment description.\nObject 1 description.\nObject 2 description.\nObject 3 description.\nRobot description.
        """
        response = llm_api.llm_api(prompt, model="gpt-4o-mini", temperature=0.7, is_visual=False)
        return response if isinstance(response, str) else ""

    def save_world_state(self, world_state):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(world_state, f, ensure_ascii=False, indent=2)

    def update_object_state(self, object_name, new_state, new_location):
        for obj in self.world_state["objects"]:
            if obj["name"] == object_name:
                obj["state"] = new_state
                obj["location"] = new_location
                break
        else:
            print(colorama.Fore.RED + f"Object not found: {object_name}" + colorama.Fore.RESET)
        self.world_state['description'] = self.generate_world_description(self.world_state)
        self.save_world_state(self.world_state)

    def update_robot_state(self, new_state, new_location):
        self.world_state["robot"]["state"] = new_state
        self.world_state["robot"]["location"] = new_location
        self.world_state['description'] = self.generate_world_description(self.world_state)
        self.save_world_state(self.world_state)

    def execute_command(self, command):
        # First, check if the command is executable
        check_prompt = f"""
        Based on the following world state, strictly check if the command "{command}" can be executed:

        World state:
        {json.dumps(self.world_state, ensure_ascii=False, indent=2)}

        Please consider the following factors:
        1. Current position and capabilities of the robot
        2. Position, state, and attributes of objects
        3. Environmental limitations and features
        4. Physical laws and logical possibilities
        5. Whether the command contains only one action, not a series of actions

        Return a result in JSON format containing the following fields:
        1. 'executable': Boolean, indicating whether the command is executable
        2. 'reason': String, detailed explanation of why it is or is not executable
        """

        check_response = llm_api.llm_api(check_prompt, model="gpt-4o-mini", temperature=0.7, is_visual=True)

        if isinstance(check_response, dict) and 'executable' in check_response:
            if not check_response['executable']:
                print(colorama.Fore.RED + f"Cannot execute command: {check_response['reason']}" + colorama.Fore.RESET)
                return

        # If the command is executable, continue execution
        prompt = f"""You are an intelligent robot. Please execute the command based on the following detailed world state:
        
        World state:
        {json.dumps(self.world_state, ensure_ascii=False, indent=2)}
        
        Human command: {command}
        
        Please execute this command and return a result in JSON format. When executing the command, please follow these rules:
        1. Execute strictly according to the command, performing only one action at a time
        2. Consider physical limitations and logical possibilities
        3. Describe the action process and results in detail
        4. If it cannot be executed, please explain the reason

        The returned JSON should contain the following fields:
        1. 'success': Boolean, indicating whether the command was successfully executed
        2. 'message': String, detailed description of the execution process, result, or reason for failure
        3. 'updates': List, containing the object states that need to be updated, each element is a dictionary in the format:
           {{"object_name": "Object name", 
             "new_state": "New state, detailed description of the object's state change, including its relationship with other objects", 
             "new_location": "New location, detailed description of the object's position change",
             "attribute_changes": ["Any changes in attributes"]
           }}
        4. 'environment_changes': Dictionary, describing any changes in the environment
        
        For example:
        {{
            "success": true,
            "message": "The robot successfully moved slowly to the table.",
            "updates": [
                {{"object_name": "Robot", "new_state": "Standing next to the table", "new_location": "Next to the table", "attribute_changes": ["Current position: Next to the table"]}}
            ],
            "environment_changes": {{
                "description": "The atmosphere in the room has changed slightly, the robot's movement caused a slight air flow."
            }}
        }}
        """
        
        response = llm_api.llm_api(prompt, model="gpt-4o-mini", temperature=0.7, is_visual=False)
        
        if isinstance(response, dict) and 'success' in response:
            if response['success']:
                for update in response['updates']:
                    obj_name = update['object_name']
                    new_state = update['new_state']
                    new_location = update['new_location']
                    if self.is_similar_object(obj_name, "Robot"):
                        self.update_robot_state(new_state, new_location)
                    else:
                        self.update_object_state(obj_name, new_state, new_location)
                if 'environment_changes' in response:
                    self.world_state['environment'].update(response['environment_changes'])
                print(colorama.Fore.GREEN + response['message'] + colorama.Fore.RESET)
            else:
                print(colorama.Fore.RED + f"Execution failed: {response['message']}" + colorama.Fore.RESET)
        else:
            print(colorama.Fore.RED + "Incomprehensible response" + colorama.Fore.RESET)

    def print_world_state(self):
        print(colorama.Fore.CYAN + self.world_state['description'] + colorama.Fore.RESET)

    def is_similar_object(self, obj_name, target_name):
        if obj_name.lower() in target_name.lower():
            return True
        if target_name.lower() in obj_name.lower():
            return True
        return False

if __name__ == "__main__":
    world = WorldModel(initial_description="There is a table in the center of the room with a book and an apple on it. In the northeast corner, there is a bookshelf with books on it, including one specific book. In the southwest corner, there is a chair. There is a door on the north side with a doorknob. In the center of the room, there is a robot capable of moving, grasping objects, and opening/closing doors.")
    while True:
        print(colorama.Fore.WHITE + "\n\n----------------------------------------" + colorama.Fore.RESET)
        print(colorama.Fore.YELLOW + "\nCurrent world state:" + colorama.Fore.RESET)
        world.print_world_state()
        command = input(colorama.Fore.MAGENTA + "Please enter a command: " + colorama.Fore.RESET)
        world.execute_command(command)
        print(colorama.Fore.YELLOW + f"\nWorld state after executing '{command}':" + colorama.Fore.RESET)
        world.print_world_state()
        print(colorama.Fore.WHITE + "\n\n----------------------------------------" + colorama.Fore.RESET)
