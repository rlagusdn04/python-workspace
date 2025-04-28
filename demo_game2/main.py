import pygame
from modules.player import Player, SpriteSheet
from modules.map import Map 
from modules.camera import Camera
from modules.save import SaveLoad
from modules.map import SeedManager
from modules.player import CollisionManager
from modules.npc import NPC, NPCManager  # NPCManager 추가

# Main Function
def main():
    pygame.init()

    screen_width = 800
    screen_height = 600

    game_time = 0

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("게임 타이틀")

    clock = pygame.time.Clock()
    running = True

    # 스프라이트 시트 로드
    sprite_sheet = SpriteSheet("data/ditto.png")

    # 객체 생성
    player = Player(100, 100, 40, 5, sprite_sheet)
    game_map = Map()
    npc_manager = NPCManager()  # NPCManager 인스턴스화
    camera = Camera(screen_width, screen_height, game_map, screen)
    seed_manager = SeedManager(game_map)
    collision_manager = CollisionManager(game_map)

    # 저장된 데이터 로드
    SaveLoad.load_game(player, game_map, npc_manager)

    while running:
        dt = clock.tick(60)  # 프레임별 경과 시간 (밀리초)
        game_time += dt     # 게임 전체의 누적 시간을 업데이트

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:  # 'E' 키를 눌러 작물 수확 및 상호작용
                    player.plant(event, game_map, game_time) # 작물 심기
                    game_map.harvest_crop(player, player.x, player.y)
                    #player.use_hand_item(event,game_map)
                    player.use_item(event)
            camera.toggle_inventory(event)  # 인벤토리 토글
            player.interact_with_npcs(event, npc_manager,camera)


        # 키보드와 마우스 입력 처리
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()  # 마우스 위치
        mouse_pressed = pygame.mouse.get_pressed()  # 마우스 버튼 상태

        player.move(keys, game_map, collision_manager, dt, npc_manager, camera, event)  # dt를 전달

        camera.update(player)
        npc_manager.update(game_map)
        game_map.update_crop(game_time)

        screen.fill((0, 0, 0))
        game_map.draw(screen, camera, seed_manager)
        player.draw(screen, camera)

        npc_manager.draw(screen, camera)

        # UI 표시 (체력, 경험치, 돈, 인벤토리 등)
        camera.draw_ui(player)
        camera.draw_inventory(player)

        pygame.display.flip()

    # 게임 종료 시 자동 저장
    SaveLoad.save_game(player, game_map, npc_manager)
    game_map.save_maps()
    pygame.quit()

if __name__ == "__main__":
    main()

