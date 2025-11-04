from classe_do_jogador import jogador
from classe_do_inimigo import inimigo
from collections import deque
import time, random, os, json, textwrap
from maps import *
from inimigo_batalha import *
from batalha import *
from classe_arts import draw_window,term, clear, art_ascii, Cores, mini_mapa_, dialogos, clear_region_a
from mm import tocar_musica, escolher_e_tocar_musica, parar_musica, tocando_musica
from classe_do_inventario import TODOS_OS_ITENS, Item
##ARQUIVO DO MAPA
mapas = mini_mapa_()
dialogo = dialogos()
ascii = art_ascii()
C = Cores()
player = jogador(nome="Joojs", hp_max=30, atk=5000, niv=15, xp_max=100, defesa=0, gold=0, stm_max=100, intt=0, mn_max=100,d_m=15,art_player=ascii.necro, skin="@", skin_nome='')
import glob

def limpar_todos_os_saves():
    for save_file in glob.glob("save_mapa_*.json"):
        try:
            os.remove(save_file)
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todas_caverna():
    for save_file in glob.glob("save_mapa_Caverna*.json"):
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

def serializar_para_json(data):
    if isinstance(data, dict):
        novo_dicionario = {}
        for k, v in data.items():
            if isinstance(k, tuple):
                k = f"{k[0]},{k[1]}"
            novo_dicionario[k] = serializar_para_json(v)
        return novo_dicionario
        
    elif isinstance(data, list):
        return [serializar_para_json(item) for item in data]
        
    elif isinstance(data, set):
        return list(data)
    elif hasattr(data, '__class__') and data.__class__.__name__ == 'Item':
        return {
            "__class__": "Item", 
            "nome": data.nome
        }
    
    else:
        return data

def deserializar_do_json(data):
    if isinstance(data, dict) and data.get("__class__") == "Item":
        item_nome = data.get("nome")
        if item_nome and item_nome in TODOS_OS_ITENS:
            return TODOS_OS_ITENS[item_nome]
        else:
            print(f"⚠️ Aviso: Item '{item_nome}' não encontrado em TODOS_OS_ITENS durante o load.")
            return None
    if isinstance(data, dict):
        novo_dicionario = {}
        for k, v in data.items():
            if isinstance(k, str) and ',' in k and all(part.strip().isdigit() for part in k.split(',')):
                try:
                    k = tuple(map(int, k.split(',')))
                except ValueError:
                    pass                     
            novo_dicionario[k] = deserializar_do_json(v)
        return novo_dicionario
        
    elif isinstance(data, list):
        return [deserializar_do_json(item) for item in data]
        
    else:
        return data

def salvar_mapa_estado(filename, mapa_id, estado_mapa):
    try:
        dados_salvar = {
            "mapa_id": mapa_id,
            "mapa_art": estado_mapa["mapa_art"],
            # Campos que são SETs
            "inimigos_derrotados": estado_mapa.get("inimigos_derrotados", set()),
            "baus_abertos": estado_mapa.get("baus_abertos", set()),
            "obstaculos": estado_mapa.get("obstaculos", set()),
            "chaves_pegas": estado_mapa.get("chaves_pegas", set()),
            "abrir_porta": estado_mapa.get("abrir_porta", set()),
            # Campos com chaves de TUPLA
            "cores": estado_mapa.get("cores", {}),
            "plantacoes": estado_mapa.get("plantacoes", {}),
            "regeneracoes": estado_mapa.get("regeneracoes", {}),  # <-- adicionado corretamente
            "interacoes": estado_mapa.get("interacoes", {}),
            "caracteres_aleatorios": estado_mapa.get("caracteres_aleatorios", []),
            "baus_armazenamento": estado_mapa.get("baus_armazenamento", {}),
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializar_para_json(dados_salvar), f, indent=4)

    except IOError as e:
        print(f"Erro ao salvar mapa em {filename}: {e}")

def carregar_mapa_estado(filename):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            dados_carregados = json.load(f)
            estado_deserializado = deserializar_do_json(dados_carregados)
            estado_deserializado["inimigos_derrotados"] = set(estado_deserializado.get("inimigos_derrotados", []))
            estado_deserializado["baus_abertos"] = set(estado_deserializado.get("baus_abertos", []))
            estado_deserializado["obstaculos"] = set(estado_deserializado.get("obstaculos", []))
            estado_deserializado["chaves_pegas"] = set(estado_deserializado.get("chaves_pegas", []))
            estado_deserializado["abrir_porta"] = set(estado_deserializado.get("abrir_porta", [])) 
            for pos_str, lista_itens in baus_armazenamento_carregados.items():
                pos_tuple = pos_str if isinstance(pos_str, tuple) else tuple(map(int, pos_str.strip('()').split(', '))) # Garante que é uma tupla
                baus_finais[pos_tuple] = lista_itens
            estado_deserializado["baus_armazenamento"] = baus_finais           
            if "regeneracoes" not in estado_deserializado:
                estado_deserializado["regeneracoes"] = {}

            return estado_deserializado
    except Exception as e:
        print(f"Erro ao carregar estado do mapa {filename}: {e}")
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
            "pontos": player.ponto,
            "andar": player.andar
        }

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
                "plantacoes": estado.get("plantacoes", {}),
                "regeneracoes": estado.get("regeneracoes", {}), 
                "baus_armazenamento": estado.get("baus_armazenamento", {}),
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
        player.ponto = player_data["pontos"]
        player.andar = player_data["andar"]
        player.x_mapa = player_data["pos_x"]
        player.y_mapa = player_data["pos_y"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None for slot, n in player_data.get("equipa", {}).items()}
        player.mana_lit = player_data.get("mana_lit", [])
        player.itens_coletaodos = player_data.get("itens_coletaodos", {})
        player.rodar_jogo = player_data["rodar"]
        player.classe = player_data["classes"]

        mapas_carregados = {}
        for mapa_id, estado_serializado in save_data.get("mapas", {}).items():
            estado_deserializado = deserializar_do_json(estado_serializado)
            baus_armazenamento_carregados = estado_deserializado.get("baus_armazenamento", {})
            baus_finais = {}
            for pos_str, lista_itens in baus_armazenamento_carregados.items():
                if isinstance(pos_str, str) and pos_str.startswith('(') and pos_str.endswith(')'):
                    try:
                        pos_tuple = tuple(map(int, pos_str.strip('()').split(', ')))
                    except ValueError:
                        pos_tuple = pos_str
                else:
                    pos_tuple = pos_str
                baus_finais[pos_tuple] = lista_itens

            mapas_carregados[mapa_id] = {
                "mapa_art": estado_deserializado["mapa_art"],
                "inimigos_derrotados": set(tuple(p) for p in estado_deserializado.get("inimigos_derrotados", [])),
                "baus_abertos": set(tuple(p) for p in estado_deserializado.get("baus_abertos", [])),
                "interacoes": estado_deserializado.get("interacoes", {}),
                "obstaculos": set(estado_deserializado.get("obstaculos", [])),
                "cores": estado_deserializado.get("cores", {}),
                "plantacoes": estado_deserializado.get("plantacoes", {}),
                "regeneracoes": estado_deserializado.get("regeneracoes", {}),  # <-- adicionado aqui também
                "explorado": set(tuple(p) for p in estado_deserializado.get("explorado", [])),
                "caracteres_aleatorios": estado_deserializado.get("caracteres_aleatorios", []),
                "chaves_pegas": set(tuple(p) for p in estado_deserializado.get("chaves_pegas", [])),
                "abrir_porta": set(tuple(p) for p in estado_deserializado.get("abrir_porta", [])),
                "baus_armazenamento": baus_finais,
            }

        print(f"✅ Save global carregado com sucesso de '{filename}'")
        return player, mapas_carregados

    except Exception as e:
        print(f"❌ Erro ao carregar save global: {e}")
        return None, {}

def adicionar_caracteres_aleatorios(mapa_id, estado_mapa, caracteres_quantidades, seed=None):
    if estado_mapa.get("caracteres_aleatorios"):
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
    total_caracteres = min(total_caracteres, len(posicoes_validas))

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
    estado_mapa["mapa_art"] = mapa_art  # Atualiza o mapa com os novos caracteres

    # Garante persistência
    salvar_mapa_estado(f"save_mapa_{mapa_id}.json", mapa_id, estado_mapa)

from collections import deque

def mapas_aleatorio(player):
    escolha = random.choice(["caverna1", "caverna2"])
    if escolha == "caverna1":
        novo_mapa = mapa_caverna(player)
        x_p = 4
        y_p = 3
    else:
        novo_mapa = mapa_caverna2(player)
        x_p = 14
        y_p = 18
    mini_mapa(
        x_l=0, y_l=0,
        player=player,
        mapas_=novo_mapa["mapa"],
        camera_w=35,
        camera_h=15,
        x_p=x_p,
        y_p=y_p,
        menager="",
        cores_custom=novo_mapa["cores"],
        obstaculos_custom=novo_mapa["obstaculos"],
        mapa_nome=novo_mapa["nome"]
    )

def substituir_caractere(mapa_art, x, y, novo_char):
    if not (0 <= y < len(mapa_art)):
        raise IndexError(f"Linha {y} fora dos limites do mapa.")
    if not (0 <= x < len(mapa_art[y])):
        raise IndexError(f"Coluna {x} fora dos limites da linha {y}.")

    linha_antiga = mapa_art[y]
    mapa_art[y] = linha_antiga[:x] + novo_char + linha_antiga[x + 1:]
    return mapa_art

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
    x_l, y_l, player, mapas_, camera_w, camera_h, x_p, y_p, menager,
    cores_custom=None, obstaculos_custom=None, mapa_anterior=None, interacoes_custom=None, 
    mapa_nome=None, ESTADO_GLOBAL_LOAD=None 
):

    ESTADO_MAPAS = ESTADO_GLOBAL_LOAD if ESTADO_GLOBAL_LOAD is not None else {}
    mapa_id = mapa_nome or id(mapas_)
    if mapa_nome:
        player.mapa_atual = mapa_nome

    estado_carregado = ESTADO_MAPAS.get(mapa_id)
    save_filename = f"save_mapa_{mapa_id}.json"

    if estado_carregado is None:
        estado_carregado = carregar_mapa_estado(save_filename)

    if estado_carregado:
        ESTADO_MAPAS[mapa_id] = {
            "mapa_art": estado_carregado["mapa_art"],
            "inimigos_derrotados": estado_carregado.get("inimigos_derrotados", set()),
            "baus_abertos": estado_carregado.get("baus_abertos", set()),
            "interacoes": estado_carregado.get("interacoes", {}),
            "obstaculos": estado_carregado.get("obstaculos", set()),
            "cores": estado_carregado.get("cores", {}),
            "caracteres_aleatorios": estado_carregado.get("caracteres_aleatorios", []),
            "chaves_pegas": estado_carregado.get("chaves_pegas", set()),
            "abrir_porta": estado_carregado.get("abrir_porta", set()),
            "plantacoes": estado_carregado.get("plantacoes", {}),
            "regeneracoes":estado_carregado.get("regeneracoes", {}),
            "baus_armazenamento": estado_carregado.get("baus_armazenamento", {}),
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
            "plantacoes": {},
            "regeneracoes": {},
            "baus_armazenamento": {}, 
        }

    player.x_mapa = x_p
    player.y_mapa = y_p
    OBSTACULOS = obstaculos_custom or ESTADO_MAPAS[mapa_id]["obstaculos"]
    INTERACOES = interacoes_custom or {}
    CORES_DO_ESTADO = ESTADO_MAPAS[mapa_id].get("cores", {})
    CORES = cores_custom or CORES_DO_ESTADO or {}
    plantacoes_ativas = ESTADO_MAPAS[mapa_id].get("plantacoes", {})
    for (px, py), dados in plantacoes_ativas.items():
        if mapa_art[py][px] in ('*', '='): 
            cor_plantio = dados.get("cor")
            if cor_plantio:
                CORES[(px, py)] = cor_plantio
    interacoes_contagem = {}
    feedback_message = ""
    MAP_WIDTH = max_width
    MAP_HEIGHT = len(mapa_art)
    CAMERA_WIDTH = camera_w
    CAMERA_HEIGHT = camera_h

    if "plantacoes" not in ESTADO_MAPAS[mapa_id]:
        ESTADO_MAPAS[mapa_id]["plantacoes"] = {}

    camera_x = max(0, player.x_mapa - CAMERA_WIDTH // 2)
    camera_y = max(0, player.y_mapa - CAMERA_HEIGHT // 2)

    def atualizar_camera():
        nonlocal camera_x, camera_y
        camera_x = max(0, min(MAP_WIDTH - CAMERA_WIDTH, player.x_mapa - CAMERA_WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - CAMERA_HEIGHT, player.y_mapa - CAMERA_HEIGHT // 2))

    while True:
        px, py = player.x_mapa, player.y_mapa
        caractere_atual = mapa_art[py][px]
        clear()
        regeneracoes = ESTADO_MAPAS[mapa_id].get("regeneracoes", {})
        tempo_atual = time.time()
        for (px, py), dados in list(regeneracoes.items()):
            tempo_passado = tempo_atual - dados["tempo_inicio"]
            tempo_regeneracao = dados.get("tempo_regeneracao", 30)
            if tempo_passado >= tempo_regeneracao:
                substituir_caractere(mapa_art, px, py, '♠')
                del regeneracoes[(px, py)]
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        plantacoes = ESTADO_MAPAS[mapa_id].get("plantacoes", {})
        tempo_atual = time.time()
        for (px, py), dados in list(plantacoes.items()):
            tempo_passado = tempo_atual - dados["tempo_plantio"]
            tempo_crescimento = dados.get("tempo_crescimento", 10)
            tipo = dados.get("item", "desconhecido")

            if tempo_passado >= tempo_crescimento and mapa_art[py][px] in ('*', "1", ','):
                if tipo == "trigo":
                    substituir_caractere(mapa_art, px, py, "‼")
                elif tipo == "milho":
                    substituir_caractere(mapa_art, px, py, "¥")
                elif tipo == 'abobora':
                    substituir_caractere(mapa_art, px, py, '0')
                elif tipo == 'arvore':
                    substituir_caractere(mapa_art, px, py, '♣')
                elif tipo == 'arbusto':
                    substituir_caractere(mapa_art, px, py, '♠')
                elif tipo == 'terra':
                    substituir_caractere(mapa_art, px, py, '.')
                else:
                    substituir_caractere(mapa_art, px, py, "¶")
                
                del plantacoes[(px, py)]
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        inimigo_chars = []
        def bau(pos_bau):
            if pos_bau in ESTADO_MAPAS[mapa_id]["baus_abertos"]:
                return
            ESTADO_MAPAS[mapa_id]["baus_abertos"].add(pos_bau)
            itens = ['Suco', 'Poção de Cura', 'Elixir', 'Moedas']
            selec = random.choice(itens)
            if selec == 'Moedas':
                quantia = (player.niv * 10)
                moedas = f"Você Encontrou um Baú\nVocê conseguiu um {selec}\nquantidade ({quantia})x"
                falas(moedas)
                quantia += player.gold
            else:
                item_ = f"Você Encontrou um Baú\nVocê conseguiu um {selec}"
                falas(item_)
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

        def falas(menager, velocidade=0.03):
            max_width = CAMERA_WIDTH + 3 
            lines = menager.split('\n')
            wrapped_lines = []

            for line in lines:
                wrapped_lines.extend(textwrap.wrap(line, max_width))

            draw_window(
                term,
                x=x_l + CAMERA_WIDTH + 5,
                y=y_l,
                width=CAMERA_WIDTH + 5,
                height=CAMERA_HEIGHT + 2,
                text_content=''
            )

            for i, line in enumerate(wrapped_lines):
                with term.location(x_l + CAMERA_WIDTH + 7, y_l + 1 + i):
                    for char in line:
                        print(char, end='', flush=True)
                        time.sleep(velocidade)

            with term.location(x_l + CAMERA_WIDTH + 7, y_l + CAMERA_HEIGHT):
                input(term.bold_cyan("[Pressione Enter para continuar]"))

        def bau_armazenamento(pos_bau):
            ESTADO = ESTADO_MAPAS[mapa_id]
            baus_armazenamento = ESTADO.setdefault("baus_armazenamento", {})
            bau_inventario = baus_armazenamento.setdefault(pos_bau, [])

            def exibir_telas_bau():
                """Desenha as três janelas: Menu, Baú e Inventário do Jogador."""
                clear()
                
                # --- Desenho do Inventário do Jogador (Esquerda) ---
                conteudo_player = "\n".join(f"{i+1}. {item.nome}" for i, item in enumerate(player.inventario)) or "Inventário vazio."
                draw_window(
                    term, 
                    x=x_l - 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=f"Inventário de {player.nome}",
                    text_content=conteudo_player
                )

                # --- Desenho do Menu (Centro) ---
                menu_texto = term.bold_yellow("[1]") + " Guardar\n" + \
                             term.bold_yellow("[2]") + " Pegar\n" + \
                             term.bold_yellow("[3]") + " Sair"
                draw_window(
                    term, 
                    x=x_l, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=term.bold_cyan("Baú de Armazenamento"),
                    text_content=menu_texto
                )
                
                # --- Desenho do Inventário do Baú (Direita) ---
                conteudo_bau = "\n".join(f"{i+1}. {item.nome}" for i, item in enumerate(bau_inventario)) or "Baú vazio."
                draw_window(
                    term, 
                    x=x_l + 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=term.bold_green("Itens do Baú"),
                    text_content=conteudo_bau
                )

            def processar_transferencia(origem_lista, destino_lista, titulo_escolha):
                """Função auxiliar para gerenciar a transferência de itens (Guardar/Pegar)."""
                if not origem_lista:
                    falas(f"A lista de origem ({titulo_escolha}) está vazia.")
                    return

                clear()
                
                # Exibe a lista de itens para escolha
                itens_enumerados = "\n".join(f"{i+1}. {item.nome}" for i, item in enumerate(origem_lista))
                draw_window(
                    term, 
                    x=x_l, 
                    y=y_l, 
                    width=40, 
                    height=15, 
                    title=titulo_escolha,
                    text_content=itens_enumerados
                )

                with term.location(x=x_l, y=y_l + 16):
                    idx_str = input(term.bold("Digite o número do item (ou C para Cancelar): ")).strip()
                
                if idx_str.upper() == 'C':
                    return
                    
                if idx_str.isdigit():
                    idx = int(idx_str) - 1
                    if 0 <= idx < len(origem_lista):
                        item = origem_lista.pop(idx)
                        destino_lista.append(item)
                        falas(f"{item.nome} foi {'guardado no baú' if destino_lista is bau_inventario else 'pego do baú'}.")
                        salvar_mapa_estado(save_filename, mapa_id, ESTADO)
                    else:
                        falas("Número de item inválido.")
                else:
                    falas("Entrada inválida. Tente novamente.")

            while True:
                exibir_telas_bau()
                
                with term.location(x=x_l, y=y_l + 16):
                    escolha = input(term.bold_cyan("Escolha uma opção: ")).strip()

                if escolha == "1":  # Guardar
                    processar_transferencia(
                        player.inventario, 
                        bau_inventario, 
                        "Escolha o item para guardar no Baú:"
                    )

                elif escolha == "2":  # Pegar
                    processar_transferencia(
                        bau_inventario, 
                        player.inventario, 
                        "Escolha o item para pegar do Baú:"
                    )

                elif escolha == "3":  # Sair
                    break
                    
                else:
                    falas("Opção inválida. Escolha 1, 2 ou 3.")

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
                cor = CORES.get((mapa_x, mapa_y), CORES.get(ch, "")) 
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
            if ch in ["G", "F"]:
                if ch == "G":
                    status = esqueleto(player_b=player, art=ascii)
                    inimigo_b = inimigo(
                        nome=status['nome'],
                        hp_max = status["hp"],
                        atk=status['atk'],
                        niv=status['niv'],
                        xp=status['xp'],
                        defesa=status['defesa'],
                        gold = status['gold'],
                        atk1 = status['atk_1'],
                        atk2= status['atk_2'],
                        art_ascii=status['art']
                    )
                elif ch == "F":
                    status = zumbi(player_b=player, art=ascii)
                    inimigo_b = inimigo(
                        nome=status['nome'],
                        hp_max = status["hp"],
                        atk=status['atk'],
                        niv=status['niv'],
                        xp=status['xp'],
                        defesa=status['defesa'],
                        gold = status['gold'],
                        atk1 = status['atk_1'],
                        atk2= status['atk_2'],
                        art_ascii=status['art']
                    )
                batalha(player_b=player, inimigo_b=inimigo_b)
                if inimigo_b.hp <= 0:
                    ESTADO_MAPAS[mapa_id]["inimigos_derrotados"].add((px, py))
                    linha_antiga = mapa_art[py]
                    mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        if mapas_ == mapas.praia.split("\n"):
            for px, py, ch in proximos:
                    if ch == '&':
                        if player.itens_coletaodos["item_1"] == False:
                            fala = 'Aqui está uma coisa para te ajudar\nfoi adicionado uma Bancada no\nIventario'
                            player.itens_coletaodos["item_1"] = True
                            falas(fala)
                            player.inventario.append(TODOS_OS_ITENS['Bancada'])
                        elif player.itens_coletaodos["item_1"] == True:
                            fala = 'Sabe aqui nesse ilha tem uma caverna aqui perto recomendo entrar lá para evoluir'
                            falas(fala)
                            substituir_caractere(mapa_art, 37, 6, ".")
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    if ch == "%":
                        limpar_todas_caverna()
                        mapas_aleatorio(player)
                
                
            adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'♠':10})

        elif mapas_ == mapas.caverna.split("\n"):
            adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'o': 25, 'G': 5, 'F': 5, 'B': 5, '!': 1})
            obstaculos_inimigo = ['o', 'G', 'F', 'B', f'{player.skin}', '!',"#"]
            inimigo_chars = ["F","G"]
            if caractere_atual == '!':
                player.andar += 1
                limpar_todas_caverna()
                mapas_aleatorio(player)
            
            mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=5)
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        elif mapas_ == mapas.caverna2.split("\n"):
            adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'o': 25, 'G': 5, 'F': 5, 'B': 5, '!': 1})
            obstaculos_inimigo = ['o', 'G', 'F', 'B', f'{player.skin}', '!',"#"]
            inimigo_chars = ["F","G"]
            if caractere_atual == '!':
                player.andar += 1
                limpar_todas_caverna()
                mapas_aleatorio(player)
            
            mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=5)
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        if feedback_message:
            with term.location(x_l , CAMERA_HEIGHT + y_l + 3):
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
                if caractere in ("*", "1"):
                    posicao = (player.x_mapa, player.y_mapa)
                    plantacoes = ESTADO_MAPAS[mapa_id].get("plantacoes", {})
                    if posicao in plantacoes:
                        tipo = plantacoes[posicao].get("item", "desconhecido")
                        feedback_message = f"Você está sobre uma semente de {tipo.capitalize()}."
                    else:
                        feedback_message = "Você está sobre uma semente plantada."

        else:
            if movi == "i":
                player.inventario_(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=0, batalha=False)
            
            elif movi == "sair":
                exit()
            
            elif movi == "up":
                player.up(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT + 2, x_i = 1)
            
            elif movi == 'r':
                for px, py, ch in proximos:
                    if ch == '♣':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        item_equipado = player.equipa.get("m_pri")
                        if item_equipado and item_equipado.nome.lower() == "machado" or item_equipado and item_equipado.nome.lower() ==  'picareta':
                            if item_equipado and item_equipado.nome.lower() == "machado":
                                if tentativas == 1:
                                    feedback_message == 'Você quebrou uma Arvore'
                                    linha_antiga = mapa_art[py]
                                    mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                                    interacoes_contagem.pop(pos, None)
                                    for _ in range(5):
                                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    break
                            elif item_equipado and item_equipado.nome.lower() == "picareta":
                                if tentativas == 1:
                                    feedback_message = 'Você começos a cortar a Arvore'
                                elif tentativas == 2:
                                    feedback_message = 'Você continuar cortando'
                                elif tentativas == 3:
                                    feedback_message = 'Você quebrou a Arvore'
                                    linha_antiga = mapa_art[py]
                                    mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                                    interacoes_contagem.pop(pos, None)
                                    for _ in range(5):
                                        player.inventario.append(TODOS_OS_ITENS["Madeira"])
                                    player.inventario.append(TODOS_OS_ITENS['Muda/Arvore'])
                                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    break
                        else:
                            feedback_message = 'Você precisa de um machado ou uma picareta'
                    elif ch == '♠':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        if tentativas == 1:
                            feedback_message = "Você colheu um arbusto"
                            linha_antiga = mapa_art[py]             
                            mapa_art[py] = linha_antiga[:px] + 'x' + linha_antiga[px + 1:]
                            interacoes_contagem.pop(pos, None) 
                            cair = random.randint(1, 5)                   
                            for _ in range(cair):
                                player.inventario.append(TODOS_OS_ITENS["Fruta"])
                            
                            ESTADO_MAPAS[mapa_id]["regeneracoes"][(px, py)] = {
                                "tempo_inicio": time.time(),
                                "tempo_regeneracao": 30,}
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

                        break 
                    elif ch == '¥':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        if tentativas == 1:
                            feedback_message = "Você coletou o Milho"
                            quantia_s = random.randint(1, 5)
                            quantia = random.randint(1, 5)
                            linha_antiga = mapa_art[py]
                            mapa_art[py] = linha_antiga[:px] + '=' + linha_antiga[px + 1:]
                            interacoes_contagem.pop(pos, None)
                            for _ in range(quantia):
                                player.inventario.append(TODOS_OS_ITENS["Milho"])
                            for _ in range(quantia_s):
                                player.inventario.append(TODOS_OS_ITENS["Semente/Milho"])
                            
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                        break
                    elif ch == 'x':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        if tentativas == 1:
                            feedback_message = "Você começa a cortar o arbusto..."
                        elif tentativas == 2:
                            feedback_message = "O arbusto caio..."
                            linha_antiga = mapa_art[py]
                            mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                            interacoes_contagem.pop(pos, None)
                            if pos in ESTADO_MAPAS[mapa_id].get("regeneracoes", {}):
                                del ESTADO_MAPAS[mapa_id]["regeneracoes"][pos]
                            for _ in range(2):
                                player.inventario.append(TODOS_OS_ITENS["Madeira"])
                            player.inventario.append(TODOS_OS_ITENS['Semente/Arbusto'])
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    elif ch == '#':
                        if mapas_ == mapas.praia.split("\n"):
                            pos = (px, py)
                            interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                            tentativas = interacoes_contagem[pos]
                            item_equipado = player.equipa.get("m_pri")
                            if item_equipado and item_equipado.nome.lower() == "machado":
                                if tentativas == 1:
                                    feedback_message = 'Você quebrou a Madeira'
                                substituir_caractere(mapa_art, px, py, '.')
                                player.inventario.append(TODOS_OS_ITENS['Madeira'])
                                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                            else:
                                feedback_message = 'Você precisa de um machado'
                        else:
                            pass
                    elif ch == 'o':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        item_equipado = player.equipa.get("m_pri")
                        if item_equipado and item_equipado.nome.lower() == "picareta":
                            if tentativas == 1:
                                feedback_message = 'Você quebrou uma Pedra'
                            substituir_caractere(mapa_art, px, py, '.')
                            player.inventario.append(TODOS_OS_ITENS['Pedra'])
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                        else:
                            feedback_message = 'Você precisa de uma Picareta'
                    elif ch == '‼':
                        pos = (px, py)
                        interacoes_contagem[pos] = interacoes_contagem.get(pos, 0) + 1
                        tentativas = interacoes_contagem[pos]
                        if tentativas == 1:
                            feedback_message = "Você coletou o Trigo"
                            quantia_s = random.randint(1, 5)
                            quantia = random.randint(1, 5)
                            linha_antiga = mapa_art[py]
                            mapa_art[py] = linha_antiga[:px] + '=' + linha_antiga[px + 1:]
                            interacoes_contagem.pop(pos, None)
                            for _ in range(quantia):
                                player.inventario.append(TODOS_OS_ITENS["Trigo"])
                            for _ in range(quantia_s):
                                player.inventario.append(TODOS_OS_ITENS["Semente/Trigo"])
                            
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                        break

            elif movi == 'jump':
                if mapas_ in (mapas.caverna.split("\n"), mapas.caverna2.split("\n")):
                    config = mapa_prai()
                    mini_mapa(
                    x_l=0, y_l=0,
                    player=player,
                    mapas_=config["mapa"],
                    camera_w=35, camera_h=15,
                    x_p=37, y_p=18,
                    menager="",
                    cores_custom=config["cores"],
                    obstaculos_custom=config["obstaculos"],
                    mapa_nome=config["nome"]
                    )

            elif movi == "e":
                chao_atual = mapa_art[player.y_mapa][player.x_mapa]
                if chao_atual == ".":
                    item_equipado = player.equipa.get("m_pri")
                    if item_equipado and item_equipado.nome.lower() == "enchada":
                        feedback_message = 'Você arou o chão'
                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, '=')
                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    if item_equipado and item_equipado.nome.lower() == 'pá':
                        if caractere_atual == '.':
                            tipo = 'terra'
                            tempo_crescimento = 25
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, ",")
                            ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                            "item": tipo,
                            "tempo_plantio": time.time(),
                            "tempo_crescimento": tempo_crescimento,}
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                            itens_ale = random.choice('Semente/Trigo', 'Semente/Milho', 'Semente/Abobora')
                            player.inventario.append(TODOS_OS_ITENS[f'{itens_ale}'])
                            feedback_message = f'Você cavou um buraco\nconseguio um {itens_ale}'
                        elif caractere_atual == ',':
                            feedback_message = 'Você já existe um buraco aqui'

            elif movi == 'x':
                for px, py, ch in proximos:
                    if ch == '%':
                        feedback_message = 'Entrando nas Caverna'
                    if ch == "$":
                        bau_armazenamento((px, py))
                        break
                    if ch == 'C':
                        player.craft(x=x_l, y=y_l, werd=CAMERA_WIDTH + 10, herd=CAMERA_HEIGHT + 2)
                    if ch == 'x':
                        pos = (px, py)
                        reg = ESTADO_MAPAS[mapa_id].get("regeneracoes", {}).get(pos)                        
                        if reg and time.time() - reg["tempo_inicio"] < reg["tempo_regeneracao"]:
                            feedback_message = "O arbusto ainda não deu frutos novamente."
                        else:
                            linha_antiga = mapa_art[py]
                            mapa_art[py] = linha_antiga[:px] + '*' + linha_antiga[px + 1:]
                            ESTADO_MAPAS[mapa_id]["regeneracoes"].pop(pos, None)
                            feedback_message = "O arbusto voltou a dar frutos!"

            elif movi == "usar":
                if mapas_ == mapas.praia.split('\n'):
                    if len(entrada) > 1 and entrada[1].isdigit():
                        indice = int(entrada[1]) - 1
                        if 0 <= indice < 4:
                            slot_nome = f"slot_{indice + 1}"
                            material_slot = player.matariais['slots'].get(slot_nome)
                            if material_slot:
                                item_escolhido = material_slot
                                if item_escolhido not in player.inventario:
                                    feedback_message = f"O item {item_escolhido.nome} não está mais no inventário. Slot liberado."
                                    player.matariais['slots'][slot_nome] = None
                                else:
                                    if item_escolhido.nome == "Madeira":
                                        feedback_message = "Você colocou Madeira."
                                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "#")
                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    elif item_escolhido.nome == "Bancada":
                                        feedback_message = "Você colocou Bancada."
                                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "C")
                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    elif item_escolhido.nome == "Pedra":
                                        feedback_message = "Você colocou Pedra."
                                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "#")
                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    elif item_escolhido.nome == "Bau":
                                        feedback_message = "Você colocou Bau."
                                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "$")
                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    
                                    elif item_escolhido.nome in ['Semente/Arbusto', 'Semente/Abobora', 'Semente/Milho', 'Semente/Trigo', 'Muda/Arvore']:
                                        if item_escolhido.nome == "Semente/Trigo":
                                            tipo = "trigo"
                                            tempo_crescimento = 30
                                        elif item_escolhido.nome == "Semente/Milho":
                                            tipo = "milho"
                                            tempo_crescimento = 30
                                        elif item_escolhido.nome == 'Semente/Abobora':
                                            tipo = 'abobora'
                                            tempo_crescimento = 60
                                        elif item_escolhido.nome == 'Muda/Arvore':
                                            tipo = 'arvore'
                                            tempo_crescimento = 120
                                        elif item_escolhido.nome == 'Semente/Arbusto':
                                            tipo = 'arbusto'
                                            tempo_crescimento = 20
                                        if tipo in ('trigo', 'milho', 'abobora'):
                                            if mapa_art[player.y_mapa][player.x_mapa] != "=":
                                                feedback_message = "Você só pode plantar sementes em solo arado ('=')."
                                                continue
                                        elif tipo in ('arvore', 'arbusto'):
                                            if mapa_art[player.y_mapa][player.x_mapa] != ".":
                                                feedback_message = "Você só pode plantar a muda em terra('.')."
                                        if tipo in ('trigo', 'milho', 'abobora'):
                                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "*")
                                        elif tipo in ('arvore', 'arbusto'):
                                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, "1")
                                        
                                        ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                                            "item": tipo,
                                            "tempo_plantio": time.time(),
                                            "tempo_crescimento": tempo_crescimento,
                                        }

                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                        feedback_message = f"Você plantou {tipo.capitalize()}!"
                                    elif item_escolhido.nome == "Pedra":
                                        feedback_message = "Você criou uma fundação sólida."
                                        player.inventario.remove(item_escolhido)
                                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                                    else:
                                        feedback_message = f"Você usou o material {item_escolhido.nome}!"
                                        
                                    tem_mais = any(i.nome == item_escolhido.nome for i in player.inventario)
                                    if not tem_mais:
                                        player.matariais['slots'][slot_nome] = None 

                            else:
                                feedback_message = f"O slot {indice + 1} está vazio."
                        elif indice < len(player.inventario):
                            item_escolhido = player.inventario[indice]

                            if item_escolhido.tipo == "Material":
                                feedback_message = "Você precisa equipar esse material em um slot para usá-lo."
                            else:
                                feedback_message = f"Você usou o item {item_escolhido.nome}!"
                        else:
                            feedback_message = "Número inválido."
                    else:
                        feedback_message = "Use: usar [número]"
                    
            elif movi == "save":
                salvar_jogo_global(player, ESTADO_MAPAS)
                feedback_message = "Jogo salvo com sucesso."
            
            else:
                feedback_message = f"Comando '{movi}' inválido. Use w/a/s/d/inventario/up/q."


"""config = mapa_prai()
player.inventario.append(TODOS_OS_ITENS['Machado'])
player.inventario.append(TODOS_OS_ITENS['Picareta'])
mini_mapa(
x_l=0, y_l=0,
player=player,
mapas_=config["mapa"],
camera_w=35, camera_h=15,
x_p=37, y_p=18,
menager="",
cores_custom=config["cores"],
obstaculos_custom=config["obstaculos"],
mapa_nome=config["nome"]
)"""
