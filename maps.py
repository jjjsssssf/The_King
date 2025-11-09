from random import *
from classe_arts import draw_window,term, clear, art_ascii, Cores, mini_mapa_, dialogos, clear_region_a
from classe_do_jogador import *

player_b = jogador(nome="", hp_max=100, atk=15, niv=1, xp_max=100, defesa=10, gold=0, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=art.necro, skin=0,skin_nome='')
mapas = mini_mapa_()
def mapa_prai():
    mapa = mapas.praia.split("\n")
    obstaculos = {'#','~','♣','&',"C", '‼','¥', 'o', '0', '1','„','♠', 'x', '$', '∏'} 
    cores = {'#':term.brown, '♣':term.green, '~':term.lightblue_on_darkblue, 'C':term.brown, '.':term.lightgreen,
    '*': term.lightgreen,'‼':term.bold_yellow,'¥':term.darkgreen, 'o': term.bold_ligtgray,
    '0':term.orange, '1':term.green,'„': term.bold_ligtgreen,'♠': term.darkgreen, 'x':term.bold_brown, ',': term.on_brown,
    '$': term.yellow, '∏':term.magenta_on_lightcyan, '=':term.yellow, ';':term_darkgreen}

    return {
        "nome": "Praia",
        "mapa": mapa,
        "obstaculos": obstaculos,
        "cores": cores,

    }

def mapa_vila():
    mapa = mapas.vila.split("\n")
    obstaculos = {'#','~','&','‼','¥','0','P', 'g', '+', '-', 'P', 'M','▀','█','▄', 'O'} 
    cores = {'#':term.brown,'*': term.lightgreen, '-':term.bold_brown,'‼':term.bold_yellow,'¥':term.darkgreen, '0':term.orange,
    '+':term.brown, '&':term.blue, 'P': term.magenta, 'V': term.green, 'M': term.purple, '▀':term.lightgray_on_darkgray,'█':term.darkgray,'▄':term.lightgray_on_darkgray,
    ':': term.bold_white, 'O':term.bold_brown, '░': term.yellow, '=':term.yellow, '~':term.lightblue_on_darkblue}

    return {
        "nome": "Vila",
        "mapa": mapa,
        "obstaculos": obstaculos,
        "cores": cores,

    }

CASAS = [
    [
        '#########........',
        '#:::::::#..‼‼‼‼‼‼',
        '#::::&::#........',
        '#:::::::#........',
        r'##\######........',
    ],
    [
    '########............',
    '#:::::B#..!!!!!!!!!!',
    '#::&:::#..!........!',
    r'#::::::#..\........!',
    '#\\#####..!!!!!!!!!!',
    ],
]
IGREJAS = [
    [
        '...+...',
        '...#...',
        '..#:#..',
        '.#:::#.',
        '#::P::#',
        '#:::::#',
        '#:::::#',
        r'###\### ',
    ]
]
FAZENDAD = [

    [
    '!!!!!!!!!!!!!!!!',
    '!..............!',
    '!..............!',
    '!..............!',
    '!..............!',
    r'!\\!!!!!!!!!!!!!',
    ],
    [
    '.#######.',
    '#:::&:::#',
    '#:::::::#',
    '#B::::::#',
    '#B::::::#',
    r'####\\###'
    ]

]


def colocar_construcao(mapa, estrutura, pos_x, pos_y):
    mapa_altura = len(mapa)
    mapa_largura = len(mapa[0])

    for y, linha in enumerate(estrutura):
        for x, ch in enumerate(linha):
            mapa_y = pos_y + y
            mapa_x = pos_x + x
            if 0 <= mapa_x < mapa_largura and 0 <= mapa_y < mapa_altura:
                mapa[mapa_y][mapa_x] = ch

def colocar_par_fazenda(mapa, item1, item2, distancia, pos_x, pos_y):
    colocar_construcao(mapa, item1, pos_x, pos_y)
    
    largura_item1 = len(item1[0])
    nova_pos_x = pos_x + largura_item1 + distancia
    colocar_construcao(mapa, item2, nova_pos_x, pos_y)

def gerar_mapa_procedural_unido(largura, altura, seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    noise = [[random.random() for _ in range(largura)] for _ in range(altura)]

    def suavizar(matriz, vezes=2):
        temp_matriz = matriz
        for _ in range(vezes):
            nova = [[0.0] * largura for _ in range(altura)]
            for y in range(altura):
                for x in range(largura):
                    vizinhos = []
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < largura and 0 <= ny < altura:
                                vizinhos.append(temp_matriz[ny][nx])
                    nova[y][x] = sum(vizinhos) / len(vizinhos)
            temp_matriz = nova
        return temp_matriz

    noise = suavizar(noise, vezes=3)

    total = largura * altura

    qtd_chao = int(total * 0.70)
    qtd_agua = int(total * 0.05)
    qtd_pedras = int(total * 0.1)
    qtd_carvao = int(total * 0.02)
    qtd_construcoes = int
    qtd_igrejas = int
    qtd_fazendas = int

    noise_flat = [(noise[y][x], x, y) for y in range(altura) for x in range(largura)]
    noise_flat.sort(key=lambda t: t[0])

    mapa = [['.'] * largura for _ in range(altura)]

    player_spawn_x = largura // 2
    player_spawn_y = altura // 2
    zona_segura_x = 10
    zona_segura_y = 5

    idx_atual = 0
    #agua
    qtd_a_preencher = min(qtd_agua, len(noise_flat) - idx_atual)
    for i in range(qtd_a_preencher):
        _, x, y = noise_flat[idx_atual + i]
        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue

        mapa[y][x] = '~'
    idx_atual += qtd_a_preencher

    #arvorea
    candidatos_arvore = noise_flat[-qtd_pedras:]
    restante_para_embaralhar = noise_flat[idx_atual : -qtd_pedras if qtd_pedras > 0 else None]
    random.shuffle(restante_para_embaralhar)
    for _, x, y in candidatos_arvore:
        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue
        mapa[y][x] = '♣'

    candidatos_idx = 0
    #arbusto
    qtd_total_arbusto = min(qtd_carvao, len(restante_para_embaralhar) - candidatos_idx)
    for _ in range(qtd_total_arbusto):
        _, x, y = restante_para_embaralhar[candidatos_idx]
        candidatos_idx += 1

        if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
            continue

        mapa[y][x] = '♠'

    #Estruturas
    if total <= 31250:
        qtd_construcoes = 10
        casas_colocadas = []
        for _ in range(qtd_construcoes):
            casa = random.choice(CASAS)
            altura_casa = len(casa)
            largura_casa = len(casa[0])

            tentativas = 0
            max_tentativas = 100  

            while tentativas < max_tentativas:
                x = random.randint(0, largura - largura_casa - 1)
                y = random.randint(0, altura - altura_casa - 1)
                tentativas += 1

                if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                    continue

                muito_perto = False
                for (cx, cy) in casas_colocadas:
                    if abs(x - cx) < 20 and abs(y - cy) < 10:
                        muito_perto = True
                        break

                if not muito_perto:
                    colocar_construcao(mapa, casa, x, y)
                    casas_colocadas.append((x, y))
                    break

    if total <= 31250:
        igrejas_colocadas = []
        qtd_igrejas = random.randint(1, 3)
        for _ in range(qtd_igrejas):
            igrejas = random.choice(IGREJAS)
            altura_igrejas = len(igrejas)
            largura_igrejas = len(igrejas[0])

            tentativas = 0
            max_tentativas = 100  

            while tentativas < max_tentativas:
                x = random.randint(0, largura - largura_igrejas - 1)
                y = random.randint(0, altura - altura_igrejas - 1)
                tentativas += 1

                if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                    continue

                muito_perto = False
                for (cx, cy) in igrejas_colocadas:
                    if abs(x - cx) < 20 and abs(y - cy) < 10:
                        muito_perto = True
                        break

                if not muito_perto:
                    colocar_construcao(mapa, igrejas, x, y)
                    casas_colocadas.append((x, y))
                    break
    
    if total <= 31250:
        qtd_fazendas = 5
        fazendas_colocada = []
        for _ in range(qtd_fazendas):
            casa_idx = random.randint(0, len(FAZENDAD)-1)
            
            if casa_idx in [0, 1]:
                item1 = FAZENDAD[0]
                item2 = FAZENDAD[1]
                tentativas = 0
                max_tentativas = 100
                while tentativas < max_tentativas:
                    x = random.randint(0, largura - len(item1[0]) - len(item2[0]) - 4)
                    y = random.randint(0, altura - max(len(item1), len(item2)))
                    tentativas += 1

                    if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                        continue

                    muito_perto = False
                    for (cx, cy) in fazendas_colocada:
                        if abs(x - cx) < 20 and abs(y - cy) < 10:
                            muito_perto = True
                            break

                    if not muito_perto:
                        colocar_par_fazenda(mapa, item1, item2, 4, x, y)
                        fazendas_colocada.append((x, y))
                        break
            else:
                # Casas normais
                fazenda = FAZENDAD[fazenda_idx]
                altura_fazenda = len(fazenda)
                largura_fazenda = len(fazenda[0])
                tentativas = 0
                max_tentativas = 100
                while tentativas < max_tentativas:
                    x = random.randint(0, largura - largura_fazenda - 1)
                    y = random.randint(0, altura - altura_fazenda - 1)
                    tentativas += 1

                    if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                        continue

                    muito_perto = False
                    for (cx, cy) in fazendas_colocada:
                        if abs(x - cx) < 20 and abs(y - cy) < 10:
                            muito_perto = True
                            break

                    if not muito_perto:
                        colocar_construcao(mapa, casa, x, y)
                        fazendas_colocada.append((x, y))
                        break


    if mapa[player_spawn_y][player_spawn_x] == '~':
        mapa[player_spawn_y][player_spawn_x] = '.'

    mapa_final = [''.join(linha) for linha in mapa]
    return mapa_final

def mapa_procedural(nome, largura, altura, seed=None):
    mapa = gerar_mapa_procedural_unido(largura=largura, altura=altura, seed=seed)
    player_b.mapa_atual = 'Mundo'
    cores = {
    '#':term.lightsalmon,
    '♣':term.olivedrab2,
    '&':term.blue,
    "C":term.brown,
    '‼':term.yellow2,
    '¥':term.forestgreen,
    'o':term.antiquewhite3,
    '0':term.coral,
    '1':term.brown,
    '*':term.olivedrab,
    '♠':term.springgreen4,
    'x':term.chocolate3,
    '$':term.sandybrown,
    '.':term.lawngreen,
    '\\': term.tan4,
    '~': term.bold_white_on_deepskyblue3,
    ':': term.thistle4,
    '+': term.bold_cornsilk3,
    '=': term.lightsalmon3,
    'I': term.rosybrown2,
    'N': term.sienna,
    'G': term.red,
    'F': term.magenta,
    ',': term.bold_white_on_rosybrown2,
    '!': term.lightsalmon
    }
    obstaculos = set([
        '#', '♣', '&', "C", '‼', '¥', 'o', '0', '1', '„', '♠', 'x', '$', '+', 'P', 'N', 'I', 'G', 'F', '!'
    ])

    return {
        "mapa": mapa,
        "cores": cores,
        "obstaculos": obstaculos,
        "nome": nome
    }

def gerar_caverna(largura, altura, player_b, seed=None):
    if seed is not None:
        random.seed(seed)
    else:
        random.seed()

    player_x = player_b.x_mapa
    player_y = player_b.y_mapa

    # Cria mapa cheio de pedra
    mapa = [['o' for _ in range(largura)] for _ in range(altura)]

    # Posição inicial
    x, y = player_x, player_y
    mapa[y][x] = '.'

    num_tuneis = 100
    comprimento_tunel = 40
    direcoes = [(0,1), (1,0), (0,-1), (-1,0)]

    for _ in range(num_tuneis):
        dx, dy = random.choice(direcoes)
        for _ in range(random.randint(5, comprimento_tunel)):
            x += dx
            y += dy

            if x < 1 or x >= largura-1 or y < 1 or y >= altura-1:
                break
            mapa[y][x] = '.'

            # 🔹 Chance de abrir uma sala ao redor
            if random.random() < 0.05:
                for dy2 in range(-2, 3):
                    for dx2 in range(-2, 3):
                        if 0 < y+dy2 < altura and 0 < x+dx2 < largura:
                            mapa[y+dy2][x+dx2] = '.'

            # Pequena chance de mudar de direção
            if random.random() < 0.2:
                dx, dy = random.choice(direcoes)

    total = largura * altura
    qtd_ferro = int(total * 0.03)
    qtd_carvao = int(total * 0.05)
    qtd_esqueleto = int(total * 0.0002)
    qtd_zumbi = int(total * 0.0001)

    pos_pedras = [(x, y) for y in range(altura) for x in range(largura) if mapa[y][x] == 'o']
    pos_terra = [(x, y) for y in range(altura) for x in range(largura) if mapa[y][x] == '.']
    random.shuffle(pos_pedras)

    # Ferro
    if player_b.andar >= 5:
        for i in range(min(qtd_ferro, len(pos_pedras))):
            x, y = pos_pedras[i]
            mapa[y][x] = 'u'
    else:
        pass
    # Carvão
    random.shuffle(pos_pedras)
    colocados = 0
    for x, y in pos_pedras:
        if mapa[y][x] == 'o':
            mapa[y][x] = 'c'
            colocados += 1
            if colocados >= qtd_carvao:
                break

    random.shuffle(pos_terra)
    colocados = 0
    for x, y in pos_terra:
        if mapa[y][x] == '.':
            mapa[y][x] = 'F'
            colocados += 1
            if colocados >= qtd_zumbi:
                break
    colocados = 0
    for x, y in pos_terra:
        if mapa[y][x] == '.':
            mapa[y][x] = 'G'
            colocados += 1
            if colocados >= qtd_esqueleto:
                break

    if player_b.andar == 10:
        direcoes_possiveis = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0),           (1, 0),
            (-1, 1),  (0, 1),  (1, 1),
        ]
        random.shuffle(direcoes_possiveis)
        colocado = False

        for dx, dy in direcoes_possiveis:
            bx, by = player_x + dx, player_y + dy
            if 0 <= bx < largura and 0 <= by < altura and mapa[by][bx] == '.':
                mapa[by][bx] = '@'
                colocado = True
                break

        # Se não conseguiu nas posições próximas, tenta achar outro ponto livre aleatório
        if not colocado:
            for _ in range(1000):
                bx, by = random.randint(1, largura-2), random.randint(1, altura-2)
                if mapa[by][bx] == '.':
                    mapa[by][bx] = '@'
                    break

    mapa_final = [''.join(linha) for linha in mapa]
    return mapa_final

def mapa_caverna(nome, largura, altura, player_b ,seed=None):
    mapa = gerar_caverna(largura=largura, altura=altura, player_b = player_b,seed=seed)
    player_b.mapa_atual = f'Caverna - [{player_b.andar}]'
    cores = {
        'o': term.bold_antiquewhite3,
        'u': term.rosybrown2,
        '.': term.seashell2,
        'c': term.darkslategray,
        '~': term.bold_white_on_deepskyblue3,
        'B': term.sandybrown,
        'F': term.magenta,
        'G': term.red
    }

    obstaculos = set([
        '&', 'o', 'u', 'c'
    ])

    return {
        "mapa": mapa,
        "cores": cores,
        "obstaculos": obstaculos,
        "nome": nome
    }


