import typing

import numpy as np
from scipy import signal

import pygame

# units: meters and nanoseconds
C = 0.3

# sine wave on then off
def cw_pulse(
    freq: float,
    pw: float,
    prf: float,
) -> typing.Callable[[np.ndarray[float]], np.ndarray[np.complex128]]:
    def fn(t: np.ndarray[float]) -> np.ndarray[np.complex128]:
        out = np.exp(2j * np.pi * t * freq)
        out[t < 0] = 0
        out[(t % prf) > pw] = 0
        return out
    return fn

# frequency modulation pulse compression
def chirp_pulse(
    f0: float,
    f1: float,
    pw: float,
    prf: float,
) -> typing.Callable[[np.ndarray[float]], np.ndarray[np.complex128]]:
    def fn(t: np.ndarray[float]) -> np.ndarray[np.complex128]:
        out = signal.chirp(t % prf, f0, pw, f1)
        out[t < 0] = 0
        out[(t % prf) > pw] = 0
        return out
    return fn

# reflect a signal off a target - what gets returned?
def reflection(
    sig: typing.Callable[[np.ndarray[float]], np.ndarray[np.complex128]],
    tgt_loc: float,
    tgt_vel: float,
    tgt_xs: float,
) -> typing.Callable[[np.ndarray[float]], np.ndarray[np.complex128]]:
    
    def fn(t_recv: np.ndarray[float]) -> np.ndarray[np.complex128]:
        t_refl = (t_recv * C - tgt_loc) / (tgt_vel + C)
        d_refl = tgt_loc + tgt_vel * t_refl
        t_send = t_refl - d_refl / C
        return sig(t_send) * tgt_xs #* d_refl ** -2
    
    return fn

# generate normally distributed complex numbers using floats as seeds
# now less slow using box-muller transform
def deterministic_noise(
    scale: float = 1.0,
    seed: int = 18,
) -> typing.Callable[[np.ndarray[float]], np.ndarray[np.complex128]]:
    m = np.int64(0xAAAAAAAAAAAAAAA) # alternating 1s and 0s
    def fn(t: np.ndarray[float]) -> np.ndarray[np.complex128]:
        # reinterpret the bits of t as belonging to an integer, mix things up with the *1.3
        x = ((t * 1.3 + hash(seed)).astype(np.float64).view(np.int64))
        # odd bits to one side and even bits to the other
        a, b = (x & m) % np.e, (x & ~m) % np.pi
        # apply box-muller transform
        # assert np.all(a > 0), np.min(a)
        return scale * np.sqrt(2 - 2 * np.log(a + 1e-7)) * np.exp(2j * b)
            
    return fn

def draw_wave(
    surf: pygame.Surface, 
    signal: np.ndarray[float | np.complex128],
    x0: float,
    x1: float,
    y: float,
    color: tuple[int, int, int] = (0, 0, 255),
) -> None:
    x = np.linspace(x0, x1, len(signal))
    pygame.draw.lines(
        surf, 
        color, 
        False, 
        [(int(xx), int(yy)) for xx, yy in zip(x, signal.real + y)],
    )