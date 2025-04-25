import pygame
import os

TILE_SIZE = 32

class UI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont("Arial", 20)
        self.width = 800         # 화면 가로 크기 (픽셀)
        self.height = 600        # 화면 세로 크기 (픽셀)
        # camera_x, camera_y는 타일 단위 좌표로 사용
        self.camera_x = 0        
        self.camera_y = 0        

    def draw_ui(self, screen):
        # 상태창 UI: 플레이어 이름과 HP 표시
        display_text = f"Player: {self.player.name} HP: {self.player.hp}"
        screen.blit(self.font.render(display_text, True, (255, 255, 255)), (10, 10))
        
        # 상호작용 안내 UI: 'E'키 누르라는 메시지
        update_text = "Press 'E' to interact"
        screen.blit(self.font.render(update_text, True, (255, 255, 255)), (10, 40))

    def update(self, player):
        # 화면의 픽셀 단위를 타일 단위로 변환 (예: 800px -> 25타일, 600px -> 18.75타일)
        screen_tiles_x = self.width / TILE_SIZE
        screen_tiles_y = self.height / TILE_SIZE

        # 플레이어를 화면 중앙에 두기 위한 카메라 목표 좌표 계산 (타일 단위)
        target_x = player.x - screen_tiles_x / 2
        target_y = player.y - screen_tiles_y / 2

        # 즉시 목표 좌표로 이동 (부드러운 이동을 원하면 lerp_factor를 0과 1 사이로 조정)
        lerp_factor = 1  # 1이면 즉시 이동
        self.camera_x += (target_x - self.camera_x) * lerp_factor
        self.camera_y += (target_y - self.camera_y) * lerp_factor

    def show_dialogue(self, dialogue):
        print(dialogue)
        pass
        
    def inventory(self, screen):
        pass

    def hand_ui(self, screen):
        pass

    def dialogue(self, screen):
        pass

    def name_input(self, screen, parallax_bg):
        input_active = True
        input_text = ""
        focused = False  # 입력창 포커스 여부
        clock = pygame.time.Clock()
        
        # 색상 설정
        box_color = (50, 50, 50, 180)      # 입력창 배경 (투명도 180)
        border_color = (200, 200, 200)      # 테두리 색상
        text_color = (255, 255, 255)        # 입력 텍스트 색상
        placeholder_color = (150, 150, 150) # 플레이스홀더 텍스트 색상
        
        while input_active:
            # 입력창 위치와 크기 (화면 중앙)
            box_width, box_height = 400, 50
            box_x = (self.width - box_width) // 2
            box_y = (self.height - box_height) // 1.5

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # 입력창 내부 클릭 시 포커스 활성화
                    if box_x <= event.pos[0] <= box_x + box_width and box_y <= event.pos[1] <= box_y + box_height:
                        if not focused:
                            input_text = ""  # 최초 클릭 시 플레이스홀더 삭제
                        focused = True
                    else:
                        focused = False  # 입력창 외부 클릭 시 포커스 해제
                if event.type == pygame.KEYDOWN and focused:
                    if event.key == pygame.K_RETURN:
                        self.player.name = input_text.strip() if input_text.strip() != "" else "Player"
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode

            # 배경 레이어 업데이트 및 그리기
            parallax_bg.update(clock.get_time())
            parallax_bg.draw(screen)
            
            # 투명 배경을 가진 입력창 surface 생성
            input_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
            input_surface.fill(box_color)
            screen.blit(input_surface, (box_x, box_y))
            pygame.draw.rect(screen, border_color, (box_x, box_y, box_width, box_height), 2)
            
            # 블링크 커서: 현재 시간에 따라 깜박임 효과 (500ms 주기)
            current_time = pygame.time.get_ticks()
            blink = (current_time // 500) % 2 == 0
            
            # 입력 상태에 따라 표시할 텍스트 결정
            if focused:
                display_text = input_text + ("|" if blink else "")
            else:
                display_text = input_text if input_text != "" else "Enter your name"
            
            # 플레이스홀더 색상 적용: 포커스가 없고 아직 입력이 없을 때
            render_color = text_color if focused or input_text != "" else placeholder_color
            text_surface = self.font.render(display_text, True, render_color)
            screen.blit(text_surface, (box_x + 10, box_y + 10))

            pygame.display.flip()
            clock.tick(30)

