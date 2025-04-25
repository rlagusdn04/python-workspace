import pygame
import json
import math

TILE_SIZE = 32  # 타일 크기

class SpriteSheet:
    def __init__(self, file_path, scale_factor=0.5):
        self.sheet = pygame.image.load(file_path)
        self.scale_factor = scale_factor

    def get_image(self, x, y, width, height):
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), (x, y, width, height))
        if self.scale_factor != 1:
            new_width = int(width * self.scale_factor)
            new_height = int(height * self.scale_factor)
            image = pygame.transform.scale(image, (new_width, new_height))
        return image

class Animation:
    def __init__(self, images, frame_duration):
        self.images = images
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.time_counter = 0

    def update(self, dt):
        self.time_counter += dt
        if self.time_counter >= self.frame_duration:
            self.time_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.images)

    def get_current_image(self):
        return self.images[self.current_frame]

class Player:
    def __init__(self, name="Player", x=0, y=0, sprite_path="assets/ditto.png", 
                 hp=100, level=1, exp=0, money=0, inventory=None):
        self.name = name
        self.x = x      # 월드 좌표 (타일 단위)
        self.y = y
        self.sprite_path = sprite_path
        self.sprite_sheet = SpriteSheet(sprite_path)
        self.hp = hp
        self.level = level
        self.exp = exp
        self.money = money
        self.inventory = inventory if inventory is not None else []  # 인벤토리는 아이템 목록
        self.hitbox = None

        # 충돌 판정을 위한 히트박스 크기 (여기서는 TILE_SIZE로 설정)
        self.width = TILE_SIZE
        self.height = TILE_SIZE

        self.current_animation = "stand"
        self.animations = self._create_animations()
        self.animator = Animation(self.animations[self.current_animation], 100)

    def _create_animations(self):
        return {
            "stand": [
                self.sprite_sheet.get_image(0, 0, 128, 128),
                self.sprite_sheet.get_image(128, 0, 128, 128),
                self.sprite_sheet.get_image(256, 0, 128, 128),
            ],
            "walk_down": [
                self.sprite_sheet.get_image(0, 0, 128, 128),
                self.sprite_sheet.get_image(128, 0, 128, 128),
                self.sprite_sheet.get_image(256, 0, 128, 128),
            ],
            "walk_up": [
                self.sprite_sheet.get_image(0, 128 * 5, 128, 128),
                self.sprite_sheet.get_image(0, 128 * 6, 128, 128),
                self.sprite_sheet.get_image(128 * 3, 128 * 7, 128, 128),
                self.sprite_sheet.get_image(128 * 2, 128 * 7, 128, 128)
            ],
            "walk_left": [
                pygame.transform.flip(img, True, False)
                for img in [
                    self.sprite_sheet.get_image(0, 0, 128, 128),
                    self.sprite_sheet.get_image(128, 0, 128, 128),
                    self.sprite_sheet.get_image(256, 0, 128, 128),
                ]
            ],
            "walk_right": [
                self.sprite_sheet.get_image(0, 0, 128, 128),
                self.sprite_sheet.get_image(128, 0, 128, 128),
                self.sprite_sheet.get_image(256, 0, 128, 128),
            ],
            "pick_up_right": [
                self.sprite_sheet.get_image(0, 128, 128, 128),
                self.sprite_sheet.get_image(128, 128, 128, 128),
            ],
            "pick_up_left": [
                pygame.transform.flip(img, True, False)
                for img in [
                    self.sprite_sheet.get_image(0, 128, 128, 128),
                    self.sprite_sheet.get_image(128, 128, 128, 128),
                ]
            ],
            "level_up": [
                self.sprite_sheet.get_image(0, 128 * 8, 128, 128),
                pygame.transform.flip(self.sprite_sheet.get_image(0, 128 * 8, 128, 128), True, False),
                self.sprite_sheet.get_image(128, 128 * 8, 128, 128),
                pygame.transform.flip(self.sprite_sheet.get_image(128, 128 * 8, 128, 128), True, False),
                self.sprite_sheet.get_image(256, 128 * 8, 128, 128),
                pygame.transform.flip(self.sprite_sheet.get_image(256, 128 * 8, 128, 128), True, False),
                self.sprite_sheet.get_image(128 * 3, 128 * 8, 128, 128),
                pygame.transform.flip(self.sprite_sheet.get_image(128 * 3, 128 * 8, 128, 128), True, False),
                self.sprite_sheet.get_image(128 * 4, 128 * 8, 128, 128),
                pygame.transform.flip(self.sprite_sheet.get_image(128 * 4, 128 * 8, 128, 128), True, False),
            ],
        }

    def draw(self, screen, ui):
        camera_x, camera_y = ui.camera_x, ui.camera_y
        current_image = self.animator.get_current_image()
        screen.blit(current_image, ((self.x - camera_x) * TILE_SIZE, (self.y - camera_y) * TILE_SIZE))

    def move(self, dx, dy, game_map, npcs, ui):
        speed = 0.2
        new_x = self.x + dx * speed
        new_y = self.y + dy * speed


        # 새로운 위치를 기반으로 픽셀 단위의 플레이어 히트박스 생성 (약간의 오프셋 및 크기 조절)
        self.hitbox = pygame.Rect(
            int(new_x * TILE_SIZE) + 5,
            int(new_y * TILE_SIZE) + 15,
            self.width + 20,
            self.height + 10
        )

        if self.check_collision_map(game_map):
            return
        
        if self.check_collision_npc(npcs):
            return
        
        if self.check_collision_trigger(game_map.triggers):
            pos = game_map.trigger_event(self.check_collision_trigger(game_map.triggers))
            self.set_player_position(pos[0], pos[1])
            return

        self.x = new_x
        self.y = new_y

    #플레이어 위치 변경
    def set_player_position(self, x, y):
        self.x = x
        self.y = y

    # 충돌 검사
    def check_collision_map(self,game_map):
         # 맵 충돌 검사: 히트박스 내의 타일 중 하나라도 충돌 타일이면 이동 취소
        if game_map.check_collision_rect(self.hitbox):
            return True
        return False
        
    def check_collision_npc(self, npcs):
        # NPC와의 충돌 검사 (히트박스 기반)
        for npc in npcs:
            # NPC 객체는 get_hitbox() 메서드를 통해 자신의 히트박스를 반환합니다.
            if npc.get_hitbox().colliderect(self.hitbox):
                return npc
        return False
    
    def check_collision_trigger(self, triggers):
        # 트리거와의 충돌 검사 (히트박스 기반)
        # 현재 맵의 충돌한 트리거를 반환
        for trigger in triggers:
            trigger_x = trigger.get("x")
            trigger_y = trigger.get("y")
            trigger_rect = pygame.Rect(trigger_x * TILE_SIZE, trigger_y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if trigger_rect.colliderect(self.hitbox):
                return trigger
        return False

    def load(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading player data from {filename}: {e}")
            return

        self.name = data.get("name", "Player")
        self.x = data.get("x", 0)
        self.y = data.get("y", 0)
        new_sprite_path = data.get("sprite", self.sprite_path)
        if new_sprite_path != self.sprite_path:
            self.sprite_path = new_sprite_path
            self.sprite_sheet = SpriteSheet(new_sprite_path)
        self.hp = data.get("hp", 100)
        self.level = data.get("level", 1)
        self.exp = data.get("exp", 0)
        self.money = data.get("money", 0)
        self.inventory = data.get("inventory", [])

        self.current_animation = "stand"
        self.animations = self._create_animations()
        self.animator = Animation(self.animations[self.current_animation], 100)

    def save(self, filename):
        data = {
            "name": self.name,
            "sprite": self.sprite_path,
            "x": self.x,
            "y": self.y,
            "hp": self.hp,
            "level": self.level,
            "exp": self.exp,
            "money": self.money,
            "inventory": self.inventory
        }
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving player data to {filename}: {e}")
