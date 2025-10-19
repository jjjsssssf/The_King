#PxPlus ToshibaTxL1 8x16
from blessed import Terminal
import os
term = Terminal()
import sys
if os.name == 'nt':
    try:
        import ctypes
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        handle = ctypes.windll.kernel32.GetStdHandle(-11) 
        mode = ctypes.c_ulong(0)
        ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(mode))
        mode.value |= ENABLE_VIRTUAL_TERMINAL_PROCESSING
        ctypes.windll.kernel32.SetConsoleMode(handle, mode)        
    except Exception:
        pass
def clear():
    print(term.home + term.clear_eos, end="")
def clear_region_a(x, start_y, end_y, width):
    if end_y < start_y:
        start_y, end_y = end_y, start_y 
    empty_line = ' ' * width
    for y in range(start_y, end_y + 1):
        print(term.move_xy(x, y) + empty_line)

def linhas():
    print(term.bold_white("<<"+"="*25+">>"))
def linha_inven():
    print(term.bold_blue("<<")+term.bold_white("="*30)+term.bold_blue(">>"))
def linhas_batalha():
    print(term.bold_white("##"+"-"*25+"##"))
def linhas_jogo():
    print(term.bold_white("xX"+"="*40+"Xx"))

def draw_window(term, x, y, width, height, title='', text_content='', bg_color='default'):
    if bg_color == 'default':
        bg_style = ''
    else:
        bg_style = getattr(term, f'on_{bg_color}', '')
    border_style = bg_style + term.white_on_default 
    title_style = bg_style + term.bold_on_default
    text_style = bg_style + term.on_default
    with term.location(x, y):
        print(border_style + '╔' + '═' * (width - 2) + '╗' + term.normal)
    for i in range(1, height - 1):
        with term.location(x, y + i):
            print(text_style + '║' + ' ' * (width - 2) + '║' + term.normal)
    with term.location(x, y + height - 1):
        print(border_style + '╚' + '═' * (width - 2) + '╝' + term.normal)
    if title:
        title_x = x + (width - len(title)) // 2
        with term.location(title_x, y):
            print(title_style + ' ' + title + ' ' + term.normal)
    if text_content:
        lines = text_content.split('\n')
        for i, line in enumerate(lines):
            if i < height - 2:
                with term.location(x + 2, y + i + 1):
                    print(text_style + line[:width - 4] + term.normal)

class Cores:
    PRETO = '\033[30m'
    VERMELHO = '\033[31m'
    VERDE = '\033[32m'
    AMARELO = '\033[33m'
    AZUL = '\033[34m'
    MAGENTA = '\033[35m'
    CIANO = '\033[36m'
    CINZA_CLARO = '\033[37m'
    CINZA_ESCURO = '\033[90m'
    VERMELHO_CLARO = '\033[91m'
    FUNDO_PRETO = '\033[40m'
    FUNDO_VERDE = '\033[42m'
    FUNDO_BRANCO = '\033[47m'
    FUNDO_MARROM = '\033[48;5;94m'
    CLEAR = '\033[H\033[J'
    RESET = '\033[0m'
    BRILHO = '\033[1m'
    INVERTER = '\033[7m'
C = Cores

class art_ascii:
    def __init__(self):
        self.suny = r"""    \|/            \|/
    /v\   (    )   /v\
   /v v\  |\^^/|  /v v\
  /v/v\v\_(@::@)_/v/v\v\
 /v/v v\v  \\//  v/v v\v\
(v v v v v (oo) v v v v v)
 \v /V\ v v/  \v v /V\ v/
  \/   \ v/    \v /   \/
        \/      \/
"""
        self.inferno_2 = r"""
          __ _
        .'  Y '>,
        / _   _  \
        )(_) (_)(|}
        {  4A   } /
        \uLuJJ/\l
        |3    p)/
        /nnm_n//
        \_>-<_/D
"""
        self.inferno = r"""              (_)L|J
       )      (") |     (
       ,(. A `/ \-|   (,`)
      )' (' \/\ / |  ) (.
     (' ),).  _W_ | (,)' )
    ^^^^^^^^^^^^^^^^^^^^^^^"""
        self.musumano = r"""  |
  |
  + \
  \\.G_.*=.
   `(#'/.\|
    .>' (_--.
 _=/d   ,^\
~~ \)-'   '
   / |   
  '  '
"""
        self.cidade_em_caos = r"""                         (=)          =_=_=
        y               (___)    =_=_= |=| =_=_=
       /`'                        |=|  |=|  |=|
       \ O ,                      |=|__|=|__|=|
        |,/(\   /                 |    __     |
  -`___-\  |` ./O                 |   |  |    |
  ''-(  /`--) `\/\   .=.=.=.=.=.=.|___|__|____|
      7/`       /|    .=.=.=..=.=.=.=.=.=.=.=.==
      \\       /  \     =.=.=.==..==.=.=.=.=.=.="""
        self.cidade_em_caos2 = r""" _      xxxx      _
/_;-.__ / _\  _.-;_\
   `-._`'`_/'`.-'
       `\   /`
        |  /
       /-.(
       \_._\
        \ \`;
         > |/
        / //
        |//
        \(\
         ``"""
        self.titulo = f"""
{C.AMARELO+C.BRILHO}                            ╔╦╗┬ ┬┌─┐ 
{C.AMARELO+C.BRILHO}                             ║ ├─┤├┤  
{C.AMARELO+C.BRILHO}                             ╩ ┴ ┴└─┘
{C.CINZA_CLARO+C.BRILHO}                            ╦╔═┬┌┐┌┌─┐
{C.CINZA_CLARO+C.BRILHO}                            ╠╩╗│││││ ┬
{C.CINZA_CLARO+C.BRILHO}                            ╩ ╩┴┘└┘└─┘
"""
        self.necro = r""" (\.   \      ,/)
  \(   |\     )/
  //\  | \   /\\
 (/ /\_#oo#_/\ \)
  \/\__####__/\/
       \##/
       /##\
      /####\
      \~~~~/
.,.,.,,.,,.,.,.,..,,.,.
"""
        self.mago = r"""         ,/   *
      _,'/_   |
      `(")' ,'/
   _ _,-H-./ /
   \_\_\.   /
     )" |  (
  __/   H   \__
  \    /|\    /
   `--'|||`--'
      ==^=="""
        self.esqueleto = r"""        .-.
       (o.o)
        |=|
       __|__
     //.=|=.\\
    // .=|=. \\
    \\ .=|=. //
     \\(_=_)//
      (:| |:)
       || ||
       () ()
       || ||
       || ||
      ==' '==
"""
        self.demoni0 = r'''   ,    ,    /\   /\
  /( /\ )\  _\ \_/ /_
  |\_||_/| < \_   _/ >
  \______/  \|0   0|/
    _\/_   _(_  ^  _)_
   ( () ) /`\|V"""V|/`\
     {}   \  \_____/  /
     ()   /\   )=(   /\
     {}  /  \_/\=/\_/  \ 
'''
        self.demoni1 = r"""            v
      (__)v | v
      /\/\\_|_/
     _\__/  |
    /  \/`\<`)
    \ (  |\_/
   /)))-(  |
  / /^ ^ \ |
 /  )^/\^( |
 )_//`__>> |
   #   #`  | 
"""
        self.vila1 = r"""          _        (0)
         /=\      (___)
        /===\  /\
###     |   | /==\   {0}
####    |[] | |[]|    |
==========================
"""
        self.farol = r""" . _  .    .__  .  .  __,--'                 
  (_)    ' /__\ __,--'                       
'  .  ' . '| o|'                             
          [IIII]`--.__                       
           |  |       `--.__                 
           | :|             `--.__           
           |  |                   `--.__     
._,,.-,.__.'__`.___.,.,.-..,_.,.,.,-._..`--..
"""
        self.guerriro = r"""                 /
          ,~~   /
      _  <=)  _/_
     /I\.="==.{>
     \I/-\T/-'
         /_\
        // \\_
       _I    / 
============================
"""
        self.lobo = r"""
             _/|
            =/_/
           _/ |
      (   /  ,|
       \_/^\/||__
    _/~  `""~`"` \_
 __/  -'/  `-._ `\_\__
/     /-'`  `\   \  \-.\
"""
        self.lobo1 = r"""
         _     ___
        #_~`--'__ `===-,
        `.`.     `#.,//
        ,_\_\     ## #\
        `__.__    `####\
             ~~\ ,###'~
                \##'
"""

art = art_ascii()

class mini_mapa_:
    def __init__(self):
        self.castelo = r'''
                            #################
 ##############             #....|V...M|....#
 #......@.....#             #....=======....#
 #............#             #...............#                    ############################
 #............#             #...............#                    #..........................#
 #............#             #######.#########                    #.#######################..#
 #............#                   #.#                            #.#                     #..#
 ############/#                   #.#                            #.#                     #..#
            #.#                   #.#                            #.#                     #..#
            #.#                   #.#                            #.#            ##########..#######
            #.#                   #.#                #############/###          #.................#
    #########.#####################/##################...............#          #.................#
    #................................................................#          #......###/###....#
    #/#####.......####################################...............#          #......# #.# #....#
    #.#   #.......#                                  #..########.....#          #......# #.# #....#
    #.#   #.......#############                      #..#      #.....#          #......# #.# #....#
    #.#   #...................#                      #..#      #.....#          #......# #.# #....#
    #.#   #...................#                      #..#      #.....#          #......# #.# #....#
    #.#   #########...........#                      #..##\#####.....#          #......# #.# #....#
    #.#           #...........#############          #...............#          ######## #.# ######
 ####.##########  #.......................#          #...............#                   #.#
 #.............#  #.......................#          #################   #################.#######
 #.............#  #############...........#                              #.......................#
 #.............#              #...........#                              #.......................#
 #.............#              #...........#                              #.......................#
 #.............#              #...........#                              #.......................#
 ###############              #############                              #.......................#
                                                                         #.......................#
                                                                         #########################

'''
class dialogos:
    def __init__(self):
        self.casa_1 = f"""Saia daqui seu forasteiro"""
        self.casa_2 = """Não aceitamos forasteiros
por essas terras"""