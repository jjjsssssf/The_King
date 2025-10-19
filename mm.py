import pygame
import threading
import time 
import os
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
except pygame.error as e:
    pass
tocando_musica = False
def tocar_musica(caminho_musica):
    global tocando_musica    
    if not os.path.exists(caminho_musica):
        return
    try:
        pygame.mixer.music.load(caminho_musica)
        pygame.mixer.music.play(-1)
        tocando_musica = True        
    except pygame.error as e:
        tocando_musica = False

def escolher_e_tocar_musica(caminho_musica):
    parar_musica()
    threading.Thread(target=tocar_musica, args=(caminho_musica,), daemon=True).start()

def parar_musica():
    global tocando_musica
    if tocando_musica:
        pygame.mixer.music.stop()
        tocando_musica = False
