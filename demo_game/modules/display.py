import pygame

class Display:
    def __init__(self, screen, game_map):
        self.screen = screen
        self.font = pygame.font.SysFont(None, 24)
        self.color = (0, 0, 0)

        # 카메라 관련 설정
        self.camera_x = 0
        self.camera_y = 0
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.game_map = game_map

        # 슬랙 영역 크기
        self.SLACK_WIDTH = self.screen_width * 0.2  # 화면의 20%
        self.SLACK_HEIGHT = self.screen_height * 0.2  


    def update_camera(self, player):
        """카메라가 플레이어를 부드럽게 따라가며 맵 경계를 벗어나지 않도록 제한"""
        # 플레이어를 기준으로 카메라 목표 위치 계산
        target_x = player.x - self.screen_width // 2
        target_y = player.y - self.screen_height // 2

        # 맵 크기 가져오기
        map_width, map_height = self.game_map.get_current_map()["size"]

        # 카메라 이동 선형 보간 (lerp)
        lerp_factor = 0.2  # 보간 비율 (0.0 ~ 1.0, 높을수록 빠르게 따라감)
        self.camera_x += (target_x - self.camera_x) * lerp_factor
        self.camera_y += (target_y - self.camera_y) * lerp_factor

        # 카메라 속도 제한 (플레이어 이동이 급격해도 카메라가 따라잡을 수 있도록)
        max_speed = 25  # 카메라 최대 이동 속도
        dx = target_x - self.camera_x
        dy = target_y - self.camera_y
        if abs(dx) > max_speed:
            self.camera_x += max_speed if dx > 0 else -max_speed
        if abs(dy) > max_speed:
            self.camera_y += max_speed if dy > 0 else -max_speed

        # 카메라를 맵 경계 내로 제한
        self.camera_x = max(0, min(self.camera_x, map_width - self.screen_width))
        self.camera_y = max(0, min(self.camera_y, map_height - self.screen_height))



    def draw(self, player):
        """맵과 객체를 카메라 오프셋에 맞춰 그리기"""
        offset_x = self.camera_x
        offset_y = self.camera_y

        self.game_map.draw_ob(self.screen, offset_x, offset_y)
        self.game_map.draw_crop(self.screen, offset_x, offset_y)
        self.game_map.draw_transition_zone(self.screen, offset_x, offset_y)

        # 플레이어 그리기 (오프셋 제외)
        player.draw(self.screen)

    

    def draw_ui(self, player):
        health_text = self.font.render(f"Health: {player.health}", True, (0, 0, 0))
        exp_text = self.font.render(f"Experience: {player.experience}", True, (0, 0, 0))
        money_text = self.font.render(f"Money: {player.money}", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(exp_text, (10, 30))
        self.screen.blit(money_text, (10, 50))

    def draw_inventory(self, player):
        """인벤토리 표시"""
        if pygame.key.get_pressed()[pygame.K_i]:
            inventory_text = self.font.render(f"Inventory: {player.inventory}", True, self.color)
            self.screen.blit(inventory_text, (10, 70))

