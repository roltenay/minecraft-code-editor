import sys
import subprocess
import pygame

# Pygame Başlatma
pygame.init()
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Minecraft Code Editor v0.1")
clock = pygame.time.Clock()

# --- RENK PALETİ (Minecraft Temalı) ---
DIRT_BROWN = (86, 60, 42)
BEDROCK_DARK = (30, 30, 30)
CHAT_BG = (20, 20, 20, 200)
COMMAND_BLOCK_BG = (160, 100, 60)
PANEL_BORDER = (50, 50, 50)
TEXT_WHITE = (240, 240, 240)

# Cevher Renkleri (Syntax Highlighting)
DIAMOND_BLUE = (85, 255, 255)    # 'def', 'class', 'import'
EMERALD_GREEN = (85, 255, 85)    # 'if', 'else', 'for', 'while', 'return'
GOLD_YELLOW = (255, 255, 85)     # 'print', 'len', 'range', sayılar
REDSTONE_RED = (255, 85, 85)     # Buton / Hatalar
LAPIS_BLUE = (85, 85, 255)       # String ifadeler

# Fontlar
FONT_SIZE = 20
try:
    # Varsa sistemdeki Monospace font, yoksa varsayılan
    code_font = pygame.font.SysFont("Courier", FONT_SIZE, bold=True)
    ui_font = pygame.font.SysFont("Arial", 16, bold=True)
except Exception:
    code_font = pygame.font.Font(None, FONT_SIZE)
    ui_font = pygame.font.Font(None, 18)

# --- EDİTÖR DURUMLARI ---
code_lines = [
    "# Minecraft Python Editor",
    "def selamla():",
    "    print('Merhaba Minecraft!')",
    "",
    "selamla()"
]
cursor_line = 4
cursor_col = 8

output_text = "Çıktı burada görünecek... [Redstone Şalterine Basın]"

# Buton Alanı (Redstone Çalıştır)
run_button_rect = pygame.Rect(730, 20, 140, 45)


def run_code(lines):
    """Yazılan kodu geçici olarak çalıştırır ve çıktısını döndürür."""
    code_str = "\n".join(lines)
    try:
        result = subprocess.run(
            [sys.executable, "-c", code_str],
            capture_output=True,
            text=True,
            timeout=3
        )
        if result.stderr:
            return f"[HATA]: {result.stderr.strip()}"
        return result.stdout.strip() if result.stdout else "[Kod çalıştı, çıktı yok]"
    except subprocess.TimeoutExpired:
        return "[HATA]: Kod zaman aşımına uğradı (Sonsuz döngü olabilir)!"
    except Exception as e:
        return f"[HATA]: {str(e)}"


def get_token_color(word):
    """Anahtar kelimelere Minecraft cevher renkleri atar."""
    keywords_blue = {"def", "class", "import", "from", "as"}
    keywords_green = {"if", "else", "elif", "for", "while", "in", "return", "True", "False"}
    keywords_yellow = {"print", "range", "len", "input", "int", "str"}
    
    clean_word = word.strip("():,")
    if clean_word in keywords_blue:
        return DIAMOND_BLUE
    elif clean_word in keywords_green:
        return EMERALD_GREEN
    elif clean_word in keywords_yellow or clean_word.isdigit():
        return GOLD_YELLOW
    elif word.startswith("'") or word.startswith('"') or word.endswith("'") or word.endswith('"'):
        return LAPIS_BLUE
    return TEXT_WHITE


# --- ANA DÖNGÜ ---
running = True
cursor_visible = True
cursor_timer = 0

while running:
    dt = clock.tick(30)
    cursor_timer += dt
    if cursor_timer >= 500:
        cursor_visible = not cursor_visible
        cursor_timer = 0

    # --- ETKİLEŞİM VE GİRDİ (EVENTS) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                # Run Butonuna Tıklama
                if run_button_rect.collidepoint(event.pos):
                    output_text = run_code(code_lines)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Enter: Yeni Satır Aç
                current_text = code_lines[cursor_line]
                left_part = current_text[:cursor_col]
                right_part = current_text[cursor_col:]
                
                # Otomatik girinti koruma
                indent = len(left_part) - len(left_part.lstrip(' '))
                if left_part.endswith(':'):
                    indent += 4
                
                code_lines[cursor_line] = left_part
                code_lines.insert(cursor_line + 1, " " * indent + right_part)
                cursor_line += 1
                cursor_col = indent

            elif event.key == pygame.K_BACKSPACE:
                # Silme
                if cursor_col > 0:
                    current_text = code_lines[cursor_line]
                    code_lines[cursor_line] = current_text[:cursor_col - 1] + current_text[cursor_col:]
                    cursor_col -= 1
                elif cursor_line > 0:
                    prev_len = len(code_lines[cursor_line - 1])
                    code_lines[cursor_line - 1] += code_lines[cursor_line]
                    code_lines.pop(cursor_line)
                    cursor_line -= 1
                    cursor_col = prev_len

            elif event.key == pygame.K_LEFT:
                if cursor_col > 0:
                    cursor_col -= 1
                elif cursor_line > 0:
                    cursor_line -= 1
                    cursor_col = len(code_lines[cursor_line])

            elif event.key == pygame.K_RIGHT:
                if cursor_col < len(code_lines[cursor_line]):
                    cursor_col += 1
                elif cursor_line < len(code_lines) - 1:
                    cursor_line += 1
                    cursor_col = 0

            elif event.key == pygame.K_UP:
                if cursor_line > 0:
                    cursor_line -= 1
                    cursor_col = min(cursor_col, len(code_lines[cursor_line]))

            elif event.key == pygame.K_DOWN:
                if cursor_line < len(code_lines) - 1:
                    cursor_line += 1
                    cursor_col = min(cursor_col, len(code_lines[cursor_line]))

            elif event.key == pygame.K_TAB:
                code_lines[cursor_line] = (
                    code_lines[cursor_line][:cursor_col] + "    " + code_lines[cursor_line][cursor_col:]
                )
                cursor_col += 4

            else:
                # Karakter Ekleme
                if event.unicode and event.unicode.isprintable():
                    current_text = code_lines[cursor_line]
                    code_lines[cursor_line] = (
                        current_text[:cursor_col] + event.unicode + current_text[cursor_col:]
                    )
                    cursor_col += 1

    # --- ÇİZİM (RENDER) ---
    screen.fill(DIRT_BROWN)

    # 1. Editör Alanı (Komut Bloğu Temalı)
    editor_rect = pygame.Rect(20, 20, 690, 420)
    pygame.draw.rect(screen, BEDROCK_DARK, editor_rect)
    pygame.draw.rect(screen, COMMAND_BLOCK_BG, editor_rect, 4)

    # Kod Satırlarını Çizdirme
    y_offset = 35
    for line_idx, line in enumerate(code_lines):
        x_offset = 60
        
        # Satır Numarası
        num_surf = ui_font.render(f"{line_idx + 1:>2}", True, (120, 120, 120))
        screen.blit(num_surf, (30, y_offset))

        # Kelime bazlı Renklendirme
        words = line.split(" ")
        for i, word in enumerate(words):
            color = get_token_color(word)
            word_surf = code_font.render(word + (" " if i < len(words) - 1 else ""), True, color)
            screen.blit(word_surf, (x_offset, y_offset))
            x_offset += word_surf.get_width()

        # İmleç (Cursor) Çizimi
        if line_idx == cursor_line and cursor_visible:
            cursor_x_part = line[:cursor_col]
            cursor_x = 60 + code_font.render(cursor_x_part, True, TEXT_WHITE).get_width()
            pygame.draw.line(screen, DIAMOND_BLUE, (cursor_x, y_offset), (cursor_x, y_offset + FONT_SIZE), 2)

        y_offset += FONT_SIZE + 4

    # 2. Çalıştır Butonu (Redstone Şalteri)
    pygame.draw.rect(screen, REDSTONE_RED, run_button_rect, border_radius=6)
    pygame.draw.rect(screen, (200, 30, 30), run_button_rect, 3, border_radius=6)
    btn_text = ui_font.render("[>] REDSTONE", True, TEXT_WHITE)
    screen.blit(btn_text, (run_button_rect.x + 18, run_button_rect.y + 12))

    # 3. Sohbet / Terminal Penceresi (Output)
    console_rect = pygame.Rect(20, 460, 860, 160)
    pygame.draw.rect(screen, CHAT_BG, console_rect)
    pygame.draw.rect(screen, PANEL_BORDER, console_rect, 2)

    console_title = ui_font.render("< Minecraft Server Chat / Output >", True, GOLD_YELLOW)
    screen.blit(console_title, (30, 470))

    # Output metnini satırlara bölüp basma
    out_lines = output_text.split("\n")
    out_y = 500
    for out_line in out_lines[:5]:  # En fazla 5 satır göster
        out_color = REDSTONE_RED if "[HATA]" in out_line else TEXT_WHITE
        out_surf = ui_font.render(out_line, True, out_color)
        screen.blit(out_surf, (35, out_y))
        out_y += 22

    pygame.display.flip()

pygame.quit()
sys.exit()