import json

class SaveLoad:
    @staticmethod
    def save_game(player, file_path="game_save.json"):
        # 플레이어 상태를 JSON 형식으로 저장
        data = {
            "player": {
                "x": player.x,
                "y": player.y,
                "level": getattr(player, "level", 1),  # 기본값: 1
                "experience": getattr(player, "experience", 0),  # 기본값: 0
                "health": getattr(player, "health", 100),  # 기본값: 100
                "money": getattr(player, "money", 100),  # 기본값: 100
                "inventory": getattr(player, "inventory",[])  # 기본값: 빈 리스트
            }
        }
        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
        print("게임이 저장되었습니다!")

    @staticmethod
    def load_game(player, file_path="game_save.json"):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            player.x = data["player"]["x"]
            player.y = data["player"]["y"]
            player.level = data["player"].get("level", 1)
            player.experience = data["player"].get("experience", 0)
            player.health = data["player"].get("health", 100)
            player.money = data["player"].get("money", 100)
            player.inventory = data["player"].get("inventory", [])
            print("게임이 로드되었습니다!")
        except FileNotFoundError:
            print("저장된 게임 파일이 없습니다.")
        except json.JSONDecodeError:
            print("저장 파일이 손상되었습니다.")
