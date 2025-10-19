from classe_do_jogador import jogador
from classe_do_inimigo import inimigo
from collections import deque
import time, random, os, json
from batalha import batalha, batalha_cut, seleção_inimigo
from classe_arts import draw_window,term, clear, art_ascii, Cores, mini_mapa_, dialogos, clear_region_a
from mm import tocar_musica, escolher_e_tocar_musica, parar_musica, tocando_musica
from classe_do_inventario import TODOS_OS_ITENS, Item
##ARQUIVO DO MAPA
mapas = mini_mapa_()
dialogo = dialogos()
ascii = art_ascii()
C = Cores()
player = jogador(nome="", hp_max=100, atk=10, niv=1, xp_max=100, defesa=100, gold=11110, stm_max=100, intt=10, mn_max=100,d_m=20, art_player=ascii.necro, skin="@", skin_nome='')
def salvar_mapa_estado(filename, mapa_id, estado_mapa):
    try:
        with open(filename, 'w', encoding='utf-8') as f: 
            json.dump({
                "mapa_id": mapa_id,
                "mapa_art": estado_mapa["mapa_art"],
                "inimigos_derrotados": list(estado_mapa["inimigos_derrotados"]),
                "baus_abertos": list(estado_mapa["baus_abertos"]),
                "interacoes": estado_mapa.get("interacoes", {}),
                "obstaculos": estado_mapa["obstaculos"],
                "cores": estado_mapa.get("cores", {}),
                "explorado": list(estado_mapa["explorado"]),
                "caracteres_aleatorios": estado_mapa.get("caracteres_aleatorios", [])

            }, f, indent=4)
    except IOError as e:
        pass

def carregar_mapa_estado(filename):
    if not os.path.exists(filename): 
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar estado do mapa: {e}") 
        return None

def adicionar_caracteres_aleatorios(mapa_id, estado_mapa, caracteres_quantidades, seed=None):
    if "caracteres_aleatorios" in estado_mapa:
        return 
    if seed is not None:
        random.seed(seed)

    mapa_art = estado_mapa["mapa_art"]
    altura = len(mapa_art)
    largura = len(mapa_art[0])
    posicoes_validas = [
        (x, y)
        for y in range(altura)
        for x in range(largura)
        if mapa_art[y][x] == '.'
    ]
    random.shuffle(posicoes_validas)
    total_caracteres = sum(caracteres_quantidades.values())
    if total_caracteres > len(posicoes_validas):
        total_caracteres = len(posicoes_validas)  
        print("")

    caracteres_colocados = []
    pos_index = 0

    for char, qtd in caracteres_quantidades.items():
        for _ in range(qtd):
            if pos_index >= len(posicoes_validas):
                break
            x, y = posicoes_validas[pos_index]
            pos_index += 1

            linha_antiga = mapa_art[y]
            mapa_art[y] = linha_antiga[:x] + char + linha_antiga[x+1:]

            caracteres_colocados.append((x, y, char))

    estado_mapa["caracteres_aleatorios"] = caracteres_colocados

from collections import deque

def mover_inimigos_para_jogador(mapa_art, player, obstaculos, inimigo_chars, estado_mapa):
    altura = len(mapa_art)
    largura = len(mapa_art[0])
    destino = (player.x_mapa, player.y_mapa)
    if "fundo_inimigos" not in estado_mapa:
        estado_mapa["fundo_inimigos"] = {}
    fundo_inimigos = estado_mapa["fundo_inimigos"]
    inimigos = []

    # Coleta todos os inimigos no mapa
    for y, linha in enumerate(mapa_art):
        for x, ch in enumerate(linha):
            if ch in inimigo_chars:
                inimigos.append((x, y, ch))

    for inimigo_x, inimigo_y, inimigo_tipo in inimigos:
        visitados = set()
        fila = deque()
        fila.append(((inimigo_x, inimigo_y), []))
        caminho_encontrado = None

        while fila:
            (x, y), caminho = fila.popleft()
            if (x, y) in visitados:
                continue
            visitados.add((x, y))
            if (x, y) == destino:
                caminho_encontrado = caminho
                break
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < largura and 0 <= ny < altura and (nx, ny) not in visitados:
                    ch = mapa_art[ny][nx]
                    if (nx, ny) == destino or (ch not in obstaculos and ch not in inimigo_chars):
                        fila.append(((nx, ny), caminho + [(nx, ny)]))
        if caminho_encontrado and len(caminho_encontrado) > 0:
            proximo_x, proximo_y = caminho_encontrado[0]
            if (proximo_x, proximo_y) == destino:
                continue
            if mapa_art[proximo_y][proximo_x] not in inimigo_chars:
                fundo_char = fundo_inimigos.get((inimigo_x, inimigo_y), '.')
                mapa_art[inimigo_y] = mapa_art[inimigo_y][:inimigo_x] + fundo_char + mapa_art[inimigo_y][inimigo_x + 1:]
                fundo_inimigos[(proximo_x, proximo_y)] = mapa_art[proximo_y][proximo_x]
                mapa_art[proximo_y] = mapa_art[proximo_y][:proximo_x] + inimigo_tipo + mapa_art[proximo_y][proximo_x + 1:]

def mini_mapa(
    x_l, y_l, player, ascii, mapas_, camera_w, camera_h, x_p, y_p, menager,
    cores_custom=None, obstaculos_custom=None, mapa_anterior=None, interacoes_custom=None,   
    mapa_nome=None
):
    ESTADO_MAPAS = {}

    mapa_id = mapa_nome or id(mapas_)
    if mapa_nome:
        player.mapa_atual = mapa_nome

    save_filename = f"save_mapa_{mapa_id}.json"

    estado_carregado = carregar_mapa_estado(save_filename)
    if estado_carregado:
        mapa_art = estado_carregado["mapa_art"]
        max_width = max(len(linha) for linha in mapa_art)
    
    if estado_carregado:
        ESTADO_MAPAS[mapa_id] = {
        "mapa_art": estado_carregado["mapa_art"],
        "inimigos_derrotados": set(tuple(pos) for pos in estado_carregado["inimigos_derrotados"]),
        "baus_abertos": set(tuple(pos) for pos in estado_carregado["baus_abertos"]),
        "interacoes": estado_carregado.get("interacoes", {}),
        "obstaculos": estado_carregado["obstaculos"],
        "cores": estado_carregado.get("cores", {}),
        "explorado": set(tuple(pos) for pos in estado_carregado.get("explorado", [])),
        "caracteres_aleatorios": estado_carregado.get("caracteres_aleatorios", [])
    }
    else:
        raw_map_lines = mapas_
        max_width = max(len(l) for l in raw_map_lines if l.strip())
        mapa_art = [l.ljust(max_width) for l in raw_map_lines if l.strip()]

        ESTADO_MAPAS[mapa_id] = {
    "mapa_art": mapa_art,
    "inimigos_derrotados": set(),
    "baus_abertos": set(),
    "interacoes": {},
    "obstaculos": obstaculos_custom or ['#','\\', '=', '|', 'G', 'F', 'B', f'{player.skin}'],
    "cores": cores_custom,
    "explorado": set(),
}

    player.x_mapa = x_p
    player.y_mapa = y_p
    OBSTACULOS = obstaculos_custom or ESTADO_MAPAS[mapa_id]["obstaculos"]
    INTERACOES = interacoes_custom or {}
    FOV_RADIUS = 5
    ESCURECIDO_COR = ''

    feedback_message = ""
    MAP_WIDTH = max_width
    MAP_HEIGHT = len(mapa_art)
    CAMERA_WIDTH = camera_w
    CAMERA_HEIGHT = camera_h

    camera_x = max(0, player.x_mapa - CAMERA_WIDTH // 2)
    camera_y = max(0, player.y_mapa - CAMERA_HEIGHT // 2)

    def atualizar_camera():
        nonlocal camera_x, camera_y
        camera_x = max(0, min(MAP_WIDTH - CAMERA_WIDTH, player.x_mapa - CAMERA_WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - CAMERA_HEIGHT, player.y_mapa - CAMERA_HEIGHT // 2))

    while True:
        inimigo_chars = ["F","G"]
        mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=OBSTACULOS, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id])

        def bau(pos_bau):
            if pos_bau in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                return
            ESTADO_MAPAS[mapa_id]["baus_abertos"].add(pos_bau)

            with term.location(x=x_l+CAMERA_WIDTH+6, y=CAMERA_HEIGHT-2):
                print("Você Encontrou um Baú")
            itens = ['Espada', 'Escudo', 'Suco', 'Poção de Cura']
            selec = random.choice(itens)
            with term.location(x=x_l+CAMERA_WIDTH+6, y=CAMERA_HEIGHT-1):
                print(f"Você conseguiu um {selec}")
                player.inventario.append(TODOS_OS_ITENS[f"{selec}"])
            bx, by = pos_bau
            linha_antiga = mapa_art[by]
            mapa_art[by] = linha_antiga[:bx] + '.' + linha_antiga[bx + 1:]
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        def falas(menager):
            clear_region_a(x=x_l + CAMERA_WIDTH + 6, start_y=y_l, end_y=y_l, width=CAMERA_WIDTH + 5)
            draw_window(term, x=x_l + CAMERA_WIDTH + 5, y=y_l, width=CAMERA_WIDTH + 5, height=CAMERA_HEIGHT + 2, text_content=menager)

        def inimigo_move(pos_inimigo):
            inimigo_ = seleção_inimigo(num=1)
            batalha(player_b=player, inimigo_b=inimigo_)
            if inimigo_.hp <= 0:
                ESTADO_MAPAS[mapa_id]["inimigos_derrotados"].add(pos_inimigo)
                ix, iy = pos_inimigo
                linha_antiga = mapa_art[iy]
                mapa_art[iy] = linha_antiga[:ix] + '.' + linha_antiga[ix + 1:]
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        clear()
        atualizar_camera()
        janela_mapa = [
            linha[camera_x:camera_x + CAMERA_WIDTH]
            for linha in mapa_art[camera_y:camera_y + CAMERA_HEIGHT]
        ]
        mini_mapa_render = "\n".join(janela_mapa)
        draw_window(term, x=x_l, y=y_l, width=CAMERA_WIDTH + 4, height=CAMERA_HEIGHT + 2,title=f"{mapa_nome}", text_content=mini_mapa_render)

        CORES = cores_custom or {
            "#": term.bold_gray,
            "/": term.brown,
            "\\": term.bold_brown,
            'B': term.brown,
            'G': term.green,
            'F': term.red
        }

        draw_window(term, x=x_l + CAMERA_WIDTH + 5, y=y_l, width=CAMERA_WIDTH + 5, height=CAMERA_HEIGHT + 2, text_content=menager)
        player.barra_de_vida(x_l + CAMERA_WIDTH + 6, y_l=CAMERA_HEIGHT-14)

        for j, linha in enumerate(mapa_art[camera_y:camera_y + CAMERA_HEIGHT]):
            for i, ch in enumerate(linha[camera_x:camera_x + CAMERA_WIDTH]):
                mapa_x = camera_x + i
                mapa_y = camera_y + j
                dx = mapa_x - player.x_mapa
                dy = mapa_y - player.y_mapa
                distancia = (dx**2 + dy**2)**0.5

                if distancia <= FOV_RADIUS:
                    cor = CORES.get(ch, "")
                    visivel = True
                    ESTADO_MAPAS[mapa_id]["explorado"].add((mapa_x, mapa_y)) 
                else:
                    if (mapa_x, mapa_y) in ESTADO_MAPAS[mapa_id]["explorado"]:
                        cor = CORES.get(ch, "")
                        ch = ch
                    else:
                        cor = ESCURECIDO_COR
                        ch = ' '
                with term.location(x_l + 2 + i, y_l + 1 + j):
                    print(cor + ch + C.RESET, end="")

        with term.location(x_l + 2 + player.x_mapa - camera_x, y_l + 1 + player.y_mapa - camera_y):
            print(term.bold_yellow(player.skin) + term.normal)
            
        def verificar_proximidade(x, y, raio=1):
            proximidades = []
            for dy in range(-raio, raio + 1):
                for dx in range(-raio, raio + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                        ch = mapa_art[ny][nx]
                        proximidades.append((nx, ny, ch))
            return proximidades

        proximos = verificar_proximidade(player.x_mapa, player.y_mapa, raio=1)

        for px, py, ch in proximos:
            if ch == "B":
                if (px, py) not in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                    bau((px, py))
                    break
            elif ch in ("G", "F"):
                if (px, py) not in ESTADO_MAPAS[mapa_id]["inimigos_derrotados"]:
                    inimigo_move((px, py))
                    break

        if mapas_ == mapas.castelo.split("\n"):
            adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'G':10, 'F':5, "B":10})
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
 
        if feedback_message:
            with term.location(0, CAMERA_HEIGHT + y_l + 4):
                print(term.red(feedback_message))
                feedback_message = ""

        with term.location(x=x_l, y=CAMERA_HEIGHT + y_l + 2):
            print(term.clear_eol + "Digite (w/s/a/d [n]:")
        with term.location(x=x_l + 21, y=CAMERA_HEIGHT + y_l + 2):
            entrada = input(">").strip().split()

        if not entrada:
            continue

        try:
            movi = entrada[0].lower()
            quant = int(entrada[1]) if len(entrada) > 1 else 1
        except (ValueError, IndexError):
            quant = 1

        direcoes = {
            "w": (0, -1),
            "s": (0, 1),
            "a": (-1, 0),
            "d": (1, 0),
        }

        if movi in direcoes:
            dx, dy = direcoes[movi]
            for _ in range(quant):
                passo_x = player.x_mapa + dx
                passo_y = player.y_mapa + dy
                if 0 <= passo_x < MAP_WIDTH and 0 <= passo_y < MAP_HEIGHT:
                    caractere = mapa_art[passo_y][passo_x]
                    if caractere not in OBSTACULOS and caractere not in inimigo_chars:
                        player.x_mapa = passo_x
                        player.y_mapa = passo_y
                        if caractere in INTERACOES:
                            INTERACOES[caractere]()
        else:
            if movi == "i":
                player.inventario_(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=0, batalha=False)
            elif movi == "sair":
                exit()
            elif movi == "up":
                player.up(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT + 2)
            elif movi == "q" and mapa_anterior:
                exit()
            elif movi == "save":
                player.save_game()
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                feedback_message = "Jogo salvo com sucesso."
            elif movi == "load":
                estado_carregado = carregar_mapa_estado(save_filename)
                player.load_game()
                if estado_carregado:
                    mapa_art = estado_carregado["mapa_art"]
                    ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
                    ESTADO_MAPAS[mapa_id]["inimigos_derrotados"] = set(estado_carregado["inimigos_derrotados"])
                    ESTADO_MAPAS[mapa_id]["baus_abertos"] = set(estado_carregado["baus_abertos"])
                    ESTADO_MAPAS[mapa_id]["interacoes"] = estado_carregado.get("interacoes", {})
                    ESTADO_MAPAS[mapa_id]["obstaculos"] = estado_carregado["obstaculos"]
                    ESTADO_MAPAS[mapa_id]["cores"] = estado_carregado.get("cores", {})
                    
            else:
                feedback_message = f"Comando '{movi}' inválido. Use w/a/s/d/inventario/up/q."


"""mini_mapa(
x_l=0,
y_l=0,
player=player,
ascii=ascii,
mapas_=mapas.castelo.split('\n'),
camera_w=35,
camera_h=15,
x_p=4,
y_p=2,
menager="",
mapa_nome='castelo')
"""