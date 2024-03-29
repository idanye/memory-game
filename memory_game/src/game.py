import pygame
import random


def run_game():
    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    screen_width = 640
    screen_height = 480
    screen = pygame.display.set_mode((screen_width, screen_height))

    # Colors
    bg_color = (255, 255, 255)
    hidden_color = (0, 0, 0)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
              (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)]

    # Grid setup
    rows = 4
    cols = 4
    card_width = screen_width // cols
    card_height = screen_height // rows

    # Game variables
    cards = []
    selected_cards = []
    matched_cards = []
    game_over = False

    # Generate cards with colors
    for color in colors:
        cards.append(color)
        cards.append(color)
    random.shuffle(cards)

    def draw_cards():
        for i in range(len(cards)):
            row = i // cols
            col = i % cols
            x = col * card_width
            y = row * card_height

            if i in matched_cards or i in selected_cards:
                pygame.draw.rect(screen, cards[i], (x, y, card_width, card_height))
            else:
                pygame.draw.rect(screen, hidden_color, (x, y, card_width, card_height))

    def check_for_match():
        if len(selected_cards) == 2:
            index1, index2 = selected_cards
            if cards[index1] == cards[index2]:
                matched_cards.append(index1)
                matched_cards.append(index2)
            selected_cards.clear()

    # Main game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                col = x // card_width
                row = y // card_height
                index = row * cols + col
                if index not in selected_cards and index not in matched_cards:
                    selected_cards.append(index)
                if len(selected_cards) == 2:
                    pygame.time.wait(500)  # Wait a bit for the player to see the cards
                    check_for_match()

        screen.fill(bg_color)
        draw_cards()

        if len(matched_cards) == len(cards):
            game_over = True
            print("Game Over!")

        pygame.display.flip()

    pygame.quit()