__author__ = 'unit978'

import pygame
import sys
from GameObject import *
from Vector2 import Vector2
from random import randrange, uniform
from pygame import gfxdraw
from math import pi

# Initialize any modules that pygame uses.
pygame.init()

screen_size = (1200, 700)

# Bits per pixel, 8 bits for each RGBA value.
bpp = 32
screen = pygame.display.set_mode(screen_size, pygame.HWSURFACE, bpp)

all_game_objects = list()

# MAKE THE PLAYER
player = GameObject()
player.position.x = screen_size[0]/2.0
player.position.y = screen_size[1]/2.0
player.color = (255, 0, 0)
player.boundingBox = Rect(player.position.to_tuple(), (12, 12))
all_game_objects.append(player)

# Motion variables
player_accel = 500.0
player_friction = 0.95

player_boost_interval = 0.05
player_boost_timer = 0.0

# MAKE BACKGROUND
background_img = pygame.Surface(screen_size).convert()
background_img.fill((0, 0, 0))
# fill with stars
numStars = 500
for i in range(0, numStars):
    color = (randrange(50, 255), randrange(50, 255), randrange(50, 255))
    x = randrange(0, screen_size[0])
    y = randrange(0, screen_size[1])
    gfxdraw.pixel(background_img, x, y, color)


def control_player_motion(dt):

    # Move player based on key states (able to detect multiple keys at once).
    keys = pygame.key.get_pressed()

    # Acceleration on the X axis.
    if keys[pygame.K_a]:
        player.acceleration.x = -player_accel

    elif keys[pygame.K_d]:
        player.acceleration.x = player_accel

    else:
        player.acceleration.x = 0.0

    # Acceleration on the Y axis.
    if keys[pygame.K_w]:
        player.acceleration.y = -player_accel

    elif keys[pygame.K_s]:
        player.acceleration.y = player_accel

    else:
        player.acceleration.y = 0.0

    # Apply friction if going fast enough
    if player.velocity.sq_magnitude() > 1:
        player.velocity -= player.velocity * player_friction * dt

    # Zero out if moving too slow
    else:
        player.velocity *= 0.0


def handle_player_input(event):

    # Make the player shoot towards to mouse.
    if event.type == pygame.MOUSEBUTTONDOWN:

        # Direction to mouse
        mouseX, mouseY = pygame.mouse.get_pos()
        mousePos = Vector2(mouseX, mouseY)
        dirToMouse = Vector2.get_normal(mousePos - player.position)

        # Create a bullet
        bullet = GameObject()
        bullet.tag = "player bullet"

        bullet.position.x = player.position.x
        bullet.position.y = player.position.y
        bullet.velocity = dirToMouse * 600.0
        bullet.boundingBox = Rect(player.position.to_tuple(), (5, 5))
        bullet.color = (255, 150, 255)
        bullet.set_life(1.3)
        all_game_objects.append(bullet)


def create_particle_effect(emit_pos, amount, color, dir_range=(0.0, 2.0 * pi), life_range=(1.0, 5.0)):
    for p in range(0, amount):

        particle = GameObject()
        particle.tag = "particle"
        particle.position.x = emit_pos.x
        particle.position.y = emit_pos.y

        size = randrange(2, 5)
        particle.boundingBox = Rect(particle.position.to_tuple(), (size, size))

        # particle velocity direction
        particle.velocity = Vector2(1, 0)
        particle.velocity.set_direction(uniform(dir_range[0], dir_range[1]))

        particle.velocity *= randrange(50, 200)
        particle.color = color
        particle.set_life(uniform(life_range[0], life_range[1]))
        all_game_objects.append(particle)


enemy = EnemyGameObject(all_game_objects)
enemy.position = Vector2(500, 50)
enemy.velocity = Vector2(200, 0)
enemy.fire_interval = 0.3
enemy.firing_speed = 900.0
enemy.boundingBox = Rect(enemy.position.to_tuple(), (10, 10))
enemy.color = (255, 100, 0)
enemy.target = player
enemy_dir = 0.0
all_game_objects.append(enemy)

quit_game = False

delta_time = 0.0
last_frame_time = 0.0
timer = pygame.time.Clock()

while not quit_game:

    # Get the time in milliseconds.
    start_frame_time = pygame.time.get_ticks()

    # Get all events that were triggered and process them.
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            quit_game = True

        handle_player_input(event)

    control_player_motion(delta_time)

    screen.blit(background_img, (0, 0))

    # Iterate backwards - much safer solution for iteration and removal at the same time.
    for i in xrange(len(all_game_objects) - 1, -1, -1):
        game_object = all_game_objects[i]
        game_object.update(delta_time)
        game_object.render(screen)

        # Enemy hits player - create particles - remove bullet
        if game_object.tag == "enemy bullet":
            if game_object.boundingBox.colliderect(player.boundingBox):
                create_particle_effect(player.position, 15, (0, 255, 150))
                del all_game_objects[i]

        # Player hits enemy - create particles - remove bullet
        elif game_object.tag == "player bullet":
            if game_object.boundingBox.colliderect(enemy.boundingBox):
                create_particle_effect(enemy.position, 15, (255, 255, 0))
                del all_game_objects[i]

        # Darken the particle color as time goes on.
        elif game_object.tag == "particle":

            # convert the color into a Color object.
            r, g, b = game_object.color
            color = pygame.Color(r, g, b)

            # Get the HSV representation of the color.
            h, s, v, a = color.hsva

            # Lower the value of the color - make it darker as time goes on.
            # As the particle ages, the color value goes down with respect to how old it is.
            # For example...if the particle started with a life of 10s and the current life
            # for the particle is 5s then it has gone through 50% of its life which means
            # that the value will be set 50% of the max value for a color (which is 100%).
            timeElapsedPercent = game_object.lifeTimer / game_object.lifeStart
            v = 100.0 * timeElapsedPercent

            # cap the minimum value.
            if v < 5:
                v = 5

            # Set the new value for the color
            color.hsva = (h, s, v, a)

            # update game object color to the new color.
            game_object.color = (color.r, color.g, color.b)

        # Kill object if its life timer ran out.
        if game_object.killByTimer and game_object.lifeTimer < 0:
            del all_game_objects[i]

    # Create particle effects for "engine boost".
    if player.acceleration.sq_magnitude() > 1:
        if player_boost_timer >= player_boost_interval:

            # The opposite direction of the player's acceleration
            direction = (player.acceleration * -1.0).direction()

            # Create particles between these two angles.
            direction_range = (direction - pi/6.0, direction + pi/6.0)
            create_particle_effect(player.position, 5, (0, 255, 255), direction_range, (0.2, 1.0))

            # Reset timer to create the next particle effect.
            player_boost_timer = 0.0

        player_boost_timer += delta_time

    # Move the enemy in a circle.
    enemy.velocity.set_direction(enemy_dir)
    enemy_dir += 0.7 * delta_time

    # Don't let direction get too large, cap it and 360 degrees.
    if enemy_dir > 2 * pi:
        enemy_dir -= 2 * pi

    pygame.display.update()

    # Store how long the frame lasted in seconds.
    delta_time = (start_frame_time - last_frame_time) / 1000.0

    # Mark the time the frame ended, so we can later calculate delta time.
    last_frame_time = start_frame_time


# Un-initialize pygame modules.
pygame.quit()

# Kill the window.
sys.exit()