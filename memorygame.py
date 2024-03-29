import pygame
import random


def initialize_cards(colors, cols, rows):
    # Generate cards with colors
    cards = []
    for color in colors:
        cards.append(color)
        cards.append(color)
    random.shuffle(cards)
    return cards


def draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color):
    for i, card_color in enumerate(cards):
        row = i // cols
        col = i % cols
        x = col * card_width
        y = row * card_height

        if i in matched_cards or i in selected_cards:
            pygame.draw.rect(screen, card_color, (x, y, card_width, card_height))
        else:
            pygame.draw.rect(screen, hidden_color, (x, y, card_width, card_height))


def check_for_match(cards, selected_cards, matched_cards):
    if len(selected_cards) == 2:
        index1, index2 = selected_cards
        if cards[index1] == cards[index2]:
            matched_cards.extend([index1, index2])
        selected_cards.clear()


def run_game():
    pygame.init()

    # Game settings
    screen_width, screen_height = 640, 480
    screen = pygame.display.set_mode((screen_width, screen_height))
    bg_color = (255, 255, 255)
    hidden_color = (0, 0, 0)
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),
              (255, 0, 255), (0, 255, 255), (128, 0, 0), (0, 128, 0)]
    cols, rows = 4, 4
    card_width, card_height = screen_width // cols, screen_height // rows

    cards = initialize_cards(colors, cols, rows)
    selected_cards, matched_cards = [], []
    game_over = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                x, y = pygame.mouse.get_pos()
                col, row = x // card_width, y // card_height
                index = row * cols + col
                if index not in selected_cards and index not in matched_cards:
                    selected_cards.append(index)
                if len(selected_cards) == 2:
                    pygame.time.wait(500)
                    check_for_match(cards, selected_cards, matched_cards)

        screen.fill(bg_color)
        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color)

        if len(matched_cards) == len(cards) and not game_over:
            game_over = True
            print("Game Over! Press any key to exit.")

        pygame.display.flip()

        if game_over:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                    running = False

    pygame.quit()


if __name__ == "__main__":
    run_game()
