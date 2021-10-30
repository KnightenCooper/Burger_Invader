"""
Burger Invaders

Space Invaders but with burgers and a chef.
"""
import random
import arcade
from pathlib import Path # allows us to get path for image/sound files

SPRITE_SCALING_PLAYER = 0.5
SPRITE_SCALING_enemy = 0.5
SPRITE_SCALING_LASER = 0.8

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Burger Invaders"

BULLET_SPEED = 5
ENEMY_SPEED = 2

MAX_PLAYER_BULLETS = 3

# This margin controls how close the enemy gets to the left or right side
# before reversing direction.
ENEMY_VERTICAL_MARGIN = 15
RIGHT_ENEMY_BORDER = SCREEN_WIDTH - ENEMY_VERTICAL_MARGIN
LEFT_ENEMY_BORDER = ENEMY_VERTICAL_MARGIN

# How many pixels to move the enemy down when reversing
ENEMY_MOVE_DOWN_AMOUNT = 20

# Game state
YOU_WIN = 3
GAME_OVER = 1
PLAY_GAME = 0


class MyGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Variables that will hold sprite lists
        self.player_list = None
        self.enemy_list = None
        self.player_bullet_list = None
        self.enemy_bullet_list = None
        self.shield_list = None

        # Textures for the enemy
        self.enemy_textures = None

        # State of the game
        self.game_state = PLAY_GAME

        # Set up the player info
        self.player_sprite = None
        self.score = 0

        # Enemy movement
        self.enemy_change_x = -ENEMY_SPEED

        # Don't show the mouse cursor
        self.set_mouse_visible(False)

        arcade.set_background_color(arcade.color.AMAZON)

        # arcade.configure_logging()

    def setup_level_one(self):
        # Load the textures for the enemies, one facing left, one right
        self.enemy_textures = []
        enemy_sprite_path = str(Path(__file__).parent.resolve()) + f"\\assets\\burger.png"
        texture = arcade.load_texture(enemy_sprite_path, mirrored=True)
        self.enemy_textures.append(texture)
        texture = arcade.load_texture(enemy_sprite_path)
        self.enemy_textures.append(texture)

        # Create rows and columns of enemies
        x_count = 10
        x_start = 0
        x_spacing = 60
        y_count = 5
        y_start = 550
        y_spacing = 40
        for x in range(x_start, x_spacing * x_count + x_start, x_spacing):
            for y in range(y_start, y_spacing * y_count + y_start, y_spacing):

                # Create the enemy instance
                enemy = arcade.Sprite()
                enemy.scale = SPRITE_SCALING_enemy
                enemy.texture = self.enemy_textures[1]

                # Position the enemy
                enemy.center_x = x
                enemy.center_y = y

                # Add the enemy to the lists
                self.enemy_list.append(enemy)

    def make_shield(self, x_start):
        """
        Make a shield, which is just a 2D grid of solid color sprites
        stuck together with no margin so you can't tell them apart.
        """
        shield_block_width = 5
        shield_block_height = 10
        shield_width_count = 20
        shield_height_count = 5
        y_start = 150
        for x in range(x_start, x_start + shield_width_count * shield_block_width, shield_block_width):
            for y in range(y_start, y_start + shield_height_count * shield_block_height, shield_block_height):
                shield_sprite = arcade.SpriteSolidColor(shield_block_width, shield_block_height, arcade.color.WHITE)
                shield_sprite.center_x = x
                shield_sprite.center_y = y
                self.shield_list.append(shield_sprite)

    def setup(self):
        """
        Set up the game and initialize the variables.
        Call this method if you implement a 'play again' feature.
        """

        self.game_state = PLAY_GAME

        # background music
        song = arcade.load_sound(str(Path(__file__).parent.resolve()) + f"\\assets\\song.mp3")
        arcade.play_sound(volume = 0.1, sound = song)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_bullet_list = arcade.SpriteList()
        self.enemy_bullet_list = arcade.SpriteList()
        self.shield_list = arcade.SpriteList(is_static=True)

        # Set up the player
        self.score = 0

        # Image from assets folder
        player_sprite_path = str(Path(__file__).parent.resolve()) + f"\\assets\\chef.png"
        self.player_sprite = arcade.Sprite(player_sprite_path, SPRITE_SCALING_PLAYER)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 40
        self.player_list.append(self.player_sprite)

        # Make each of the shields
        for x in range(75, 800, 190):
            self.make_shield(x)

        # Set the background color
        arcade.set_background_color(arcade.color.OLD_HELIOTROPE)

        self.setup_level_one()

    def on_draw(self):
        """ Render the screen. """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.enemy_list.draw()
        self.player_bullet_list.draw()
        self.enemy_bullet_list.draw()
        self.shield_list.draw()
        self.player_list.draw()

        # Render the text
        arcade.draw_text(f"Score: {self.score}", 10, 20, arcade.color.WHITE, 14)

        # Draw game over if the game state is such
        if self.game_state == GAME_OVER:
            arcade.draw_text(f"GAME OVER", 250, 300, arcade.color.WHITE, 55)
            self.set_mouse_visible(True)

        # Draw You Win if the game state is such
        if self.game_state == YOU_WIN:
            arcade.draw_text(f"YOU WIN", 250, 300, arcade.color.WHITE, 55)
            self.set_mouse_visible(True)

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Called whenever the mouse moves.
        """

        # Don't move the player if the game is over
        if self.game_state == GAME_OVER:
            return

        # player will be in same place as mouse
        self.player_sprite.center_x = x
        self.player_sprite.center_y = y 

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """

        # Only allow the user so many bullets on screen at a time to prevent
        # them from spamming bullets.
        if len(self.player_bullet_list) < MAX_PLAYER_BULLETS:

            # Gunshot sound
            gun_sounds = ["throw1", "throw3", "throw4", "throw4"]
            random_sound = gun_sounds[random.randrange(0, 4)]
            self.gun_sound = arcade.load_sound(str(Path(__file__).parent.resolve()) + f"\\assets\\{random_sound}.wav")
            arcade.play_sound(self.gun_sound)

            # Create a player bullet randomly from the list of options
            player_bullets = ["frying_pan", "rolling_pin", "spoon", "knife"]
            random_bullet = player_bullets[random.randrange(0, 4)]
            bullet_sprite_path = str(Path(__file__).parent.resolve()) + f"\\assets\\{random_bullet}.png"
            bullet = arcade.Sprite(bullet_sprite_path, SPRITE_SCALING_LASER)

            # The image points to the right, and we want it to point up. So
            # rotate it.
            # Set up the initial angle, and the "spin"
            bullet.angle = random.randrange(360)
            bullet.change_angle = random.randrange(15, 16)


            # Give the bullet a speed
            bullet.change_y = BULLET_SPEED

            # Position the bullet
            bullet.center_x = self.player_sprite.center_x
            bullet.bottom = self.player_sprite.top

            # Add the bullet to the appropriate lists
            self.player_bullet_list.append(bullet)

    def update_enemies(self):

        # Move the enemy vertically
        for enemy in self.enemy_list:
            enemy.center_x += self.enemy_change_x

        # Check every enemy to see if any hit the edge. If so, reverse the
        # direction and flag to move down.
        move_down = False
        for enemy in self.enemy_list:
            if enemy.right > RIGHT_ENEMY_BORDER and self.enemy_change_x > 0:
                self.enemy_change_x *= -1
                move_down = True
            if enemy.left < LEFT_ENEMY_BORDER and self.enemy_change_x < 0:
                self.enemy_change_x *= -1
                move_down = True

        # Did we hit the edge above, and need to move the enemy down?
        if move_down:
            # Yes
            for enemy in self.enemy_list:
                # Move enemy down
                enemy.center_y -= ENEMY_MOVE_DOWN_AMOUNT
                # Flip texture on enemy so it faces the other way
                if self.enemy_change_x > 0:
                    enemy.texture = self.enemy_textures[0]
                else:
                    enemy.texture = self.enemy_textures[1]
                    # Set up the initial angle, and the "spin"



    def allow_enemies_to_fire(self):
        """
        See if any enemies will fire this frame.
        """
        # Track which x values have had a chance to fire a bullet.
        # Since enemy list is build from the bottom up, we can use
        # this to only allow the bottom row to fire.
        x_spawn = []
        for enemy in self.enemy_list:
            # Adjust the chance depending on the number of enemies. Fewer
            # enemies, more likely to fire.
            chance = 4 + len(self.enemy_list) * 4

            # Fire if we roll a zero, and no one else in this column has had
            # a chance to fire.
            if random.randrange(chance) == 0 and enemy.center_x not in x_spawn:
                # Create a enemy bullet randomly from the list of options
                enemy_bullets = ["onion", "top_bun", "patty", "tomato_pickle"]
                random_bullet = enemy_bullets[random.randrange(0, 4)]
                bullet_sprite_path = str(Path(__file__).parent.resolve()) + f"\\assets\\{random_bullet}.png"

                bullet = arcade.Sprite(bullet_sprite_path, SPRITE_SCALING_LASER)
                # Spin as it falls
                bullet.angle = random.randrange(360)
                bullet.change_angle = random.randrange(15, 16)
                # Give the bullet a speed
                bullet.change_y = -BULLET_SPEED

                # Position the bullet so its top is   right below the enemy
                bullet.center_x = enemy.center_x
                bullet.top = enemy.bottom

                # Add the bullet to the appropriate list
                self.enemy_bullet_list.append(bullet)

            # Ok, this column has had a chance to fire. Add to list so we don't
            # try it again this frame.
            x_spawn.append(enemy.center_x)

    def process_enemy_bullets(self):

        # Move the bullets
        self.enemy_bullet_list.update()

        # Loop through each bullet
        for bullet in self.enemy_bullet_list:
            # Check this bullet to see if it hit a shield
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)

            # If it did, get rid of the bullet and shield blocks
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # See if the player got hit with a bullet
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_bullet_list):
                self.game_state = GAME_OVER

            # See if the player got enough points to win
            if self.score == 50:
                self.game_state = YOU_WIN
            # If the bullet falls off the screen get rid of it
            if bullet.top < 0:
                bullet.remove_from_sprite_lists()

    def process_player_bullets(self):

        # Move the bullets
        self.player_bullet_list.update()

        # Loop through each bullet
        for bullet in self.player_bullet_list:

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.shield_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()
                for shield in hit_list:
                    shield.remove_from_sprite_lists()
                continue

            # Check this bullet to see if it hit a enemy
            hit_list = arcade.check_for_collision_with_list(bullet, self.enemy_list)

            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            # For every enemy we hit, add to the score and remove the enemy
            for enemy in hit_list:
                enemy.remove_from_sprite_lists()
                self.score += 1

                # Hit Sound
                hit_sounds = ["hit1", "hit2", "hit1", "hit4"]
                random_sound = hit_sounds[random.randrange(0, 4)]
                self.hit_sound = arcade.load_sound(str(Path(__file__).parent.resolve()) + f"\\assets\\{random_sound}.wav")
                arcade.play_sound(self.hit_sound)

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > SCREEN_HEIGHT:
                bullet.remove_from_sprite_lists()

    def on_update(self, delta_time):
        """ Movement and game logic """
        # don't update is the game is over or the player wins
        if self.game_state == GAME_OVER or self.game_state == YOU_WIN:
            return
        #update the game
        self.update_enemies()
        self.allow_enemies_to_fire()
        self.process_enemy_bullets()
        self.process_player_bullets()

        # if there are no enemies then add more
        if len(self.enemy_list) == 0:
            self.setup_level_one()


# call the game
def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()

# Sources:
# https://www.bensound.com/royalty-free-music/track/dreams-chill-out
# https://pixabay.com
# freesound.org/search/
# https://api.arcade.academy/en/latest/examples/sprite_collect_rotating.html
# https://github.com/pythonarcade/arcade/blob/maintenance/doc/examples/bloom_defender.rst
# https://api.arcade.academy/en/2.6.1/get_started.html
# https://github.com/tasdikrahman/spaceShooter/blob/master/spaceshooter/spaceShooter.py
# https://github.com/KnightenCooper/game
# https://github.com/pythonarcade/community-rpg
# https://api.arcade.academy/en/latest/examples/asteroid_smasher.html#asteroid-smasher
# https://api.arcade.academy/en/latest/examples/index.html#sprite-non-player-movement
# https://api.arcade.academy/en/latest/examples/index.html#shooting-with-sprites
# https://api.arcade.academy/en/latest/examples/slime_invaders.html#slime-invaders
# https://api.arcade.academy/en/latest/examples/index.html#sprite-player-movement
# https://learn.arcade.academy/en/latest/chapters/18_sprites_and_collisions/sprites.html#basic-sprites-and-collisions