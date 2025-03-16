"""
This demonstration shows how pulse compression can reult in better resolution.
Two graphs will be displayed. On the bottom is the sent signal (in blue)
and a combined received signal (in red) that has bounced off of two targets.
The top graph will display the recieved signal after the matched filter has been applied.

If PULSE_COMPRESSION is set to False, the returns from the two objects mix together,
but if it is set to true, it is clear that there are two objects.
"""


import numpy as np
from scipy import signal

import pygame

from util import C, cw_pulse, chirp_pulse, reflection, draw_wave, deterministic_noise

if __name__ == "__main__":
    PULSE_COMPRESSION = True

    FREQ = 10
    PW = 1.0
    PRF = 10.0

    WIDTH = 5.0

    NOISE = 0.01

    RESOLUTION = 0.01

    pygame.init()
    scr = pygame.display.set_mode((1000, 400))
    clock = pygame.time.Clock()


    if PULSE_COMPRESSION:
        send_fn = chirp_pulse(FREQ - 8, FREQ + 8, PW, PRF)

    else:
        send_fn = cw_pulse(FREQ, PW, PRF)

    # refl_0 = reflection(send_fn, 0.6, 0.0, 0.5)
    # refl_1 = reflection(send_fn, 0.9, 0.0, 0.25)

    refl_0 = reflection(send_fn, 0.6, 0.0, 0.5)
    refl_1 = reflection(send_fn, 0.75, 0.0, 0.25)

    noise_fn = deterministic_noise(NOISE)
    
    def recv_fn(t: np.ndarray[float]) -> np.ndarray[float]:
        return refl_0(t) + refl_1(t) + noise_fn(t)

    filter = np.sqrt(16) * send_fn(np.arange(0, int(PW / RESOLUTION)) * RESOLUTION)

    t = 0

    while all(event.type != pygame.QUIT for event in pygame.event.get()):
        scr.fill([255, 255, 255])
        pygame.draw.line(
            scr, 
            [0, 0, 0], 
            [0, 200], 
            [1000, 200],
        )
        sig_send = send_fn(np.arange(int(-WIDTH / (C * RESOLUTION)), 0) * RESOLUTION + t)
        sig_recv = recv_fn(np.arange(int(-WIDTH / (C * RESOLUTION)), 0) * RESOLUTION + t)
        
        draw_wave( # draw recieved wave
            scr,
            -sig_recv * 50,
            0,
            1000,
            300,
            (255, 0, 0),
        )
        draw_wave( # draw transmitted wave
            scr,
            -sig_send * 50,
            0,
            1000,
            300,
            (0, 0, 255),
        )
        draw_wave( # draw matched filter output
            scr,
            -signal.correlate(sig_recv, filter, "same") / len(filter) * 50,
            0,
            1000,
            100,
            (255, 0, 0),
        )
        pygame.display.flip()
        clock.tick(60)
        t += 2 / 60

