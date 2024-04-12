import pygame
import threading
import random
from vosk import Model, KaldiRecognizer
import json
import sounddevice as sd

pygame.init()
pygame.mixer.init()
pygame.font.init()
pygame.display.set_caption('Memory Game')
match_sound = pygame.mixer.Sound('match.wav')

# Load the VOSK model for offline speech recognition
model_path = "vosk-model-small-en-us-0.15"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

# Initialize global variables for voice control
voice_command_queue = []
voice_control_mode = False
selected_cards = []
cards = []
matched_cards = []
game_over = False
current_player = 1
scores = {1: 0, 2: 0}
card_animations = {}  # Track animation state of cards
animation_in_progress = False
animation_update_speed = 0.005  # Decrease this value to slow down the animation
num_players = 1
# Constants for card states
HIDDEN = 0
REVEALED = 1
match = False
running = True

# Game settings
screen_width, screen_height = 640, 480
info_bar_height = 100  # Height of the information bar at the top
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

font = pygame.font.SysFont("calibri", 26)  # Creates a default system font of size 36
clock = pygame.time.Clock()  # Set up the clock for controlling frame rate


# Function to initialize the microphone and recognizer
def init_voice_recognition():
    def callback(indata, frames, time, status):
        if recognizer.AcceptWaveform(indata.tobytes()):
            result = json.loads(recognizer.Result())
            command = result.get('text', '').lower().strip()
            if command:
                voice_command_queue.append(command)

    try:
        with sd.InputStream(callback=callback, dtype='int16', channels=1, samplerate=16000):
            print("Voice recognition active. Speak now.")
            while True:
                pass  # Keep the stream alive until the game ends

    except Exception as e:
        print(f"Voice recognition error: {e}")


# Correct place to start the voice recognition thread
voice_thread = threading.Thread(target=init_voice_recognition, daemon=True)
voice_thread.start()


# Modified to return a boolean indicating whether an action was taken
def process_voice_commands():
    number_words_to_digits = {
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "ten": "10",
        "eleven": "11",
        "twelve": "12",
        "thirteen": "13",
        "fourteen": "14",
        "fifteen": "15",
        "sixteen": "16",
        "seventeen": "17",
        "eighteen": "18",
        "nineteen": "19",
        "twenty": "20"
    }
    action_taken = False  # Flag to track if any action was taken based on a voice command

    while voice_command_queue:
        command = voice_command_queue.pop(0).strip().lower()
        print(f"Processing command: {command}")

        # Convert number words to digits
        if command in number_words_to_digits:
            command = number_words_to_digits[command]

            print(f"{int(command)}: is a number = {command.isdigit()}")

        if command.isdigit():
            card_number = int(command) - 1

            if 0 <= card_number < len(cards):
                handle_card_selection(card_number)
                action_taken = True

    return action_taken


def match_check_and_handle():
    global selected_cards, matched_cards, scores, current_player, animation_in_progress, match

    if len(selected_cards) == 2:
        # Perform match checking
        match = check_for_match(cards, selected_cards, matched_cards, match_sound, scores, current_player)

        if match:
            matched_cards.extend(selected_cards)
            scores[current_player] += 1
            selected_cards.clear()  # Clear only on match to prevent immediate reset.

        animation_in_progress = False

    # Handle turn switching here if needed
    if not match and num_players == 2:
        current_player = 1 if current_player == 2 else 2


def handle_card_selection(index):
    global selected_cards, matched_cards, animation_in_progress, current_player, scores, num_players, card_animations

    if index in selected_cards or index in matched_cards:
        return  # Card already selected or matched, do nothing

    if len(selected_cards) < 2:
        card_animations[index] = {'progress': 0, 'color': cards[index], 'state': REVEALED}
        selected_cards.append(index)

    if len(selected_cards) == 2:
        # Delay match checking by setting a timer, do not reset animation_in_progress here
        pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # 1500 milliseconds delay


def reset_game(colors, cols, rows):
    cards = colors[:cols * rows // 2] * 2
    random.shuffle(cards)

    return cards, [], [], False, pygame.time.get_ticks(), 1, {1: 0, 2: 0}


def draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
               info_bar_height, card_animations, font):
    """
    Draws the cards on the screen, now accounting for animation states.
    """
    for index, card in enumerate(cards):
        row, col = divmod(index, cols)
        x = col * card_width
        y = row * card_height + info_bar_height

        animation = card_animations.get(index)

        if animation:
            width = card_width * (1 - abs(animation['progress'] - 0.5) * 2)
            x += (card_width - width) / 2
            color = animation['color'] if animation['progress'] >= 0.5 else hidden_color
        else:
            width = card_width
            color = card if index in matched_cards or index in selected_cards else hidden_color

        rect = pygame.Rect(x, y, width, card_height)
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, (0, 0, 0), rect, 3)  # Draw card border

        # Draw card number if not yet selected or matched
        if index not in matched_cards and index not in selected_cards:
            card_number = font.render(str(index + 1), True, (255, 255, 255))  # Assuming white numbers
            screen.blit(card_number, (
            x + card_width / 2 - card_number.get_width() / 2, y + card_height / 2 - card_number.get_height() / 2))


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


def display_text(screen, text, font, color, position):
    """
    Renders text on the screen at the specified position.
    """
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)


def display_difficulty_selection(screen, font, text_color):
    difficulties = ["Easy", "Medium", "Hard"]
    difficulty_rects = []
    screen.fill((255, 255, 255))  # Fill the screen with background color first

    for index, difficulty in enumerate(difficulties):
        text = font.render(difficulty, True, text_color)
        rect = text.get_rect(center=(320, 120 + index * 60))
        difficulty_rects.append(rect)
        screen.blit(text, rect)

    pygame.display.flip()  # Update the display to show the changes

    return difficulty_rects


def display_game_over_message(screen, message, font, text_color, screen_width, screen_height):
    game_over_surface = font.render(message, True, text_color)
    message_box_width = max(200, game_over_surface.get_width() + 20)
    message_box_height = 100
    message_box_x = (screen_width - message_box_width) // 2
    message_box_y = (screen_height - message_box_height) // 2

    pygame.draw.rect(screen, (100, 100, 100), (message_box_x, message_box_y, message_box_width, message_box_height))
    game_over_x = message_box_x + (message_box_width - game_over_surface.get_width()) // 2
    game_over_y = message_box_y + (message_box_height - game_over_surface.get_height()) // 2
    screen.blit(game_over_surface, (game_over_x, game_over_y))


def main_menu(screen, font, text_color):
    title_text = "Pick the game player's mode:"
    title_surface = font.render(title_text, True, text_color)
    title_rect = title_surface.get_rect(center=(320, 240 - 60))

    button_color = (150, 150, 150)
    button_padding_horizontal = 20  # Increase padding if necessary
    button_spacing = 10

    one_player_text = font.render('1 Player', True, text_color)
    two_player_text = font.render('2 Players', True, text_color)
    time_attack_text = font.render('Time Attack', True, text_color)
    voice_control_text = font.render('Voice Control', True, text_color)

    # Calculate button widths based on text widths
    one_player_button_width = one_player_text.get_width() + button_padding_horizontal
    two_player_button_width = two_player_text.get_width() + button_padding_horizontal
    time_attack_button_width = time_attack_text.get_width() + button_padding_horizontal
    voice_control_button_width = voice_control_text.get_width() + button_padding_horizontal

    # Calculate the total width for all buttons and spaces between them
    total_buttons_width = (one_player_button_width + two_player_button_width + time_attack_button_width
                           + voice_control_button_width + 3 * button_spacing)

    # Calculate the starting x position to center the buttons
    start_x_position = (screen.get_width() - total_buttons_width) // 2

    # Define the buttons with the new calculated positions and widths, moving Time Attack to the left
    time_attack_button = pygame.Rect(start_x_position, 240 - 25, time_attack_button_width, 50)
    one_player_button = pygame.Rect(start_x_position + time_attack_button_width + button_spacing, 240 - 25,
                                    one_player_button_width, 50)
    two_player_button = pygame.Rect(
        start_x_position + time_attack_button_width + one_player_button_width + 2 * button_spacing, 240 - 25,
        two_player_button_width, 50)
    voice_control_button = pygame.Rect(
        start_x_position + time_attack_button_width + one_player_button_width + two_player_button_width + 3 * button_spacing,
        240 - 25, voice_control_button_width, 50)

    screen.fill((255, 255, 255))

    # Display the buttons and the title
    screen.blit(title_surface, title_rect.topleft)
    pygame.draw.rect(screen, button_color, one_player_button)
    pygame.draw.rect(screen, button_color, two_player_button)
    pygame.draw.rect(screen, button_color, time_attack_button)
    pygame.draw.rect(screen, button_color, voice_control_button)

    # Blit the button text centered in the buttons
    screen.blit(one_player_text, one_player_text.get_rect(center=one_player_button.center))
    screen.blit(two_player_text, two_player_text.get_rect(center=two_player_button.center))
    screen.blit(time_attack_text, time_attack_text.get_rect(center=time_attack_button.center))
    screen.blit(voice_control_text, voice_control_text.get_rect(center=voice_control_button.center))

    pygame.display.flip()

    num_players = None
    time_attack = False
    voice_control = False  # Variable to track if voice control mode is selected

    while not num_players:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if one_player_button.collidepoint(event.pos):
                    num_players = 1
                elif two_player_button.collidepoint(event.pos):
                    num_players = 2
                elif time_attack_button.collidepoint(event.pos):
                    num_players = 1  # Time Attack mode is a kind of single-player mode
                    time_attack = True
                elif voice_control_button.collidepoint(event.pos):
                    num_players = 1
                    voice_control = True  # Set voice control mode to True when selected

    return num_players, time_attack, voice_control


def run_game():
    global voice_control_mode, cards, running, animation_in_progress

    # Difficulty selection
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
                        break

    # Adjust game settings based on difficulty
    cols, rows = {"Easy": (3, 4), "Medium": (4, 4), "Hard": (5, 4)}[difficulty]
    card_width, card_height = screen_width // cols, game_area_height // rows

    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(colors, cols, rows)
    # Main menu call now returns whether Time Attack mode is selected
    num_players, time_attack_mode, voice_control_mode = main_menu(screen, font, text_color)

    # Define button sizes and positions
    button_padding_horizontal = 10
    button_padding_vertical = 5

    # Draw reset button and define play again button
    reset_text = font.render('Reset', True, text_color)
    reset_button_width = reset_text.get_width() + (2 * button_padding_horizontal)
    reset_button_height = font.size('Test')[1] + (2 * button_padding_vertical)
    reset_button_rect = pygame.Rect(10, (info_bar_height - reset_button_height) // 2 + 25, reset_button_width,
                                    reset_button_height)  # Adjusted position

    play_again_text = font.render('Play Again', True, text_color)
    play_again_button_width = play_again_text.get_width() + (2 * button_padding_horizontal)
    play_again_button_height = reset_button_height
    play_again_button_rect = pygame.Rect(screen_width - play_again_button_width - 10,
                                         (info_bar_height - play_again_button_height) // 2 + 25,
                                         play_again_button_width, play_again_button_height)  # Adjusted position

    # Main game loop
    end_time = None
    play_again_visible = False
    # Initialize Time Attack mode variables
    time_attack_time_limit = 60
    time_attack_time_decrement = 5
    time_attack_start_time = None

    while not game_over:
        screen.fill(bg_color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.MOUSEBUTTONDOWN and (not animation_in_progress or voice_control_mode):
                mouse_x, mouse_y = event.pos

                if play_again_visible and play_again_button_rect.collidepoint(mouse_x, mouse_y):
                    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(
                        colors, cols, rows)
                    play_again_visible = False
                    continue
                if not play_again_visible and reset_button_rect.collidepoint(event.pos):
                    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(
                        colors, cols, rows)
                elif not play_again_visible:
                    if mouse_y > info_bar_height:
                        col = mouse_x // card_width
                        row = (mouse_y - info_bar_height) // card_height
                        index = row * cols + col

                        if 0 <= index < len(cards):
                            handle_card_selection(index)

            # Handle the event to flip cards back over
            if event.type == pygame.USEREVENT + 1:
                match_check_and_handle()

                if not match:
                    for idx in selected_cards:
                        card_animations[idx] = {'progress': 0, 'color': hidden_color, 'state': HIDDEN}

                selected_cards.clear()
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # Stop the timer

        # Modification: Added handling for updating the screen after voice command processing
        if voice_control_mode and process_voice_commands():  # Check if a command was processed and an action was taken
            # This ensures we give time to see the second card before checking for a match
            pass
            # pygame.time.set_timer(pygame.USEREVENT + 1, 1500)  # Delay before flipping back if no match

        # Time Attack mode logic
        if time_attack_mode and not game_over:
            current_time = pygame.time.get_ticks()

            if time_attack_start_time is None:
                time_attack_start_time = current_time

            elapsed_time = (current_time - time_attack_start_time) // 1000
            remaining_time = time_attack_time_limit - elapsed_time

            if remaining_time <= 0:
                game_over = True
                play_again_visible = True  # Show play again option
                time_attack_mode = False  # Exit Time Attack mode

        # If the game is over, handle the continuation for Time Attack mode or show game over message
        message = ""

        if game_over:
            play_again_visible = True

            if time_attack_mode:
                if len(matched_cards) == len(cards):
                    # Reset the game for Time Attack with a reduced time limit
                    time_attack_time_limit = max(10, time_attack_time_limit - time_attack_time_decrement)
                    cards, selected_cards, matched_cards, game_over, start_time, current_player, scores = reset_game(
                        colors, cols, rows)
                    time_attack_start_time = pygame.time.get_ticks()  # Restart the time attack timer
                    play_again_visible = False  # We're starting a new round, so hide the play again button
                else:
                    # Display the appropriate game over message for either mode
                    message = "Time's up! Try again?"
            else:
                # Regular mode game over handling
                if num_players == 2:
                    if scores[1] > scores[2]:
                        message = f'Player 1 Wins with {scores[1]} Points!'
                    elif scores[2] > scores[1]:
                        message = f'Player 2 Wins with {scores[2]} Points!'
                    else:  # Handle tie scenario
                        message = 'The game is a Tie!'
                else:
                    message = "Well done!" if len(matched_cards) == len(cards) else "Game Over!"

            if message:  # Display the game over message if it's set
                display_game_over_message(screen, message, font, text_color, screen_width, screen_height)

        # Draw UI elements like info bar, reset button, and timer
        pygame.draw.rect(screen, info_bar_color, (0, 0, screen_width, info_bar_height))
        pygame.draw.rect(screen, button_color, reset_button_rect)
        screen.blit(reset_text,
                    (reset_button_rect.x + button_padding_horizontal, reset_button_rect.y + button_padding_vertical))

        # Timer logic and rendering in the info bar
        current_time = pygame.time.get_ticks()

        if len(matched_cards) == len(cards) and not game_over:  # Check if all cards have been matched
            game_over = True
            end_time = current_time  # Capture end time at the moment game ends
            play_again_visible = True

        if not game_over:
            elapsed_time = (current_time - start_time) // 1000
        else:
            elapsed_time = (end_time - start_time) // 1000

        # Prevent elapsed time from going negative
        elapsed_time = max(0, elapsed_time)

        timer_minutes = elapsed_time // 60
        timer_seconds = elapsed_time % 60
        timer_text = f'{timer_minutes:02}:{timer_seconds:02}'
        timer_surface = font.render(timer_text, True, text_color, info_bar_color)
        timer_rect = timer_surface.get_rect(center=((screen_width // 2), (info_bar_height // 2) + 25))
        screen.blit(timer_surface, timer_rect)

        if play_again_visible:
            pygame.draw.rect(screen, button_color, play_again_button_rect)
            screen.blit(play_again_text, (
                play_again_button_rect.x + button_padding_horizontal,
                play_again_button_rect.y + button_padding_vertical))

        # Display scores and current player's turn for 2 Player mode
        if num_players == 2:
            display_text(screen, f"Player 1: {scores[1]} - Player 2: {scores[2]}", font, text_color, (10, 10))
            display_text(screen, f"Player {current_player}'s Turn", font, text_color, (screen_width - 220, 10))

        # Animation logic to update or clear animations
        to_remove = []

        for index, animation in card_animations.items():
            if animation['state'] == REVEALED:
                animation['progress'] += animation_update_speed
                if animation['progress'] >= 1:
                    animation_in_progress = False
                    to_remove.append(index)

            elif animation['state'] == HIDDEN:
                animation['progress'] += animation_update_speed

                if animation['progress'] >= 1:
                    matched_cards.remove(index)  # Remove from matched_cards if it's not a match
                    to_remove.append(index)

        for index in to_remove:
            del card_animations[index]

        draw_cards(screen, cards, selected_cards, matched_cards, card_width, card_height, cols, hidden_color,
                   info_bar_height, card_animations, font)
        pygame.display.flip()
        clock.tick(60)  # Maintain a steady frame rate

    pygame.quit()


if __name__ == "__main__":
    try:
        run_game()
    except Exception as e:
        print(f"Error: {e}")
