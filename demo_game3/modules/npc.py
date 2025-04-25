import pygame
import json
from modules.player import TILE_SIZE 

class NPC:
    # 스프라이트 캐싱: 동일한 경로의 스프라이트는 한 번만 로드
    sprite_cache = {}

    def __init__(self, x, y, sprite_path, name, map_name, dialogue=None):
        self.x = x
        self.y = y
        self.sprite_path = sprite_path
        # 캐시에 있으면 재사용, 없으면 로드 후 캐싱
        if sprite_path in NPC.sprite_cache:
            self.sprite = NPC.sprite_cache[sprite_path]
        else:
            self.sprite = pygame.image.load(sprite_path).convert_alpha()
            self.sprite = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE))
            NPC.sprite_cache[sprite_path] = self.sprite
        self.name = name
        self.map_name = map_name  # NPC가 속한 맵 이름 저장
        self.dialogue = dialogue if dialogue is not None else []
        self.index = 0  # 대화 인덱스
        

    def get_hitbox(self):
        """
        NPC의 히트박스를 월드 좌표(픽셀 단위)로 반환합니다.
        """
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def draw(self, screen, ui):
        camera_x, camera_y = ui.camera_x, ui.camera_y
        screen.blit(self.sprite, ((self.x - camera_x) * TILE_SIZE, (self.y - camera_y) * TILE_SIZE))
        screen.blit(ui.font.render(self.name, True, (255, 255, 255)), 
                    ((self.x - camera_x) * TILE_SIZE, (self.y - camera_y) * TILE_SIZE - 20))
        
        # 히트박스 표시 (디버깅 용도)
        hitbox = pygame.Rect((self.x - camera_x) * TILE_SIZE, (self.y - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(screen, (255, 0, 0), hitbox, 2)

    def get_dialogue(self):
        if self.dialogue and 0 <= self.index < len(self.dialogue):
            text = self.dialogue[self.index].get("text")
            self.index += 1
            if self.index >= len(self.dialogue):
                self.index = 0
            return text
        return None
    
    def show_dialogue(self, ui):
        ui.show_dialogue(self.get_dialogue())



class NPCManager:
    def __init__(self):
        self.npcs = []

    def load(self, filename):
        """
        JSON 파일에서 NPC 데이터를 불러와 NPC 객체를 생성하고 리스트에 저장합니다.
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading NPC data from {filename}: {e}")
            return

        for npc_data in data.get("npcs", []):
            npc = NPC(
                x=npc_data["x"],
                y=npc_data["y"],
                sprite_path=npc_data["sprite"],
                name=npc_data["name"],
                map_name=npc_data["map_name"],  # JSON에서 맵 이름을 받음
                dialogue=npc_data.get("dialogue")
            )
            self.npcs.append(npc)

    def get_npcs(self, current_map):
        """
        현재 맵의 이름과 일치하는 NPC들만 필터링하여 반환합니다.
        """
        return [npc for npc in self.npcs if npc.map_name == current_map.name]

    def check_npc_collision(self, player_hitbox):
        """
        플레이어의 히트박스와 충돌하는 NPC가 있으면 해당 NPC 객체를 반환합니다.
        없으면 None을 반환합니다.
        """
        for npc in self.npcs:
            if npc.get_hitbox().colliderect(player_hitbox):
                return npc
        return None

    def interact(self, npc ,ui):
        npc.show_dialogue(ui)