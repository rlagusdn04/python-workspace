import pygame
import random

class GameMap:
    def __init__(self):
        # 맵 데이터 초기화
        self.current_map_index = 0
        self.maps = [
            {
                "name": "1",
                "obstacles": [pygame.Rect(300, 200, 100, 100)],
                "crops": [],
                "bounds":(800, 600),  # 맵 경계
                "size": (800, 600),  # 맵 크기 (width, height)
                "transition_zones": [  # 맵 전환 영역
                    {"zone": pygame.Rect(750, 550, 50, 50), "next_map": 1},  # 1번 맵으로 이동
                    {"zone": pygame.Rect(400, 550, 50, 50), "next_map": 2} # 2번 맵으로 이동
                ]
            },
            {
                "name": "2",
                "obstacles": [pygame.Rect(600, 100, 150, 50)],
                "crops": [],
                "bounds": (800, 600),  # 맵 경계
                "size": (1200, 800),  # 맵 크기 (width, height)
                "transition_zones": [
                    {"zone": pygame.Rect(0, 0, 50, 50), "next_map": 0}  # 0번번 맵으로 이동
                ]
            },
            {
                "name": "3",
                "obstacles": [pygame.Rect(200, 200, 150, 50), pygame.Rect(500, 400, 100, 100)],
                "crops": [],
                "bounds": (800, 600),  # 맵 경계
                "size": (1200, 800),  # 맵 크기 (width, height)
                "transition_zones": [
                    {"zone": pygame.Rect(0, 0, 400, 50), "next_map": 0}  # 0번 맵으로 이동
                ]
            }
        ]

        # 농작물 생성 시간 관련 변수
        self.timers = {
            "crop_spawn": 0,  # 농작물 생성 타이머
        }
        self.crop_spawn_time = 2000  # 10초마다 농작물 생성

    def change_map(self, next_map_index):
        """맵 전환 (지정된 맵으로 이동)"""
        self.current_map_index = next_map_index

    def get_current_map(self):
        """현재 맵 데이터 반환"""
        return self.maps[self.current_map_index]

    def check_transition_zone(self, player_rect):
        """플레이어가 맵 전환 트리거에 도달했는지 확인"""
        for zone in self.get_current_map()["transition_zones"]:
            if player_rect.colliderect(zone["zone"]):
                return zone["next_map"]  # 전환할 맵의 인덱스 반환
        return None

    def get_start_pos(self, map_index):
        """플레이어의 시작 위치 반환"""
        if map_index == 0:
            return (750, 500)  # 맵 1의 시작 위치
        elif map_index == 1:
            return (50, 50)  # 맵 2의 시작 위치
        return (50, 50)  # 기본값 (잘못된 인덱스 처리)

    def get_current_crops(self):
        """현재 맵의 농작물 반환"""
        return self.get_current_map()["crops"]

    def draw_ob(self, screen, offset_x, offset_y):
        """카메라 오프셋을 반영하여 장애물 그리기"""
        for obstacle in self.get_current_map()["obstacles"]:
            draw_x = obstacle.x - offset_x
            draw_y = obstacle.y - offset_y
            pygame.draw.rect(screen, (255, 0, 0), (draw_x, draw_y, obstacle.width, obstacle.height))

    def draw_crop(self, screen, offset_x, offset_y):
        """카메라 오프셋을 반영하여 농작물 그리기"""
        for crop in self.get_current_crops():
            draw_x = crop.x - offset_x
            draw_y = crop.y - offset_y
            pygame.draw.rect(screen, (0, 255, 0), (draw_x, draw_y, crop.width, crop.height))

    def draw_transition_zone(self, screen, offset_x, offset_y):
        """카메라 오프셋을 반영하여 전환 구역 그리기"""
        for zone in self.get_current_map()["transition_zones"]:
            draw_x = zone["zone"].x - offset_x
            draw_y = zone["zone"].y - offset_y
            pygame.draw.rect(screen, (0, 0, 255), (draw_x, draw_y, zone["zone"].width, zone["zone"].height))

    def update_timers(self, dt):
        """타이머들 업데이트"""
        for timer_name in self.timers:
            self.timers[timer_name] += dt

    def reset_timer(self, timer_name):
        """지정된 타이머 초기화"""
        if timer_name in self.timers:
            self.timers[timer_name] = 0

    def update_crop(self, dt):
        """농작물 생성 관리"""
        self.update_timers(dt)  # 타이머 업데이트

        if len(self.get_current_crops()) < 3 and self.current_map_index == 0:  # 맵 1에서만 생성
            if self.timers["crop_spawn"] >= self.crop_spawn_time:
                self.spawn_crop()
                self.reset_timer("crop_spawn")  # 타이머 초기화

    def spawn_crop(self):
        """농작물을 랜덤 위치에 생성"""
        new_crop = pygame.Rect(random.randint(0, 700), random.randint(0, 500), 50, 50)
        self.get_current_crops().append(new_crop)

    def check_collision(self, player_rect):
        """플레이어와 장애물 간 충돌 확인"""
        for obstacle in self.get_current_map()["obstacles"]:
            if (player_rect.colliderect(obstacle) and self.is_within_bounds(player_rect)
        ):
                return True
        return False

    def check_and_change_map(self, player_rect):
        """맵 전환 확인 및 전환 처리"""
        for zone in self.get_current_map()["transition_zones"]:
            if player_rect.colliderect(zone["zone"]):
                next_map = zone["next_map"]
                self.change_map(next_map)
                return self.get_start_pos(next_map)  # 새 맵의 시작 위치 반환
        return None

    def is_within_bounds(self, player_rect):
        """플레이어가 맵 경계 내에 있는지 확인"""
        map_width, map_height = self.get_current_map()["bounds"]
        return (
            0 <= player_rect.left and
            player_rect.right <= map_width and
            0 <= player_rect.top and
            player_rect.bottom <= map_height
        )