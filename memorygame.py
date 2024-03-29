import pygame
import random
import sys


def initialize_cards(colors, cols, rows):
    # Generate cards with colors
    cards = []
    for color in colors:
        cards.append(color)
        cards.append(color)
    random.shuffle(cards)
    return cards


def draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
               info_bar_height):
    for i, card_color in enumerate(cards):
        row = i // cols
        col = i % cols
        x = col * card_width
        y = row * card_height + info_bar_height  # Offset the y position

        if i in matched_cards or i in selected_cards:
            pygame.draw.rect(screen, card_color, (x, y, card_width, card_height))
        else:
            pygame.draw.rect(screen, hidden_color, (x, y, card_width, card_height))


def check_for_match(cards, selected_cards, matched_cards, match_sound):
    if len(selected_cards) == 2:
        index1, index2 = selected_cards
        if cards[index1] == cards[index2]:
            matched_cards.extend([index1, index2])
            match_sound.play()  # Play sound on match
        selected_cards.clear()


def reset_game(colors, cols, rows):
    cards = initialize_cards(colors, cols, rows)
    selected_cards = []
    matched_cards = []
    game_over = False
    start_time = pygame.time.get_ticks()

    return cards, selected_cards, matched_cards, game_over, start_time


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
    cols, rows = 4, 4
    card_width, card_height = screen_width // cols, game_area_height // rows
    cards, selected_cards, matched_cards, game_over, start_time = reset_game(colors, cols, rows)

    font = pygame.font.SysFont(None, 36)  # Creates a default system font of size 36

    # Define buttons
    reset_button_rect = pygame.Rect(10, 10, 100, 30)
    play_again_button_text = font.render('Play Again', True, text_color)
    play_again_button_rect = play_again_button_text.get_rect(topleft=(screen_width - 110, 10))
    play_again_button_rect.inflate_ip(20, 10)  # Increase the button size to cover all the text

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if reset_button_rect.collidepoint(event.pos) or (
                        game_over and play_again_button_rect.collidepoint(event.pos)):
                    cards, selected_cards, matched_cards, game_over, start_time = reset_game(colors, cols, rows)
                elif not game_over:
                    x, y = event.pos
                    if y > info_bar_height:  # Only proceed if the click is within the game area
                        col, row = x // card_width, (y - info_bar_height) // card_height
                        if row < rows and col < cols:  # Check if the click is within the grid bounds
                            index = row * cols + col
                            if 0 <= index < len(cards):  # Ensure the index is within the range of cards
                                if index not in selected_cards and index not in matched_cards:
                                    selected_cards.append(index)
                                if len(selected_cards) == 2:
                                    pygame.time.wait(500)
                                    check_for_match(cards, selected_cards, matched_cards, match_sound)

        screen.fill(bg_color)

        # Draw the information bar at the top
        pygame.draw.rect(screen, info_bar_color, (0, 0, screen_width, info_bar_height))
        reset_text = font.render('Reset', True, text_color)
        screen.blit(reset_text, (reset_button_rect.x + 5, reset_button_rect.y + 5))
        play_again_text = font.render('Play Again', True, text_color)

        if game_over:
            # Display 'Well done!' message
            well_done_surface = font.render('Well done!', True, text_color)
            screen.blit(well_done_surface,
                        (reset_button_rect.right + 20, (info_bar_height - well_done_surface.get_height()) // 2))

            # Draw and display 'Play Again' button
            pygame.draw.rect(screen, button_color, play_again_button_rect)  # Draw play again button
            screen.blit(play_again_text, play_again_button_rect.topleft)

        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
                   info_bar_height)

        # Timer logic and rendering in the info bar
        if not game_over:
            current_time = pygame.time.get_ticks()
            elapsed_time = (current_time - start_time) // 1000
            timer_minutes = elapsed_time // 60
            timer_seconds = elapsed_time % 60
            timer_surface = font.render(f'{timer_minutes:02}:{timer_seconds:02}', True, text_color)
            screen.blit(timer_surface, (110, (info_bar_height - timer_surface.get_height()) // 2))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()
