import pygame
import time
import json
import os

class Config:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.map_manager = None
        self.current_map = None
        self.npc_manager = None
        self.tutorial = False
        self.player = None
        self.parallax_bg = None
        self.ui = None
        self.running = True

    #config.json 파일 로드
    def load(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading player data from {filename}: {e}")
            return

        tutorial_data = data.get("tutorial", {})
        self.tutorial_enabled = tutorial_data.get("enabled", False)
        self.tutorial_steps = tutorial_data.get("steps", [])
        
        on_field_data = data.get("on_field", {})
        self.on_field_enabled = on_field_data.get("enabled", True)

class ParallaxBackground:
    """
    다양한 PNG 레이어들을 사용하여 패럴랙스 효과를 구현하는 클래스입니다.
    첫 번째 PNG는 고정되고, 나머지 PNG들은 지정된 계수에 따라 시간에 맞춰 자연스럽게 움직입니다.
    스크린을 꽉 채우도록 각 레이어 이미지를 스케일링합니다.
    """
    def __init__(self, folder_path, scale=1.0, min_factor=0.3, max_factor=1.0, screen_size=(800, 600)):
        self.screen_size = screen_size
        self.layers = []
        # 숨김 파일(예: "._"로 시작하는 파일)을 제외하고 PNG 파일만 불러옵니다.
        file_list = sorted([
            f for f in os.listdir(folder_path)
            if f.lower().endswith('.png') and not f.startswith("._")
        ])
        for file in file_list:
            image_path = os.path.join(folder_path, file)
            image = pygame.image.load(image_path)
            # PNG가 투명 정보(alpha)를 가지고 있으면 convert_alpha() 사용
            if image.get_alpha() is not None:
                image = image.convert_alpha()
            else:
                image = image.convert()
            # scale 인자가 1.0이 아닐 경우, 우선 스케일 적용
            if scale != 1.0:
                width, height = image.get_size()
                image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
            # 스크린을 꽉 채우도록 이미지 스케일링 (해상도에 맞춤)
            image = pygame.transform.scale(image, self.screen_size)
            self.layers.append(image)
        
        # 패럴랙스 계수 설정: 첫 번째 레이어는 고정(0), 나머지는 선형 보간으로 이동 계수 지정
        self.factors = []
        total = len(self.layers)
        if total > 0:
            self.factors.append(0)  # 첫 번째 레이어 고정
            if total > 1:
                for i in range(1, total):
                    if total > 2:
                        factor = min_factor + (max_factor - min_factor) * ((i - 1) / (total - 2))
                    else:
                        factor = min_factor
                    self.factors.append(factor)
        
        self.offset = 0  # 전체 이동 오프셋

    def update(self, dt):
        # 시간(dt, 밀리초)에 따라 오프셋을 업데이트
        speed = 50  # 초당 50 픽셀 이동 (필요에 따라 조정)
        self.offset += speed * (dt / 1000.0)

    def draw(self, screen):
        for image, factor in zip(self.layers, self.factors):
            # 각 레이어의 이동 오프셋은 전체 오프셋에 패럴랙스 계수를 곱한 값
            layer_offset = self.offset * factor
            # 화면 폭을 기준으로 모듈로 연산하여 무한 반복 효과 구현
            offset_x = layer_offset % self.screen_size[0]
            screen.blit(image, (-offset_x, 0))
            # 이미지가 화면을 채우지 못하는 경우 오른쪽에 추가 이미지 그리기
            if offset_x > 0:
                screen.blit(image, (self.screen_size[0] - offset_x, 0))

        


class Music:
    def __init__(self, download_path="data/music/"):
        self.volume = 0.5
        self.download_path = download_path
        # 음악 번호와 파일 이름을 매핑하는 사전
        self.music_files = {
            1: "watercity.mp3", # 배경 1
            2: "Heart.mp3", # 엔딩
            3: "Triste.mp3", # 튜토
            4: "뚱땅뚱땅.mp3", # 
            5: "La nuit.mp3", # 호수
            6: "Time to Start Another Day.mp3", # 주점
            # 필요한 만큼 추가
        }

    def play(self, music_num):

        filename = self.music_files.get(music_num)
        if not filename:
            print(f"음악 번호 {music_num}에 해당하는 파일이 없습니다.")
            return

        file_path = os.path.join(self.download_path, filename)
        time.sleep(1)  # 음악 재생 전 잠시 대기
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.set_volume(self.volume)
            # 루프 재생을 원하면 -1을, 그렇지 않으면 기본값 0을 사용합니다.
            pygame.mixer.music.play(-1)
        except Exception as e:
            print(f"음악 재생 중 오류 발생: {e}")
    
    def is_playing(self):
        return pygame.mixer.music.get_busy()

    def stop(self):
        pygame.mixer.music.stop()
