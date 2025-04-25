import pygame
from modules.map import Map
from modules.npc import NPCManager
from modules.player import Player, TILE_SIZE
from modules.ui import UI
from modules.config import Config, ParallaxBackground, Music

screen_width = 800
screen_height = 600

def main():
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("게임 타이틀")

    clock = pygame.time.Clock()

    # 맵, NPC, 플레이어, UI 객체 생성 및 로드
    map_manager = Map()
    map_manager.load("data/map.json")
    current_map = Map.get_current_map()
    print("현재 맵:", Map.get_current_map_name())

    npc_manager = NPCManager()
    npc_manager.load("data/npc.json")

    player = Player()
    player.load("data/player.json")

    ui = UI(player)

    # 환경설정 객체 생성
    config = Config()
    config.load("data/config.json")
    parallax_bg = ParallaxBackground("assets/layers", scale=1.0, min_factor=0.3, max_factor=1.0)
    music = Music("data/music/")

    def SceneManager():
        # 튜토리얼 진행
        if config.tutorial_enabled and player.name == "Player":
            config.on_field = False
            music.play(3)
            
            # 닉네임 입력 UI: 엔터를 눌러 이름이 입력되면 함수가 반환됨
            ui.name_input(screen, parallax_bg)
            
            # 이름 입력 완료 후 튜토리얼 종료 처리
            config.tutorial_enabled = False
            config.on_field_enabled = True
            music.stop()
            
            pygame.display.flip()

        # 온 필드 상태
        elif config.on_field_enabled:
            if not music.is_playing():
                music.play(1)
            Map.draw_current_map(screen, ui)
            npcs_on_map = npc_manager.get_npcs(current_map)
            for npc in npcs_on_map:
                npc.draw(screen, ui)
            player.draw(screen, ui)
            ui.draw_ui(screen)
            pygame.display.flip()

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    npcs_on_map = npc_manager.get_npcs(current_map)
                    npc_collision = player.check_collision_npc(npcs_on_map)
                    if npc_collision:
                        npc_manager.interact(npc_collision, ui)

        # 키 입력에 따른 플레이어 이동 (WASD)
        keys = pygame.key.get_pressed()
        npcs_on_map = npc_manager.get_npcs(current_map)
        
        if keys[pygame.K_w]:
            player.move(0, -1, current_map, npcs_on_map, ui)
        elif keys[pygame.K_s]:
            player.move(0, 1, current_map, npcs_on_map, ui)
        elif keys[pygame.K_a]:
            player.move(-1, 0, current_map, npcs_on_map, ui)
        elif keys[pygame.K_d]:
            player.move(1, 0, current_map, npcs_on_map, ui)

        player.animator.update(dt)

        # 카메라 업데이트 (플레이어 중심으로)
        ui.update(player)

        # 화면 초기화
        screen.fill((0, 0, 0))

        # 씬 진행
        SceneManager()

    player.save("data/player.json")
    pygame.quit()

if __name__ == "__main__":
    main()
