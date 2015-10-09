__author__ = 'unit978'

from Vector2 import Vector2
from pygame import Rect, draw


class GameObject(object):

    def __init__(self):
        self.position = Vector2(0, 0)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)

        # RGB
        self.color = (255, 255, 255)
        self.boundingBox = Rect(0, 0, 1, 1)

        self.tag = "gameobject"

    # Update the game object at every delta_time interval.
    def update(self, delta_time):

        # Kinematics: v = dr / dt
        # dr = v * dt
        # -------------------------------------------
        # delta pos = vel * dt
        # new position = current position + delta pos
        # current position = new position
        self.velocity += self.acceleration * delta_time
        self.position += self.velocity * delta_time

        # Update the position of the bounding box so it goes with the game object.
        w = self.boundingBox.width
        h = self.boundingBox.height

        # Center the bounding box around the position vector.
        self.boundingBox.topleft = (self.position.x - w/2, self.position.y - h/2)

    # Render to screen.
    def render(self, screen):
        draw.rect(screen, self.color, self.boundingBox)


class EnemyGameObject(GameObject):

    def __init__(self, all_game_objects_list):

        super(EnemyGameObject, self).__init__()
        self.target = None

        # Fire at every interval of time
        self.fire_interval = 1.0

        # Keeps track of when to shoot
        self.firing_timer = 0.0

        self.all_game_objects = all_game_objects_list

        self.firing_speed = 500

    def shoot(self):
        # Direction to target
        dirToTarget = Vector2.get_normal(self.target.position - self.position)

        # Create a bullet
        bullet = GameObject()
        bullet.tag = "enemy bullet"

        bullet.position.x = self.position.x
        bullet.position.y = self.position.y
        bullet.velocity = dirToTarget * self.firing_speed
        bullet.boundingBox = Rect(self.position.to_tuple(), (5, 5))
        bullet.color = (0, 255, 0)
        bullet.killByTimer = True
        bullet.lifeTimer = 1.0
        self.all_game_objects.append(bullet)

    def update(self, delta_time):
        super(EnemyGameObject, self).update(delta_time)

        if self.target is not None:
            self.firing_timer += delta_time

            if self.firing_timer >= self.fire_interval:
                self.shoot()
                self.firing_timer = 0.0


class Particle(GameObject):

    def __init__(self):
        super(Particle, self).__init__()

        # Life span of the particle.
        # Use set_life() instead. Don't modify directly.
        self.lifeTimer = 0.0
        self.lifeStart = 0.0

        self.tag = "particle"

    def set_life(self, value):
        self.lifeTimer = self.lifeStart = value

    def update(self, delta_time):
        super(Particle, self).update(delta_time)

        self.lifeTimer -= delta_time