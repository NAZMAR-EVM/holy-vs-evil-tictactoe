import pygame
import sys
import random
import os
import time

# ==== ПАРАМЕТРЫ ====
FIELD_SIZE = 5  # поле 5x5
WIN_LEN = 4     # победа по 4 в ряд
WIDTH, HEIGHT = 800, 850
CELL_SIZE = WIDTH // FIELD_SIZE
BG_COLOR = (30, 0, 0)
LINE_COLOR = (170, 0, 0)
X_COLOR = (220, 0, 0)
O_COLOR = (255, 40, 40)
BTN_COLOR = (80, 0, 0)
BTN_HOVER = (160, 0, 0)
WHITE = (255, 255, 255)
STATS_FILE = "tictactoe_stats.txt"


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Крестики-нолики: Кровавый Культ 5x5")
icon = pygame.Surface((32, 32))
icon.fill((90, 0, 0))
pygame.display.set_icon(icon)
clock = pygame.time.Clock()
font = pygame.font.SysFont("dejavusansmono", 44, bold=True)
btn_font = pygame.font.SysFont("dejavusansmono", 32, bold=True)
stat_font = pygame.font.SysFont("dejavusansmono",16, bold=True)
msg_font = pygame.font.SysFont("dejavusansmono", 38, bold=True)
PENTAGRAM_IMG = pygame.image.load("pentagram_icon.png").convert_alpha()
CROSS_IMG = pygame.image.load("white_cross_icon.png").convert_alpha()


def load_bg_img():
    try:
        return pygame.image.load("pentagram.png").convert()
    except Exception as e:
        print("Не удалось загрузить pentagram.png:", e)
        return None

BG_IMG = load_bg_img()

def draw_background():
    if BG_IMG:
        img = pygame.transform.scale(BG_IMG, (WIDTH, HEIGHT))
        screen.blit(img, (0, 0))
    else:
        screen.fill(BG_COLOR)

class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self, mouse):
        color = BTN_HOVER if self.rect.collidepoint(mouse) else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=13)
        pygame.draw.rect(screen, LINE_COLOR, self.rect, 3, border_radius=13)
        txt = btn_font.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.x + (self.rect.width - txt.get_width()) // 2,
                          self.rect.y + (self.rect.height - txt.get_height()) // 2))

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(e.pos):
            self.callback()

def draw_grid():
    for i in range(1, FIELD_SIZE):
        pygame.draw.line(screen, LINE_COLOR, (i * CELL_SIZE, 0), (i * CELL_SIZE, CELL_SIZE * FIELD_SIZE), 8)
        pygame.draw.line(screen, LINE_COLOR, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 8)

def draw_pentagram(center, cell_size):
    img = pygame.transform.smoothscale(PENTAGRAM_IMG, (int(cell_size * 0.8), int(cell_size * 0.8)))
    rect = img.get_rect(center=center)
    screen.blit(img, rect)

def draw_cross(center, cell_size):
    img = pygame.transform.smoothscale(CROSS_IMG, (int(cell_size * 0.8), int(cell_size * 0.8)))
    rect = img.get_rect(center=center)
    screen.blit(img, rect)


def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            f.write(f"{stats['X']},{stats['O']},{stats['Draw']}\n")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_stats():
    if not os.path.exists(STATS_FILE):
        return {'X': 0, 'O': 0, 'Draw': 0}
    try:
        with open(STATS_FILE) as f:
            line = f.readline()
            x, o, d = map(int, line.strip().split(','))
            return {'X': x, 'O': o, 'Draw': d}
    except:
        return {'X': 0, 'O': 0, 'Draw': 0}

def check_win(board, win_len=WIN_LEN):
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            if board[i][j] == '':
                continue
            # Горизонталь
            if j + win_len <= FIELD_SIZE and all(board[i][j + k] == board[i][j] for k in range(win_len)):
                return board[i][j]
            # Вертикаль
            if i + win_len <= FIELD_SIZE and all(board[i + k][j] == board[i][j] for k in range(win_len)):
                return board[i][j]
            # Диагональ вниз-вправо
            if i + win_len <= FIELD_SIZE and j + win_len <= FIELD_SIZE and \
                    all(board[i + k][j + k] == board[i][j] for k in range(win_len)):
                return board[i][j]
            # Диагональ вверх-вправо
            if i - win_len + 1 >= 0 and j + win_len <= FIELD_SIZE and \
                    all(board[i - k][j + k] == board[i][j] for k in range(win_len)):
                return board[i][j]
    if all(board[i][j] != '' for i in range(FIELD_SIZE) for j in range(FIELD_SIZE)):
        return 'Draw'
    return None

def ai_move(board, ai, level):
    empty = [(i, j) for i in range(FIELD_SIZE) for j in range(FIELD_SIZE) if board[i][j] == '']
    if not empty:
        return
    if level == "Легко":
        i, j = random.choice(empty)
        board[i][j] = ai
    elif level == "Средне":
        # Атака/блокировка
        human = 'O' if ai == 'X' else 'X'
        for i, j in empty:
            board[i][j] = ai
            if check_win(board) == ai:
                return
            board[i][j] = ''
        for i, j in empty:
            board[i][j] = human
            if check_win(board) == human:
                board[i][j] = ai
                return
            board[i][j] = ''
        i, j = random.choice(empty)
        board[i][j] = ai
    elif level == "Невозможно":
        move = find_best_move(board, ai)
        if move:
            i, j = move
            board[i][j] = ai
        else:
            i, j = random.choice(empty)
            board[i][j] = ai
    else:  
        i, j = random.choice(empty)
        board[i][j] = ai
#жоске алгоритм
MAX_DEPTH = 3

def evaluate_board(board, ai, opponent):
    ai_score = 0
    opp_score = 0
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            for di, dj in [(1,0), (0,1), (1,1), (1,-1)]:
                try:
                    # 4 в ряд
                    if all(0 <= i+di*k < FIELD_SIZE and 0 <= j+dj*k < FIELD_SIZE and board[i+di*k][j+dj*k] == ai for k in range(4)):
                        ai_score += 1000
                    if all(0 <= i+di*k < FIELD_SIZE and 0 <= j+dj*k < FIELD_SIZE and board[i+di*k][j+dj*k] == opponent for k in range(4)):
                        opp_score += 1000
                    # 3 в ряд
                    if all(0 <= i+di*k < FIELD_SIZE and 0 <= j+dj*k < FIELD_SIZE and board[i+di*k][j+dj*k] == ai for k in range(3)):
                        ai_score += 10
                    if all(0 <= i+di*k < FIELD_SIZE and 0 <= j+dj*k < FIELD_SIZE and board[i+di*k][j+dj*k] == opponent for k in range(3)):
                        opp_score += 10
                except:
                    pass
    return ai_score - opp_score

def is_hot(i, j, board):
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            ni, nj = i + dx, j + dy
            if 0 <= ni < FIELD_SIZE and 0 <= nj < FIELD_SIZE:
                if board[ni][nj] != '':
                    return True
    return False

def find_best_move(board, ai):
    opponent = 'O' if ai == 'X' else 'X'

    def minimax(board, depth, maximizing, alpha, beta):
        winner = check_win(board)
        if winner == ai:
            return 10000 - depth
        elif winner == opponent:
            return depth - 10000
        elif winner == 'Draw':
            return 0
        if depth >= MAX_DEPTH:
            return evaluate_board(board, ai, opponent)

        moves = [(i, j) for i in range(FIELD_SIZE) for j in range(FIELD_SIZE)
                 if board[i][j] == '' and is_hot(i, j, board)]
        if not moves:
            moves = [(i, j) for i in range(FIELD_SIZE) for j in range(FIELD_SIZE) if board[i][j] == '']

        if maximizing:
            max_eval = -float('inf')
            for i, j in moves:
                board[i][j] = ai
                eval = minimax(board, depth + 1, False, alpha, beta)
                board[i][j] = ''
                if eval > max_eval:
                    max_eval = eval
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for i, j in moves:
                board[i][j] = opponent
                eval = minimax(board, depth + 1, True, alpha, beta)
                board[i][j] = ''
                if eval < min_eval:
                    min_eval = eval
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    best_score = -float('inf')
    best_move = None
    for i in range(FIELD_SIZE):
        for j in range(FIELD_SIZE):
            if board[i][j] == '':
                board[i][j] = ai
                score = minimax(board, 1, False, -float('inf'), float('inf'))
                board[i][j] = ''
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
    if best_move is None:
        empty = [(i, j) for i in range(FIELD_SIZE) for j in range(FIELD_SIZE) if board[i][j] == '']
        return random.choice(empty)
    return best_move







def main_menu():
    mode = [None]
    level = [None]
    first_player = ["Игрок"]
    show_level = [False]
    show_start = [False]

    def pick_mode_ai():
        mode[0] = "AI"
        show_level[0] = True
        level[0] = None
        show_start[0] = False

    def pick_mode_pvp():
        mode[0] = "PVP"
        show_level[0] = False
        level[0] = None
        show_start[0] = True

    def pick_level_easy():
        level[0] = "Легко"
        show_start[0] = True

    def pick_level_med():
        level[0] = "Средне"
        show_start[0] = True

    def pick_first_human():
        first_player[0] = "Игрок"

    def pick_first_ai():
        first_player[0] = "Компьютер"

    btns_mode = [
        Button((100, 120, 270, 70), "Против ПК", pick_mode_ai),
        Button((430, 120, 270, 70), "2 игрока", pick_mode_pvp)
    ]
    btns_level = [
    Button((100, 230, 170, 60), "Легко", pick_level_easy),
    Button((320, 230, 170, 60), "Средне", pick_level_med),
    Button((540, 230, 220, 60), "Невозможно", lambda: set_level("Невозможно")) ]
    btns_first = [
        Button((100, 320, 320, 60), "Игрок ходит первым", pick_first_human),
        Button((440, 320, 320, 60), "Компьютер первым", pick_first_ai)
    ]
    btn_start = Button((300, 420, 200, 70), "Начать", lambda: None)

    def set_level(lvl):
        level[0] = lvl
        show_start[0] = True

    running = True
    while running:
        draw_background()
        title = font.render("Крестики-нолики 5x5", True, (255, 0, 0))
        cult = stat_font.render("Культ Кровавой Пентаграммы", True, (200, 0, 0))
        screen.blit(title, ((WIDTH - title.get_width()) // 2, 40))
        screen.blit(cult, ((WIDTH - cult.get_width()) // 2, 90))

        mx, my = pygame.mouse.get_pos()
        for btn in btns_mode:
            btn.draw((mx, my))
        if mode[0]:
            pygame.draw.rect(screen, (220, 0, 0), btns_mode[0 if mode[0] == "AI" else 1].rect, 3)

        if show_level[0]:
            for btn in btns_level:
                btn.draw((mx, my))
            levels = ["Легко", "Средне", "Невозможно"]
            if level[0] in levels:
                idx = levels.index(level[0])
                pygame.draw.rect(screen, (220, 0, 0), btns_level[idx].rect, 3)

        if mode[0] == "AI" and show_start[0]:
            for btn in btns_first:
                btn.draw((mx, my))
            pygame.draw.rect(screen, (220, 0, 0), btns_first[0 if first_player[0] == "Игрок" else 1].rect, 3)

        if show_start[0]:
            btn_start.draw((mx, my))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for btn in btns_mode:
                btn.handle_event(event)
            if show_level[0]:
                for btn in btns_level:
                    btn.handle_event(event)
            if mode[0] == "AI" and show_start[0]:
                for btn in btns_first:
                    btn.handle_event(event)
            if show_start[0]:
                btn_start.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and btn_start.rect.collidepoint(event.pos):
                    running = False

        pygame.display.flip()
        clock.tick(30)

    return level[0] if level[0] else "Легко", mode[0], first_player[0]


def play_game(level, mode, stats, first_player):
    board = [['' for _ in range(FIELD_SIZE)] for _ in range(FIELD_SIZE)]
    player = 'X'
    ai = 'O'
    ai_should_move = mode == "AI" and first_player == "Компьютер"
    run = True
    win = None
    fullscr = False

    while run:
        draw_background()
        draw_grid()
        for i in range(FIELD_SIZE):
            for j in range(FIELD_SIZE):
                x = j * CELL_SIZE + CELL_SIZE // 2
                y = i * CELL_SIZE + CELL_SIZE // 2
                if board[i][j] == 'X':
                    draw_pentagram((x, y), CELL_SIZE)
                elif board[i][j] == 'O':
                    draw_cross((x, y), CELL_SIZE)

        stat_text = stat_font.render(
            f"Победы культ божий: {stats['X']} | Победы культ бафомета: {stats['O']} | Ничьи: {stats['Draw']}",
            True, (220, 0, 0)
        )

        screen.blit(stat_text, (20, HEIGHT - 38))
        if win:
            msg = "Победил " + (
                "культ божий" if win == 'X'
                else ("культ бафомета" if win == 'O' else "Никто!")
            )
            msg_surf = msg_font.render(msg, True, (255, 0, 0))
            screen.blit(msg_surf, ((WIDTH - msg_surf.get_width()) // 2, HEIGHT // 2 - 30))

            screen.blit(msg_surf, ((WIDTH - msg_surf.get_width()) // 2, HEIGHT // 2 - 30))
            screen.blit(msg_surf, ((WIDTH - msg_surf.get_width()) // 2, HEIGHT // 2 - 30))
            restart_btn = Button((300, 650, 200, 70), "Заново", lambda: None)
            restart_btn.draw(pygame.mouse.get_pos())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_btn.rect.collidepoint(event.pos):
                        run = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        fullscr = not fullscr
                        pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscr else 0)
            pygame.display.flip()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    fullscr = not fullscr
                    pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN if fullscr else 0)
            if event.type == pygame.MOUSEBUTTONDOWN and mode == "PVP":
                x, y = event.pos
                if y >= CELL_SIZE * FIELD_SIZE:
                    continue
                j, i = x // CELL_SIZE, y // CELL_SIZE
                if board[i][j] == '':
                    board[i][j] = player
                    win = check_win(board)
                    if win: break
                    player = 'O' if player == 'X' else 'X'
            if event.type == pygame.MOUSEBUTTONDOWN and mode == "AI":
                if ai_should_move:
                    ai_move(board, ai, level)
                    win = check_win(board)
                    ai_should_move = False
                else:
                    x, y = event.pos
                    if y >= CELL_SIZE * FIELD_SIZE:
                        continue
                    j, i = x // CELL_SIZE, y // CELL_SIZE
                    if board[i][j] == '' and player == 'X':
                        board[i][j] = player
                        win = check_win(board)
                        if win: break
                        player = ai

        if mode == "AI" and player == ai and not win and not ai_should_move:
            pygame.time.wait(320)
            ai_move(board, ai, level)
            win = check_win(board)
            if win: continue
            player = 'X'

        pygame.display.flip()
        clock.tick(30)
    if win == 'Draw':
        stats['Draw'] += 1
    elif win:
        stats[win] += 1
    save_stats(stats)

def main():
    stats = load_stats()
    while True:
        level, mode, first_player = main_menu()
        play_game(level, mode, stats, first_player)

if __name__ == "__main__":
    main()
