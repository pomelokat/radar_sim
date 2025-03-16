"""
This demonstration shows the doppler effect.
The blue wave is the transmitted wave, and the red wave is the reflected wave.
If RVEL is 0.0, the transmitted and reflected waves have the same frequency, 
but because the object that the waves are reflecting off of is moving to the left,
the returning wave has a higher frequency.
"""


import numpy as np

import pygame

from util import C, cw_pulse, reflection, draw_wave

if __name__ == "__main__":
    RVEL = -0.2
    pygame.init()
    scr = pygame.display.set_mode((1000, 200))
    clock = pygame.time.Clock()
    t = 10
    while all(event.type != pygame.QUIT for event in pygame.event.get()):
        sig_send = cw_pulse(0.5, 1.0, 1.0) # 1 GHz
        sig_recv = reflection(sig_send, 8.0, RVEL, 0.5)
        scr.fill([255, 255, 255])
        d = 8.0 + t * RVEL
        pygame.draw.line(
            scr, 
            [0, 0, 0], 
            [100, 0], 
            [100, 200],
        )
        pygame.draw.line(
            scr, 
            [0, 0, 0], 
            [100 + 100 * d, 0], 
            [100 + 100 * d, 200],
        )
        draw_wave(
            scr,
            sig_send(np.linspace(0.0, -d / C, 1000) + t) * 50,
            100,
            100 + d * 100,
            100,
            [0, 0, 255],
        )
        draw_wave(
            scr,
            sig_recv(np.linspace(0.0, d / C, 1000) + t) * 50,
            100,
            100 + d * 100,
            100,
            [255, 0, 0],
        )
        pygame.display.flip()
        clock.tick(60)
        t += 2 / 60

