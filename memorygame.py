import pygame
import random
import sys


def reset_game(colors, cols, rows):
    """
    Resets the game by preparing a new set of cards, shuffling them,
    and resetting game state variables.
    """
    num_pairs = cols * rows // 2
    cards = colors[:num_pairs] * 2
    # Ensure there are enough colors to fill the grid, repeat color pairs if necessary
    extended_colors = (colors * ((num_pairs // len(colors)) + 1))[:num_pairs]
    cards = extended_colors * 2

    random.shuffle(cards)
    selected_cards = []
    matched_cards = []
    game_over = False
    start_time = pygame.time.get_ticks()

    return cards, selected_cards, matched_cards, game_over, start_time


def draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
               info_bar_height):
    """
    Draws the cards on the screen. Shows card color if selected or matched, otherwise shows a hidden color.
    """
    for index, card in enumerate(cards):
        row, col = divmod(index, cols)
        x = col * card_width
        y = row * card_height + info_bar_height
        rect = pygame.Rect(x, y, card_width, card_height)
        if index in matched_cards or index in selected_cards:
            pygame.draw.rect(screen, card, rect)
        else:
            pygame.draw.rect(screen, hidden_color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)  # Draw card border


def check_for_match(cards, selected_cards, matched_cards, match_sound):
    if len(selected_cards) == 2:
        index1, index2 = selected_cards
        if cards[index1] == cards[index2]:
            matched_cards.extend([index1, index2])
            match_sound.play()  # Play sound on match
        selected_cards.clear()


def display_difficulty_selection(screen, font, text_color):
    screen.fill((255, 255, 255))  # Fill the screen with white
    difficulties = ["Easy", "Medium", "Hard"]
    difficulty_rects = []
    for index, difficulty in enumerate(difficulties):
        text = font.render(difficulty, True, text_color)
        rect = text.get_rect(center=(320, 120 + index * 60))
        screen.blit(text, rect)
        difficulty_rects.append(rect)
    pygame.display.flip()
    return difficulty_rects


def run_game():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    match_sound = pygame.mixer.Sound('match.wav')

    # Game settings
    screen_width, screen_height = 640, 480
    info_bar_height = 50  # Height of the information bar at the top
    game_area_height = screen_height - info_bar_height  # Adjusted height for the game area
    screen = pygame.display.set_mode((screen_width, screen_height))
    bg_color = (255, 255, 255)
    info_bar_color = (230, 230, 230)  # A light grey color for the information bar
    button_color = (150, 150, 150)  # Color for the reset button
    hidden_color = (0, 0, 0)
    text_color = (0, 0, 0)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
              (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)]

    font = pygame.font.SysFont(None, 36)  # Creates a default system font of size 36

    # Difficulty selection screen
    difficulty_rects = display_difficulty_selection(screen, font, text_color)
    difficulty = None
    while difficulty is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(difficulty_rects):
                    if rect.collidepoint(event.pos):
                        difficulty = ["Easy", "Medium", "Hard"][i]
        pygame.time.wait(100)

    # Adjust game settings based on difficulty
    cols, rows = {"Easy": (3, 4), "Medium": (4, 4), "Hard": (5, 4)}[difficulty]

    card_width, card_height = screen_width // cols, game_area_height // rows

    cards, selected_cards, matched_cards, game_over, start_time = reset_game(colors, cols, rows)

    # Define buttons
    reset_button_rect = pygame.Rect(10, 10, 100, 30)
    play_again_text = font.render('Play Again', True, text_color)
    play_again_button_rect = play_again_text.get_rect(topleft=(screen_width - 160, 10))
    play_again_button_rect.inflate_ip(20, 10)  # Increase the button size to cover all the text

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button_rect.collidepoint(event.pos) or play_again_button_rect.collidepoint(event.pos):
                    cards, selected_cards, matched_cards, game_over, start_time = reset_game(colors, cols, rows)
                    game_over = False
                elif not game_over:
                    x, y = event.pos
                    if y > info_bar_height:
                        col, row = x // card_width, (y - info_bar_height) // card_height
                        if row < rows and col < cols:
                            index = row * cols + col
                            if 0 <= index < len(cards):
                                if index not in selected_cards and index not in matched_cards:
                                    selected_cards.append(index)
                                if len(selected_cards) == 2:
                                    pygame.time.wait(200)
                                    check_for_match(cards, selected_cards, matched_cards, match_sound)
                                    if len(matched_cards) == len(cards):
                                        game_over = True

        screen.fill(bg_color)

        # Draw the information bar at the top
        pygame.draw.rect(screen, info_bar_color, (0, 0, screen_width, info_bar_height))

        # Draw reset button
        pygame.draw.rect(screen, button_color, reset_button_rect)
        reset_text = font.render('Reset', True, text_color)
        screen.blit(reset_text, (reset_button_rect.x + 5, reset_button_rect.y + 5))

        # Timer logic and rendering in the info bar
        if not game_over:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time) // 1000
            timer_minutes = elapsed_time // 60
            timer_seconds = elapsed_time % 60
            timer_surface = font.render(f'{timer_minutes:02}:{timer_seconds:02}', True, text_color)
            screen.blit(timer_surface,
                        (reset_button_rect.right + 10, (info_bar_height - timer_surface.get_height()) // 2))

        # Draw cards
        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
                   info_bar_height)

        if game_over:
            well_done_surface = font.render('Well done!', True, text_color)
            screen.blit(well_done_surface, ((screen_width // 2) - (well_done_surface.get_width() // 2), 10))

            pygame.draw.rect(screen, button_color, play_again_button_rect)
            screen.blit(play_again_text, (play_again_button_rect.x + 5, play_again_button_rect.y + 5))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()
