from classe_arts import draw_window,term, clear, art_ascii, Cores, mini_mapa_, dialogos, clear_region_a
from classe_do_jogador import *

player_b = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=art.necro, skin=0,skin_nome='')
mapas = mini_mapa_()
def mapa_prai():
    mapa = mapas.praia.split("\n")
    obstaculos = {'#','~','♣','&',"C", '‼','¥', 'o', '0', '1','„','♠', 'x'} 
    cores = {'#':term.brown, '♣':term.green, '~':term.lightblue_on_darkblue, 'C':term.brown, '.':term.yellow,
'*': term.lightgreen, '-':term.bold_yellow,'‼':term.bold_yellow,'¥':term.darkgreen, 'o': term.bold_ligtgray,
'0':term.orange, '1':term.green,'„': term.bold_ligtgreen,'♠': term.darkgreen, 'x':term.bold_brown}

    return {
        "nome": "Praia",
        "mapa": mapa,
        "obstaculos": obstaculos,
        "cores": cores,

    }

def mapa_caverna(player_b):
    mapa = mapas.caverna.split("\n")
    obstaculos = {'#', 'o', 'G', 'F', 'B', 'f'} 
    cores = {'#':term.brown,'B':term.brown, '.':term.darkcyan, 'o': term.bold_ligtgray,
'G':term.red, 'F': term.magenta, 'f':term.bold_lightcyan}

    return {
        "nome": f"Caverna-[{player_b.andar}]",
        "mapa": mapa,
        "obstaculos": obstaculos,
        "cores": cores,

    }
def mapa_caverna2(player_b):
    mapa = mapas.caverna2.split("\n")
    obstaculos = {'#', 'o', 'G', 'F', 'B', 'f'} 
    cores = {'#':term.brown,'B':term.brown, '.':term.darkcyan, 'o': term.bold_ligtgray,
'G':term.red, 'F': term.magenta, 'f':term.bold_lightcyan}

    return {
        "nome": f"Caverna-[{player_b.andar}]",
        "mapa": mapa,
        "obstaculos": obstaculos,
        "cores": cores,

    }

