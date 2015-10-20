__author__ = 'unit978'

from pygame import Rect


class Camera:

    def __init__(self, boundBox, worldBounds=None):

        self.boundingBox = boundBox
        self.target = None

    def update(self, delta_time):

        if self.target is not None:

            # Center around the target
            self.boundingBox.center = self.target.position.to_tuple()