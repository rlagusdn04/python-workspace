import json
import pygame

TILE_SIZE = 32  

class SpriteSheet:
    def __init__(self, file_path, scale_factor=2):
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

class Map:
    current_map = None  # 현재 활성화된 맵

    def __init__(self, name=None, map_type=None, width=None, height=None,
                 tiles=None, objects=None, triggers=None, properties=None):
        if name is None:
            self.maps = {}  # 매니저 역할일 경우 전체 맵 데이터 관리
        else:
            self.name = name
            self.map_type = map_type
            self.tiles = tiles or []
            self.objects = objects or []
            self.triggers = triggers or []
            self.properties = properties or {}

            # 타일 배열이 있다면 실제 크기를 기준으로 width, height를 재설정합니다.
            if self.tiles:
                actual_height = len(self.tiles)
                actual_width = max(len(row) for row in self.tiles) if actual_height > 0 else 0

                if width is None or width != actual_width:
                    print(f"[Warning] 제공된 width({width})와 실제 타일 너비({actual_width})가 일치하지 않습니다. 실제 값({actual_width})을 사용합니다.")
                    self.width = actual_width
                else:
                    self.width = width

                if height is None or height != actual_height:
                    print(f"[Warning] 제공된 height({height})와 실제 타일 높이({actual_height})가 일치하지 않습니다. 실제 값({actual_height})을 사용합니다.")
                    self.height = actual_height
                else:
                    self.height = height
            else:
                # 타일 배열이 없으면 제공된 값 또는 기본값(0)을 사용
                self.width = width if width is not None else 0
                self.height = height if height is not None else 0

            self.collision_tiles = [1,2,3,4,5,6,8,9,10,11,12,13,14,15,16,17,18,19,20]  # 충돌 타일 ID
            self.sprite_sheet = SpriteSheet("assets/tiles.png")
            self.object_mapping = {
                "house": (TILE_SIZE + 64, TILE_SIZE - 32, TILE_SIZE + 45, TILE_SIZE + 64)
            }

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)

        self.maps = {}
        for map_data in data.get("maps", []):
            tiles = map_data.get("tiles")
            # 타일 배열이 있을 경우 실제 크기 계산
            actual_height = len(tiles) if tiles else 0
            actual_width = max(len(row) for row in tiles) if tiles else 0

            provided_width = map_data.get("width", actual_width)
            provided_height = map_data.get("height", actual_height)

            if provided_width != actual_width:
                print(f"[Warning] 맵 '{map_data.get('name')}'의 제공된 width({provided_width})와 실제 너비({actual_width})가 다릅니다.")
            if provided_height != actual_height:
                print(f"[Warning] 맵 '{map_data.get('name')}'의 제공된 height({provided_height})와 실제 높이({actual_height})가 다릅니다.")

            self.maps[map_data.get("name")] = Map(
                name=map_data.get("name"),
                map_type=map_data.get("type"),
                width=provided_width,
                height=provided_height,
                tiles=tiles,
                objects=map_data.get("objects", []),
                triggers=map_data.get("triggers", []),
                properties=map_data.get("properties", {})
            )

        current_map_name = data.get("current_map")
        if current_map_name in self.maps:
            Map.set_current_map(self.maps[current_map_name])
        elif self.maps:
            Map.set_current_map(list(self.maps.values())[0])

    @classmethod
    def set_current_map(cls, map_obj):
        cls.current_map = map_obj

    @classmethod
    def get_current_map(cls):
        return cls.current_map

    @classmethod
    def get_current_map_name(cls):
        if cls.current_map:
            return cls.current_map.name
        return None

    @classmethod
    def draw_current_map(cls, screen, ui):
        if cls.current_map:
            cls.current_map.draw(screen, ui)


    def change_map(self, map_name, start_position=None):
        self.get_current_map_name = map_name
        # 맵 변경 시 현재 맵을 변경합니다.
        # 맵을 로딩
        self.load("data/map.json")
        # 맵 이름이 존재하는지 확인
        if map_name in self.maps:
            Map.set_current_map(self.maps[map_name])
            print("맵 변경:", map_name)

            # 플레이어 위치를 start_position으로 이동
        else:
            print(f"[Error] 맵 '{map_name}'을 찾을 수 없습니다.")

    def draw(self, screen, ui):
        camera_x, camera_y = ui.camera_x, ui.camera_y
        
        # 타일 그리기
        for y, row in enumerate(self.tiles):
            for x, tile_id in enumerate(row):
                tile_image = self.get_tile_image(tile_id)
                # 타일 이미지와 화면 타일 크기 차이에 따른 위치 보정
                screen.blit(tile_image, ((x - camera_x) * TILE_SIZE, (y - camera_y) * TILE_SIZE))
        
        # 객체 그리기 (예: 하우스, 아이템, NPC 등)
        for obj in self.objects:
            obj_type = obj.get("type")
            obj_x = obj.get("x")
            obj_y = obj.get("y")
            
            if obj_type == "house":
                if "house" in self.object_mapping:
                    sx, sy, sw, sh = self.object_mapping["house"]
                    house_image = self.sprite_sheet.get_image(sx, sy, sw, sh)
                    screen.blit(house_image, ((obj_x - camera_x) * TILE_SIZE, (obj_y - camera_y) * TILE_SIZE))
            else:
                color = (0, 0, 255) if obj_type == "item" else (255, 0, 0)
                rect = pygame.Rect((obj_x - camera_x) * TILE_SIZE, (obj_y - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(screen, color, rect)

        # 트리거 영역 그리기 (빨간 테두리)
        for trigger in self.triggers:
            trigger_x = trigger.get("x")
            trigger_y = trigger.get("y")
            rect = pygame.Rect((trigger_x - camera_x) * TILE_SIZE, (trigger_y - camera_y) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, (255, 0, 0), rect, 2)

    def is_colliding(self, x, y):
        tile_id = self.get_tile_id(x, y)
        return tile_id in self.collision_tiles

    def get_tile_id(self, x, y):
        # 실제 타일 배열 크기를 기준으로 안전하게 인덱싱
        if 0 <= y < len(self.tiles) and 0 <= x < len(self.tiles[y]):
            return self.tiles[y][x]
        return None

    def get_tile_image(self, tile_id):
        """
        tile_id에 따라 스프라이트 시트에서 해당 타일 이미지를 추출합니다.
        예시: tile_id 0은 (0, 0)에서 타일을 가져옵니다.
        """
        tile_mapping = {
            0: (0, 0, 16, 16),          # 풀
            1: (32, 32, 16, 16),        #물타일1
            2: (16, 16, 16, 16),
            3: (0, 16, 16, 16),
            4: (16, 32, 16, 16),
            5: (0, 32, 16, 16),         # 물타일5
            6: (16*4, 16*9, 16, 16),   #벽타일1
            7: (16*5, 16*9, 16, 16),   #이동 가능 타일
            8: (16*6, 16*9, 16, 16),
            9: (16*4, 16*10, 16, 16), 
            10: (16*5, 16*10, 16, 16),
            11: (16*6, 16*10, 16, 16),
            12: (16*4, 16*11, 16, 16),
            13: (16*5, 16*11, 16, 16),
            14: (16*6, 16*11, 16, 16),
            15: (16*4, 16*12, 16, 16),
            16: (16*5, 16*12, 16, 16),
            17: (16*6, 16*12, 16, 16),
            18: (16*4, 16*13, 16, 16),
            19: (16*5, 16*13, 16, 16),
            20: (16*6, 16*13, 16, 16), 
            21: (16*4, 16*14, 16, 16),
            22: (16*5, 16*14, 16, 16),
            23: (16*6, 16*14, 16, 16), #벽타일20
            24: (16*0, 16*11, 16, 16), #풀 모서리 1
            25: (16*1, 16*11, 16, 16), #풀 모서리 2
            26: (16*2, 16*11, 16, 16), #풀 모서리 3
        }
        if tile_id in tile_mapping:
            x, y, width, height = tile_mapping[tile_id]
            return self.sprite_sheet.get_image(x, y, width, height)
        else:
            default_image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            default_image.fill((150, 150, 150))
            return default_image

    def check_collision_rect(self, rect):
        left_tile = rect.left // TILE_SIZE
        right_tile = (rect.right - 1) // TILE_SIZE
        top_tile = rect.top // TILE_SIZE
        bottom_tile = (rect.bottom - 1) // TILE_SIZE
        for y in range(top_tile, bottom_tile + 1):
            for x in range(left_tile, right_tile + 1):
                tile_id = self.get_tile_id(x, y)
                if tile_id in self.collision_tiles:
                    return True
        return False
    
    #트리거 영역 관리

    #트리거 이벤트 처리
    def trigger_event(self, trigger):
        event_type = trigger.get("event")
        if event_type == "change_map":
            map_name = trigger.get("target_map")
            start_position = trigger.get("start_pos")
            self.change_map(map_name, start_position)
            return start_position # 플레이어 위치 변경을 위해 start_position 반환
        else:
            print(f"[Warning] 알 수 없는 트리거 이벤트: {event_type}")
        
