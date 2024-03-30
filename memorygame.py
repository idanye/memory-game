import pygame
import random


def reset_game(colors, cols, rows, num_players):
    """
    Resets the game by preparing a new set of cards, shuffling them,
    and resetting game state variables.
    """
    cards = colors[:cols * rows // 2] * 2
    random.shuffle(cards)

    return cards, [], [], False, pygame.time.get_ticks(), 1, [0] * (num_players + 1)


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


def check_for_match(cards, selected_cards, matched_cards, match_sound, scores, current_player):
    match = False

    if len(selected_cards) == 2:
        if cards[selected_cards[0]] == cards[selected_cards[1]]:
            matched_cards.extend(selected_cards)
            scores[current_player] += 1
            match_sound.play()
            match = True

        selected_cards.clear()

    return match


def display_difficulty_selection(font, text_color):
    difficulties = ["Easy", "Medium", "Hard"]
    difficulty_rects = []

    for index, difficulty in enumerate(difficulties):
        text = font.render(difficulty, True, text_color)
        rect = text.get_rect(center=(320, 120 + index * 60))
        difficulty_rects.append(rect)

    return difficulty_rects


def run_game():
    pygame.init()
    pygame.mixer.init()
    pygame.font.init()
    match_sound = pygame.mixer.Sound('match.wav')
    pygame.display.set_caption('Memory Game')

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
    colors = [
        (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
        (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0),
        (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128),
        (192, 192, 192), (128, 128, 128), (64, 0, 0), (0, 64, 0),
        (0, 0, 64), (64, 64, 0), (64, 0, 64), (0, 64, 64)
    ]

    font = pygame.font.SysFont("calibri", 36)  # Creates a default system font of size 36

    title_text = "Pick the game player's mode:"
    title_surface = font.render(title_text, True, text_color)
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 60))

    player_turns = {1: "Player 1's turn", 2: "Player 2's turn"}
    player_scores = {1: 0, 2: 0}

    # Create turn indicator rectangle here
    turn_indicator = font.render('', True, text_color, info_bar_color)
    turn_indicator_rect = turn_indicator.get_rect(topleft=(10, 5))

    button_width, button_height = 150, 50
    button_gap = 10
    total_buttons_width = (button_width * 2) + button_gap

    one_player_button_left = (screen_width // 2) - (total_buttons_width // 2)
    one_player_button = pygame.Rect(one_player_button_left, screen_height // 2 - button_height // 2, button_width,
                                    button_height)

    two_player_button_left = one_player_button_left + button_width + button_gap
    two_player_button = pygame.Rect(two_player_button_left, screen_height // 2 - button_height // 2, button_width,
                                    button_height)

    one_player_text = font.render('1 Player', True, text_color)
    two_player_text = font.render('2 Players', True, text_color)

    num_players = None

    while not num_players:
        screen.fill(bg_color)
        screen.blit(title_surface, title_rect.topleft)

        pygame.draw.rect(screen, button_color, one_player_button)
        pygame.draw.rect(screen, button_color, two_player_button)

        screen.blit(one_player_text, one_player_text.get_rect(center=one_player_button.center))
        screen.blit(two_player_text, two_player_text.get_rect(center=two_player_button.center))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if one_player_button.collidepoint(event.pos):
                    num_players = 1
                    break
                elif two_player_button.collidepoint(event.pos):
                    num_players = 2
                    break

    # Once the number of players is chosen, proceed to difficulty selection
    difficulty_rects = display_difficulty_selection(font, text_color)
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
                        break
        if difficulty:
            break

    # Adjust game settings based on difficulty
    cols, rows = {"Easy": (3, 4), "Medium": (4, 4), "Hard": (5, 4)}[difficulty]
    card_width, card_height = screen_width // cols, game_area_height // rows

    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(colors, cols, rows, num_players)

    # Define button sizes and positions
    button_padding_horizontal = 10
    button_padding_vertical = 5

    # Draw reset button and define play again button
    reset_text = font.render('Reset', True, text_color)
    reset_button_width = reset_text.get_width() + (2 * button_padding_horizontal)
    reset_button_height = font.size('Test')[1] + (2 * button_padding_vertical)
    reset_button_rect = pygame.Rect(10, (info_bar_height - reset_button_height) // 2, reset_button_width,
                                    reset_button_height)

    play_again_text = font.render('Play Again', True, text_color)
    play_again_button_width = play_again_text.get_width() + (2 * button_padding_horizontal)
    play_again_button_height = reset_button_height
    play_again_button_rect = pygame.Rect(screen_width - play_again_button_width - 10,
                                         (info_bar_height - play_again_button_height) // 2, play_again_button_width,
                                         play_again_button_height)

    # Main game loop
    running = True
    end_time = None
    play_again_visible = False

    while running:
        screen.fill(bg_color)
        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
                   info_bar_height)

        # Player turn indicator
        if num_players and not play_again_visible:
            turn_indicator = font.render(player_turns[current_player], True, text_color, info_bar_color)
            turn_indicator_rect = turn_indicator.get_rect(topleft=(10, 5))
            screen.blit(turn_indicator, turn_indicator_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not play_again_visible:
                if reset_button_rect.collidepoint(event.pos):
                    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(
                        colors, cols, rows, num_players)
                    current_player = 1
                else:
                    mouse_x, mouse_y = event.pos

                    if mouse_y > info_bar_height:
                        col = mouse_x // card_width
                        row = (mouse_y - info_bar_height) // card_height
                        index = row * cols + col

                        if 0 <= index < len(cards):
                            if index not in selected_cards + matched_cards:
                                selected_cards.append(index)
                            if len(selected_cards) == 2:
                                pygame.time.wait(200)

                                if check_for_match(cards, selected_cards, matched_cards, match_sound, player_scores,
                                                   current_player):
                                    if num_players == 2:
                                        continue
                                else:
                                    current_player = 2 if current_player == 1 else 1

        screen.fill(bg_color)

        if num_players:
            turn_text = font.render(player_turns[current_player], True, text_color, info_bar_color)
            screen.blit(turn_text, (10, 5))  # Adjust as necessary

        pygame.draw.rect(screen, info_bar_color, (0, 0, screen_width, info_bar_height))
        pygame.draw.rect(screen, button_color, reset_button_rect)
        screen.blit(reset_text,
                    (reset_button_rect.x + button_padding_horizontal, reset_button_rect.y + button_padding_vertical))

        if play_again_visible:
            pygame.draw.rect(screen, button_color, play_again_button_rect)
            screen.blit(play_again_text, (
                play_again_button_rect.x + button_padding_horizontal,
                play_again_button_rect.y + button_padding_vertical))

        # Timer logic and rendering in the info bar
        current_time = pygame.time.get_ticks()

        if not game_over:
            elapsed_time = (current_time - start_time) // 1000

            if check_for_match(cards, selected_cards, matched_cards, match_sound, scores, current_player):
                if num_players == 2:
                    # If there's a match, current player gets another turn
                    pass
                else:
                    game_over = True  # Single-player mode can end the game
            else:
                if num_players == 2:
                    # Switch turns if no match
                    current_player = 2 if current_player == 1 else 1
        else:
            elapsed_time = (end_time - start_time) // 1000  # Use end_time if game is over

        timer_minutes = elapsed_time // 60
        timer_seconds = elapsed_time % 60
        timer_text = f'{timer_minutes:02}:{timer_seconds:02}'
        timer_surface = font.render(timer_text, True, text_color, info_bar_color)
        timer_rect = timer_surface.get_rect(center=((screen_width // 2), (info_bar_height // 2)))
        screen.blit(timer_surface, timer_rect)

        # Draw cards
        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
                   info_bar_height)

        if game_over:
            play_again_visible = True
            message_box_width, message_box_height = 200, 100
            message_box_x, message_box_y = (screen_width - message_box_width) // 2, (
                    screen_height - message_box_height) // 2
            pygame.draw.rect(screen, (100, 100, 100),
                             (message_box_x, message_box_y, message_box_width, message_box_height))

            well_done_surface = font.render('Well done!', True, text_color)
            well_done_x = message_box_x + (message_box_width - well_done_surface.get_width()) // 2
            well_done_y = message_box_y + (message_box_height - well_done_surface.get_height()) // 2
            screen.blit(well_done_surface, (well_done_x, well_done_y))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()
