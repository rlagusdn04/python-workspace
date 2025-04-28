import pygame

class Player:
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.health = 100
        self.level = 1
        self.experience = 0
        self.money = 0
        self.inventory = []

    def move(self, keys, game_map):
        """플레이어 이동 및 맵 전환 처리"""
        new_x, new_y = self.x, self.y

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            new_y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_y += self.speed
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_x += self.speed

        # 플레이어의 임시 사각형 생성
        player_rect = pygame.Rect(new_x, new_y, self.width, self.height)

        # 맵 경계 및 충돌 확인
        if game_map.is_within_bounds(player_rect) and not game_map.check_collision(player_rect):
            self.x, self.y = new_x, new_y

        # 맵 전환 확인
        next_map = game_map.check_transition_zone(player_rect)
        if next_map is not None:
            # 맵 전환
            game_map.change_map(next_map)
            start_pos = game_map.get_start_pos(next_map)  # 새 맵 시작 위치
            if start_pos is not None:
                self.x, self.y = start_pos  # 새 맵 시작 위치로 이동

        # 농작물 수확 처리
        self.harvest(keys, game_map)

    def set_start_pos(self, game_map):
        """시작 위치 설정"""
        start_pos = game_map.get_start_pos(game_map.get_current_map())  # 맵 시작 위치
        if start_pos is not None:
            self.x, self.y = start_pos  # 맵 시작 위치로 이동

    def draw(self, screen):
        """플레이어를 실제 좌표를 기준으로 화면에 그리기"""
        pygame.draw.rect(screen, (0, 0, 255), (self.x, self.y, self.width, self.height))

    def add_experience(self, exp):
        """경험치 추가"""
        self.experience += exp

    def add_money(self, money):
        """소지금 추가"""
        self.money += money

    def add_item(self, item_name, quantity=1):
        """인벤토리에 아이템 추가"""
        for item in self.inventory:
            if item["name"] == item_name:
                item["quantity"] += quantity
                return
        self.inventory.append({"name": item_name, "quantity": quantity})

    def harvest(self, keys, game_map):
        """농작물 수확"""
        current_crops = game_map.get_current_crops()
        for crop in current_crops:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(crop) and keys[pygame.K_SPACE]:
                current_crops.remove(crop)
                self.add_experience(10)
                self.add_item("apple")
                game_map.reset_timer("crop_spawn")
                break
