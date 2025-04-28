import pygame
from modules.player import Player
from modules.game_map import GameMap
from modules.save_load import SaveLoad
from modules.display import Display

# 초기화
pygame.init()

# 화면 크기 설정
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2D RPG - 저장 및 로드")

# 색상 정의
WHITE = (255, 255, 255)

# 게임 상태
running = True
clock = pygame.time.Clock()

# 객체 생성
player = Player(x=100, y=100, width=50, height=50, speed=5)  # Player 객체 생성
game_map = GameMap()  # GameMap 객체 생성
display = Display(screen, game_map)  # Display 객체 생성
SaveLoad.load_game(player)  # 저장된 데이터 로드

player.set_start_pos(game_map)  # 시작 위치 설정

# 게임 루프
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 키 입력 처리
    keys = pygame.key.get_pressed()
    player.move(keys, game_map)  # 플레이어 이동
    player.harvest(keys, game_map)  # 농작물 수확

    # 화면 갱신
    screen.fill(WHITE)

    display.update_camera(player)  # 카메라 업데이트
    display.draw(player)  # 맵, 플레이어, 농작물 등 그리기

    # UI 표시 (체력, 경험치, 돈, 인벤토리 등)
    display.draw_ui(player)
    display.draw_inventory(player)
  
    # 맵 업데이트 (농작물 생성, 맵 전환 등)
    game_map.update_crop(30)

    pygame.display.flip()
    clock.tick(30)  # 초당 프레임 수

# 게임 종료 시 자동 저장
SaveLoad.save_game(player)
pygame.quit()
