import json
import random

class WorldModel:
    def __init__(self, json_file='world_state.json'):
        self.json_file = json_file
        self.world_state = self.load_or_create_world()

    def load_or_create_world(self):
        try:
            with open(self.json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return self.create_initial_world()

    def create_initial_world(self):
        # 创建一个随机的初始世界状态
        objects = [
            {
                "name": "苹果",
                "description": "一个红色的苹果",
                "state": "在桌子上"
            },
            {
                "name": "书",
                "description": "一本蓝色封面的书",
                "state": "在书架上"
            },
            {
                "name": "椅子",
                "description": "一把木制椅子",
                "state": "在房间角落"
            }
        ]
        robot = {
            "name": "机器人",
            "description": "一个能执行简单任务的机器人",
            "state": "站在房间中央"
        }
        world_state = {"objects": objects, "robot": robot}
        self.save_world_state(world_state)
        return world_state

    def save_world_state(self, world_state):
        with open(self.json_file, 'w', encoding='utf-8') as f:
            json.dump(world_state, f, ensure_ascii=False, indent=2)

    def update_object_state(self, object_name, new_state):
        for obj in self.world_state["objects"]:
            if obj["name"] == object_name:
                obj["state"] = new_state
                break
        else:
            print(f"未找到物体: {object_name}")
        self.save_world_state(self.world_state)

    def update_robot_state(self, new_state):
        self.world_state["robot"]["state"] = new_state
        self.save_world_state(self.world_state)

    def execute_command(self, command):
        # 这里可以使用大模型来解释命令并更新状态，为了演示,使用一个简单的示例初始化
        if "拿起" in command:
            object_name = command.split("拿起")[-1].strip()
            self.update_object_state(object_name, f"被机器人拿起")
            self.update_robot_state(f"正在拿着{object_name}")
        elif "放下" in command:
            object_name = command.split("放下")[-1].strip()
            self.update_object_state(object_name, "在地上")
            self.update_robot_state("没有拿着任何东西")
        else:
            print("无法理解的命令")

    def print_world_state(self):
        print(json.dumps(self.world_state, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    world = WorldModel()
    print("初始世界状态:")
    world.print_world_state()

    world.execute_command("拿起 苹果")
    print("\n执行'拿起苹果'后的世界状态:")
    world.print_world_state()

    world.execute_command("放下 苹果")
    print("\n执行'放下苹果'后的世界状态:")
    world.print_world_state()

