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
import glob

def limpar_todos_os_saves():
    for save_file in glob.glob("save_mapa_*.json"):
        try:
            os.remove(save_file)
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todos_os_saves_p():
    for save_file in glob.glob("demo.json"):
        try:
            os.remove(save_file)
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def serializar_para_json(obj):
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, tuple):
        return list(obj)
    elif isinstance(obj, dict):
        return {k: serializar_para_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serializar_para_json(v) for v in obj]
    else:
        return obj

def salvar_mapa_estado(filename, mapa_id, estado_mapa):
    try:
        with open(filename, 'w', encoding='utf-8') as f: 
            json.dump(serializar_para_json({
                "mapa_id": mapa_id,
                "mapa_art": estado_mapa["mapa_art"],
                "inimigos_derrotados": estado_mapa["inimigos_derrotados"],
                "baus_abertos": estado_mapa["baus_abertos"],
                "interacoes": estado_mapa.get("interacoes", {}),
                "obstaculos": estado_mapa["obstaculos"],
                "cores": estado_mapa.get("cores", {}),
                "caracteres_aleatorios": estado_mapa.get("caracteres_aleatorios", []),
                "chaves_pegas": estado_mapa["chaves_pegas"],
                "abrir_porta": estado_mapa["abrir_porta"],
            }), f, indent=4)
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

def salvar_jogo_global(player, ESTADO_MAPAS, filename="save_global.json"):
    try:
        inventario_nomes = [item.nome for item in player.inventario]
        equipa_nomes = {slot: item.nome if item else None for slot, item in player.equipa.items()}

        player_data = {
            "nome": player.nome,
            "hp_max": player.hp_max,
            "hp": player.hp,
            "atk": player.atk,
            "niv": player.niv,
            "xp_max": player.xp_max,
            "defesa": player.defesa,
            "gold": player.gold,
            "stm_max": player.stm_max,
            "stm": player.stm,
            "intt": player.intt,
            "mn_max": player.mana_max,
            "mana": player.mana,
            "d_m": player.dano_magico,
            "xp": player.xp,
            "aleatorio": player.aleatorio,
            "inventario": inventario_nomes,
            "mana_lit": player.mana_lit,
            "equipa": equipa_nomes,
            "itens_coletaodos": player.itens_coletaodos,
            "rodar": player.rodar_jogo,
            "classes": player.classe,
            "pos_x": player.x_mapa,
            "pos_y": player.y_mapa,
            "mapa_atual": player.mapa_atual,
            "char_skin": player.skin,
            "art_player_nome": player.skin_nome,
        }

        # Serializa todos os mapas
        mapas_serializados = {}
        for mapa_id, estado in ESTADO_MAPAS.items():
            mapas_serializados[mapa_id] = serializar_para_json({
                "mapa_art": estado["mapa_art"],
                "inimigos_derrotados": estado["inimigos_derrotados"],
                "baus_abertos": estado["baus_abertos"],
                "interacoes": estado.get("interacoes", {}),
                "obstaculos": estado["obstaculos"],
                "cores": estado.get("cores", {}),
                "caracteres_aleatorios": estado.get("caracteres_aleatorios", []),
                "chaves_pegas": estado["chaves_pegas"],
                "abrir_porta": estado["abrir_porta"],
            })

        save_data = {
            "player": player_data,
            "mapas": mapas_serializados
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=4)

        print(f"✅ Jogo global salvo com sucesso em '{filename}'")

    except Exception as e:
        print(f"❌ Erro ao salvar jogo global: {e}")

def carregar_jogo_global(filename="save_global.json"):
    if not os.path.exists(filename):
        print(f"❌ Nenhum save global encontrado em '{filename}'")
        return None, {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            save_data = json.load(f)

        # --- PLAYER ---
        player_data = save_data["player"]
        SKIN_MAP = {
            "necro": ascii.necro,
            "guerreiro": ascii.guerriro,
            "mago": ascii.mago
        }
        skin_nome_carregado = player_data.get("art_player_nome")
        skin_arte_carregada = SKIN_MAP.get(skin_nome_carregado) or None

        player = jogador(
            nome=player_data["nome"],
            hp_max=player_data["hp_max"],
            atk=player_data["atk"],
            niv=player_data["niv"],
            xp_max=player_data["xp_max"],
            defesa=player_data["defesa"],
            gold=player_data["gold"],
            stm_max=player_data["stm_max"],
            intt=player_data["intt"],
            mn_max=player_data["mn_max"],
            d_m=player_data["d_m"],
            art_player=skin_arte_carregada,
            skin=player_data.get("char_skin", "@"),
            skin_nome=skin_nome_carregado,
        )

        player.hp = player_data["hp"]
        player.mana = player_data["mana"]
        player.xp = player_data["xp"]
        player.stm = player_data["stm"]
        player.x_mapa = player_data["pos_x"]
        player.y_mapa = player_data["pos_y"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None for slot, n in player_data.get("equipa", {}).items()}
        player.mana_lit = player_data.get("mana_lit", [])
        player.itens_coletaodos = player_data.get("itens_coletaodos", {})
        player.rodar_jogo = player_data["rodar"]
        player.classe = player_data["classes"]

        # --- MAPAS ---
        mapas_carregados = {}
        for mapa_id, estado in save_data.get("mapas", {}).items():
            mapas_carregados[mapa_id] = {
                "mapa_art": estado["mapa_art"],
                "inimigos_derrotados": set(tuple(p) for p in estado["inimigos_derrotados"]),
                "baus_abertos": set(tuple(p) for p in estado["baus_abertos"]),
                "interacoes": estado.get("interacoes", {}),
                "obstaculos": estado["obstaculos"],
                "cores": estado.get("cores", {}),
                "explorado": set(tuple(p) for p in estado.get("explorado", [])),
                "caracteres_aleatorios": estado.get("caracteres_aleatorios", []),
                "chaves_pegas": set(tuple(p) for p in estado["chaves_pegas"]),
                "abrir_porta": set(tuple(p) for p in estado["abrir_porta"]),
            }

        print(f"✅ Save global carregado com sucesso de '{filename}'")
        return player, mapas_carregados

    except Exception as e:
        print(f"❌ Erro ao carregar save global: {e}")
        return None, {}

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

def mover_inimigos_para_jogador(mapa_art, player, obstaculos, inimigo_chars, estado_mapa, raio_visao=int):
    altura = len(mapa_art)
    largura = len(mapa_art[0])
    destino = (player.x_mapa, player.y_mapa)
    
    if "fundo_inimigos" not in estado_mapa:
        estado_mapa["fundo_inimigos"] = {}
    fundo_inimigos = estado_mapa["fundo_inimigos"]
    inimigos = []

    for y, linha in enumerate(mapa_art):
        for x, ch in enumerate(linha):
            if ch in inimigo_chars:
                inimigos.append((x, y, ch))

    for inimigo_x, inimigo_y, inimigo_tipo in inimigos:
        dx = player.x_mapa - inimigo_x
        dy = player.y_mapa - inimigo_y
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > raio_visao:
            continue
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
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
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
    mapa_nome=None,ESTADO_GLOBAL_LOAD=None 
):

    ESTADO_MAPAS = ESTADO_GLOBAL_LOAD if ESTADO_GLOBAL_LOAD is not None else {}
    
    mapa_id = mapa_nome or id(mapas_)
    if mapa_nome:
        player.mapa_atual = mapa_nome

    estado_carregado = ESTADO_MAPAS.get(mapa_id)
    
    if estado_carregado is None:
        save_filename = f"save_mapa_{mapa_id}.json"
        estado_carregado = carregar_mapa_estado(save_filename)

    if estado_carregado:
        ESTADO_MAPAS[mapa_id] = {
            "mapa_art": estado_carregado["mapa_art"],
            "inimigos_derrotados": set(tuple(pos) for pos in estado_carregado["inimigos_derrotados"]),
            "baus_abertos": set(tuple(pos) for pos in estado_carregado["baus_abertos"]),
            "interacoes": estado_carregado.get("interacoes", {}),
            "obstaculos": estado_carregado["obstaculos"],
            "cores": estado_carregado.get("cores", {}),
            "caracteres_aleatorios": estado_carregado.get("caracteres_aleatorios", []),
            "chaves_pegas": set(tuple(pos) for pos in estado_carregado["chaves_pegas"]),
            "abrir_porta": set(tuple(pos) for pos in estado_carregado["abrir_porta"])
        }

        mapa_art = ESTADO_MAPAS[mapa_id]["mapa_art"]
        max_width = max(len(l) for l in mapa_art)

    else:
        raw_map_lines = mapas_
        max_width = max(len(l) for l in raw_map_lines if l.strip())
        mapa_art = [l.ljust(max_width) for l in raw_map_lines if l.strip()]

        ESTADO_MAPAS[mapa_id] = {
            "mapa_art": mapa_art,
            "inimigos_derrotados": set(),
            "baus_abertos": set(),
            "interacoes": {},
            "obstaculos": obstaculos_custom or set(),
            "cores": cores_custom or {},
            "caracteres_aleatorios": [],
            "chaves_pegas": set(),
            "abrir_porta": set(),
        }



    player.x_mapa = x_p
    player.y_mapa = y_p
    OBSTACULOS = obstaculos_custom or ESTADO_MAPAS[mapa_id]["obstaculos"]
    INTERACOES = interacoes_custom or {}
    CORES_DO_ESTADO = ESTADO_MAPAS[mapa_id].get("cores", {})
    if CORES_DO_ESTADO is None:
        CORES_DO_ESTADO = {}

    CORES = cores_custom or CORES_DO_ESTADO
    
    if CORES is None:
        CORES = {}

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
        inimigo_chars = []
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

        def chave(pos_chave):
            if pos_chave in ESTADO_MAPAS[mapa_id]["chaves_pegas"]:
                return
            ESTADO_MAPAS[mapa_id]["chaves_pegas"].add(pos_chave)

            chave_item = TODOS_OS_ITENS.get('Chave')
            if chave_item:
                player.inventario.append(chave_item)
            else:
                print("Item 'Chave' não encontrado em TODOS_OS_ITENS.")
                return

            with term.location(x=x_l+CAMERA_WIDTH+6, y=CAMERA_HEIGHT-2):
                print("Você Encontrou uma Chave")

            bx, by = pos_chave
            linha_antiga = mapa_art[by]
            mapa_art[by] = linha_antiga[:bx] + '.' + linha_antiga[bx + 1:]

            ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        def abrir_portas(pos_porta):
            if pos_porta in ESTADO_MAPAS[mapa_id]["abrir_porta"]:
                return

            possui_chave = any(item.nome == 'Chave' for item in player.inventario)
            if possui_chave:
                ESTADO_MAPAS[mapa_id]["abrir_porta"].add(pos_porta)
                bx, by = pos_porta
                linha_antiga = mapa_art[by]
                mapa_art[by] = linha_antiga[:bx] + '\\' + linha_antiga[bx + 1:]

                for i, item in enumerate(player.inventario):
                    if item.nome == 'Chave':
                        del player.inventario[i]
                        break

                ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            else:
                with term.location(x=x_l+CAMERA_WIDTH+6, y=CAMERA_HEIGHT-2):
                    print("Você precisa de uma chave para abrir esta porta.")

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

        draw_window(term, x=x_l + CAMERA_WIDTH + 5, y=y_l, width=CAMERA_WIDTH + 5, height=CAMERA_HEIGHT + 2, text_content=menager)
        player.barra_de_vida(x_l + CAMERA_WIDTH + 6, y_l=CAMERA_HEIGHT-14)

        for j, linha in enumerate(mapa_art[camera_y:camera_y + CAMERA_HEIGHT]):
            for i, ch in enumerate(linha[camera_x:camera_x + CAMERA_WIDTH]):
                mapa_x = camera_x + i
                mapa_y = camera_y + j

                cor = CORES.get(ch, "")
                with term.location(x_l + 2 + i, y_l + 1 + j):
                    print(cor + ch + C.RESET, end="")

        with term.location(x_l + 2 + player.x_mapa - camera_x, y_l + 1 + player.y_mapa - camera_y):
            print(term.bold_yellow(player.skin) + term.normal)
            
        def verificar_proximidade_cruz(x, y):
            direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            proximidades = []
            for dx, dy in direcoes:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    ch = mapa_art[ny][nx]
                    proximidades.append((nx, ny, ch))
            return proximidades
        proximos = verificar_proximidade_cruz(player.x_mapa, player.y_mapa)

        for px, py, ch in proximos:
            if ch == "B":
                if (px, py) not in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                    bau((px, py))
                    break
            elif ch in ("G", "F"):
                if (px, py) not in ESTADO_MAPAS[mapa_id]["inimigos_derrotados"]:
                    inimigo_move((px, py))
                    break
            elif ch == 'K':
                if (px, py) not in ESTADO_MAPAS[mapa_id]["chaves_pegas"]:
                    chave((px, py))
                    break
            if ch == '/':
                if (px, py) not in ESTADO_MAPAS[mapa_id]["abrir_porta"]:
                    abrir_portas((px, py))
                    break
            
            elif ch == 'M':
                player.aprender_magias(term ,x_menu=x_l + CAMERA_WIDTH + 5, y_menu=y_l, wend=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT)
            elif ch == 'V':
                player.gerenciar_loja(x=0, y=0, largura=30)
            
        if mapas_ == mapas.inicil.split('\n'):
            if player.x_mapa == 28 and player.y_mapa == 5:
                obs = {'#', 'G', 'F', '/', 'B',}
                cur = {'#':term.gray, 'G':term.red, 'F':term.green, '\\':term.brown, 'B':term.bold_brown}
                mini_mapa(
x_l=0,
y_l=0,
player=player,
ascii=ascii,
mapas_=mapas.castelo.split('\n'),
camera_w=35,
camera_h=15,
x_p=3,
y_p=3,
menager="",
mapa_nome='Castelo de Argos',
obstaculos_custom=obs,
cores_custom=cur 
                )
                
        elif mapas_ == mapas.castelo.split("\n"):
            adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'G':5, 'F':5, "B":3})
            obstaculos_inimigo = ['#','\\', 'G', 'F', 'B', f'{player.skin}', 'V', 'M', '/']
            inimigo_chars = ["F","G"]
            mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=5)
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            if player.x_mapa == 17 and player.y_mapa == 11:
                obs = {'#', 'G', 'F', '/', 'B',}
                cur = {'#':term.gray, 'G':term.red, 'F':term.green, '\\':term.brown, 'B':term.bold_brown}
                mini_mapa(
x_l=0,
y_l=0,
player=player,
ascii=ascii,
mapas_=mapas.castelo_1.split('\n'),
camera_w=35,
camera_h=15,
x_p=75,
y_p=20,
menager="",
mapa_nome='Castelo de Argos 2',
obstaculos_custom=obs,
cores_custom=cur )
 
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
                player.up(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT + 2, x_i = 1)
            elif movi == "q" and mapa_anterior:
                exit()
            elif movi == "save":
                salvar_jogo_global(player, ESTADO_MAPAS)
                feedback_message = "Jogo salvo com sucesso."
            else:
                feedback_message = f"Comando '{movi}' inválido. Use w/a/s/d/inventario/up/q."

