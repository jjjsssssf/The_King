from classe_do_jogador import jogador
from classe_do_inimigo import inimigo
from quebrar import *
from collections import deque
import time, random, os, json, textwrap
from collections import Counter
from maps import *
from inimigo_batalha import *
from batalha import *
from classe_arts import *
from mm import tocar_musica, escolher_e_tocar_musica, parar_musica, tocando_musica
from classe_do_inventario import *
##ARQUIVO DO MAPA
mapas = mini_mapa_()
dialogo = dialogos()
ascii = art_ascii()
C = Cores()
player = jogador(nome="Joojs", hp_max=30, atk=5000, niv=15, xp_max=100, defesa=0, gold=0, stm_max=100, intt=0, mn_max=100,d_m=15,art_player=ascii.necro, skin="@", skin_nome='')
import glob
import json, os, glob

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

def salvar_jogo_player(player, filename="save_player.json"):
    try:
        # Serializa o inventário e equipamento apenas pelos nomes
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
            "mana_max": player.mana_max,
            "mana": player.mana,
            "d_m": player.dano_magico,
            "xp": player.xp,
            "aleatorio": player.aleatorio,
            "inventario": inventario_nomes,
            "equipa": equipa_nomes,
            "itens_coletados": player.itens_coletaodos,
            "rodar": player.rodar_jogo,
            "classe": player.classe,
            "pos_x": player.x_mapa,
            "pos_y": player.y_mapa,
            "mapa_atual": player.mapa_atual,
            "skin": player.skin,
            "skin_nome": player.skin_nome,
            "pontos": player.ponto,
            "andar": player.andar,
            "seed": player.seed,
            'seed_caverna': player.seed_caverna,
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(player_data, f, indent=4)
    except Exception as e:
        pass

def carregar_jogo_player(filename="save_player.json"):
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            player_data = json.load(f)

        # Reconstrói o jogador
        SKIN_MAP = {
            "necro": ascii.necro,
            "guerreiro": ascii.guerriro,
            "mago": ascii.mago
        }
        skin_nome_carregado = player_data.get("skin_nome")
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
            mn_max=player_data["mana_max"],
            d_m=player_data["d_m"],
            art_player=skin_arte_carregada,
            skin=player_data.get("skin", "@"),
            skin_nome=skin_nome_carregado,
        )

        # Restaura atributos
        player.hp = player_data["hp"]
        player.mana = player_data["mana"]
        player.xp = player_data["xp"]
        player.stm = player_data["stm"]
        player.ponto = player_data["pontos"]
        player.andar = player_data["andar"]
        player.x_mapa = player_data["pos_x"]
        player.y_mapa = player_data["pos_y"]
        player.seed_caverna = player_data['seed_caverna']
        player.seed = player_data["seed"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None
                         for slot, n in player_data.get("equipa", {}).items()}
        player.itens_coletaodos = player_data.get("itens_coletados", {})
        player.rodar_jogo = player_data.get("rodar")
        player.classe = player_data.get("classe")
        return player

    except Exception as e:
        return None

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
            "regeneracoes": estado_mapa.get("regeneracoes", {}),
            "interacoes": estado_mapa.get("interacoes", {}),
            "caracteres_aleatorios": estado_mapa.get("caracteres_aleatorios", []),
            "baus_armazenamento": estado_mapa.get("baus_armazenamento", {}),
            "tempo_inicio": estado_mapa.get("tempo_inicio"),
            "tempo_decorrido": estado_mapa.get("tempo_decorrido", 0)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializar_para_json(dados_salvar), f, indent=4)

    except IOError as e:
        print(f"❌ Erro ao salvar mapa em {filename}: {e}")
    except Exception as e:
        print(f"⚠️ Erro inesperado ao salvar mapa {mapa_id}: {e}")

def carregar_mapa_estado(filename):
    if not os.path.exists(filename):
        print(f"Nenhum save encontrado para {filename}. Será criado um novo mapa.")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            dados_carregados = json.load(f)
            estado_deserializado = deserializar_do_json(dados_carregados)
            # Conversões de volta para SETs
            estado_deserializado["inimigos_derrotados"] = set(estado_deserializado.get("inimigos_derrotados", []))
            estado_deserializado["baus_abertos"] = set(estado_deserializado.get("baus_abertos", []))
            estado_deserializado["obstaculos"] = set(estado_deserializado.get("obstaculos", []))
            estado_deserializado["chaves_pegas"] = set(estado_deserializado.get("chaves_pegas", []))
            estado_deserializado["abrir_porta"] = set(estado_deserializado.get("abrir_porta", [])) 
            # Corrige baús com chaves de string em vez de tupla
            baus_finais = {}
            baus_armazenamento_carregados = estado_deserializado.get("baus_armazenamento", {})
            for pos_str, lista_itens in baus_armazenamento_carregados.items():
                if isinstance(pos_str, tuple):
                    pos_tuple = pos_str
                else:
                    try:
                        pos_tuple = tuple(map(int, pos_str.strip("()").split(",")))
                    except Exception:
                        pos_tuple = pos_str  # fallback se não for uma tupla válida
                baus_finais[pos_tuple] = lista_itens

            estado_deserializado["baus_armazenamento"] = baus_finais

            # Garante que todos os campos esperados existam
            if "regeneracoes" not in estado_deserializado:
                estado_deserializado["regeneracoes"] = {}
            if "plantacoes" not in estado_deserializado:
                estado_deserializado["plantacoes"] = {}
            if "cores" not in estado_deserializado:
                estado_deserializado["cores"] = {}
            estado_deserializado.setdefault("tempo_inicio", None)
            estado_deserializado.setdefault("tempo_decorrido", 0)

            print(f"✅ Estado do mapa '{filename}' carregado com sucesso.")
            return estado_deserializado

    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON do arquivo {filename}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado ao carregar estado do mapa {filename}: {e}")
        return None

def limpar_todos_os_saves():
    """Remove todos os arquivos de save de qualquer mapa."""
    for save_file in glob.glob("save_mapa_Mundo.json"):
        try:
            os.remove(save_file)
            print(f"Save removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todos_os_player():
    """Remove todos os arquivos de save de qualquer mapa."""
    for save_file in glob.glob("save_player.json"):
        try:
            os.remove(save_file)
            print(f"Save removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

def limpar_todas_caverna():
    for save_file in glob.glob("save_mapa_Caverna - *.json"):
        try:
            os.remove(save_file)
            print(f"Save de caverna removido: {save_file}")
        except Exception as e:
            print(f"Erro ao remover {save_file}: {e}")

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
            "andar": player.andar,
            'seed': player.seed,
            'seed_caverna': player.seed_caverna,
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
                "tempo_inicio": estado.get("tempo_inicio"),
                "tempo_decorrido": estado.get("tempo_decorrido", 0),
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
        player.seed = player_data['seed']
        player.y_mapa = player_data["pos_y"]
        player.mapa_atual = player_data["mapa_atual"]
        player.inventario = [TODOS_OS_ITENS[n] for n in player_data.get("inventario", []) if n in TODOS_OS_ITENS]
        player.equipa = {slot: TODOS_OS_ITENS[n] if n and n in TODOS_OS_ITENS else None for slot, n in player_data.get("equipa", {}).items()}
        player.mana_lit = player_data.get("mana_lit", [])
        player.itens_coletaodos = player_data.get("itens_coletaodos", {})
        player.rodar_jogo = player_data["rodar"]
        player.classe = player_data["classes"]
        player.seed_caverna = player_data['seed_caverna']

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
                "tempo_inicio": estado_deserializado.get("tempo_inicio"),
                "tempo_decorrido": estado_deserializado.get("tempo_decorrido", 0),
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

    salvar_mapa_estado(f"save_mapa_{mapa_id}.json", mapa_id, estado_mapa)

def contar_caracteres_no_mapa(mapa_art, caracteres=None):
    if caracteres is None:
        return False
    
    contador = {ch: 0 for ch in caracteres.keys()}

    for linha in mapa_art:
        for ch in linha:
            if ch in contador:
                contador[ch] += 1

    # Verifica se algum caractere atingiu ou ultrapassou o limite
    for ch, limite in caracteres.items():
        if contador[ch] >= limite:
            return True
    
    return False

def adicionar_construcoes_aleatorias(mapa, construcoes_disponiveis,quantidades,zona_segura=(10, 5),player_spawn=(50, 25),distancia_minima=15,seed=None):
    if seed is not None:
        random.seed(seed)

    altura = len(mapa)
    largura = len(mapa[0])
    player_spawn_x, player_spawn_y = player_spawn
    zona_segura_x, zona_segura_y = zona_segura

    construcoes_colocadas = []

    for tipo, qtd in quantidades.items():
        if tipo not in construcoes_disponiveis:
            continue
        for _ in range(qtd):
            estrutura = random.choice(construcoes_disponiveis[tipo])
            alt = len(estrutura)
            larg = len(estrutura[0])

            max_tentativas = 100
            for _ in range(max_tentativas):
                x = random.randint(0, largura - larg - 1)
                y = random.randint(0, altura - alt - 1)

                # Evitar zona segura
                if abs(x - player_spawn_x) < zona_segura_x and abs(y - player_spawn_y) < zona_segura_y:
                    continue

                # Evitar sobreposição com outras construções
                muito_perto = False
                for (cx, cy) in construcoes_colocadas:
                    if abs(x - cx) < distancia_minima and abs(y - cy) < distancia_minima // 2:
                        muito_perto = True
                        break
                if muito_perto:
                    continue

                # Verifica se área é livre
                espaco_livre = True
                for yy in range(alt):
                    for xx in range(larg):
                        if mapa[y + yy][x + xx] != '.':
                            espaco_livre = False
                            break
                    if not espaco_livre:
                        break

                if not espaco_livre:
                    continue

                # Coloca a construção
                for yy, linha in enumerate(estrutura):
                    for xx, ch in enumerate(linha):
                        mapa[y + yy][x + xx] = ch

                construcoes_colocadas.append((x, y))
                break  # sucesso

    return mapa

def add_boss(mapa_art, player, mapa_id, ESTADO_MAPAS, num=0):
    from maps import BOSS
    CONSTRUCOES = {
        'BOSS': [BOSS[num]]
    }
    quantidades = {
        'BOSS': 1
    }

    mapa_mutavel = [list(linha) for linha in mapa_art]
    mapa_mutavel = adicionar_construcoes_aleatorias(
        mapa=mapa_mutavel,
        construcoes_disponiveis=CONSTRUCOES,
        quantidades=quantidades,
        zona_segura=(10, 5),
        player_spawn=(player.x_mapa, player.y_mapa),
        distancia_minima=20
    )
    mapa_art = [''.join(linha) for linha in mapa_mutavel]
    ESTADO_MAPAS[mapa_id]["mapa_art"] = mapa_art
    return mapa_art

def localizar_caractere(mapa_art, caractere):
    posicoes = []
    for y, linha in enumerate(mapa_art):
        for x, ch in enumerate(linha):
            if ch == caractere:
                posicoes.append((x, y))
    return posicoes

from collections import deque

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

def remover_caracteres(mapa_art, caracteres_para_remover):
    for y in range(len(mapa_art)):
        linha = mapa_art[y]
        nova_linha = ""
        for ch in linha:
            if ch in caracteres_para_remover:
                nova_linha += "."
            else:
                nova_linha += ch
        mapa_art[y] = nova_linha

def mini_mapa(
    x_l, y_l, player, mapas_, camera_w, camera_h, x_p, y_p, menager,
    cores_custom=None, obstaculos_custom=None, mapa_anterior=None, interacoes_custom=None, 
    mapa_nome=None, ESTADO_GLOBAL_LOAD=None ):
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
            "tempo_inicio": estado_carregado.get("tempo_inicio"),
            "tempo_decorrido": estado_carregado.get("tempo_decorrido", 0),
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
    tempo_inicio = time.time()
    tempo_decorrido = 0


    if estado_carregado:
        tempo_decorrido = estado_carregado.get("tempo_decorrido", 0)
        # Ajusta tempo_inicio para que tempo_decorrido seja mantido
        tempo_inicio = time.time() - tempo_decorrido

    ESTADO_MAPAS[mapa_id]["tempo_inicio"] = tempo_inicio
    ESTADO_MAPAS[mapa_id]["tempo_decorrido"] = tempo_decorrido

    TEMPO_TOTAL_DIA = 15 * 60
    PERIODOS = {
        "dia": (0, TEMPO_TOTAL_DIA / 3),
        "tarde": (TEMPO_TOTAL_DIA / 3, 2 * TEMPO_TOTAL_DIA / 3),
        "noite": (2 * TEMPO_TOTAL_DIA / 3, TEMPO_TOTAL_DIA)
    }
    periodo_atual = "dia"

    if "plantacoes" not in ESTADO_MAPAS[mapa_id]:
        ESTADO_MAPAS[mapa_id]["plantacoes"] = {}

    camera_x = max(0, player.x_mapa - CAMERA_WIDTH // 2)
    camera_y = max(0, player.y_mapa - CAMERA_HEIGHT // 2)

    def atualizar_camera():
        nonlocal camera_x, camera_y
        camera_x = max(0, min(MAP_WIDTH - CAMERA_WIDTH, player.x_mapa - CAMERA_WIDTH // 2))
        camera_y = max(0, min(MAP_HEIGHT - CAMERA_HEIGHT, player.y_mapa - CAMERA_HEIGHT // 2))

    while True:
        if player.hp <= 0:
            player_carregado, mapas_carregados = carregar_jogo_global(filename="save_global.json")
            if player_carregado:
                player = player_carregado
                ESTADO_MAPAS = mapas_carregados
                estado_mapa_salvo = ESTADO_MAPAS.get(player.mapa_atual)
                if estado_mapa_salvo:
                    mapa_art_para_load = estado_mapa_salvo["mapa_art"]
                    cores_custom = estado_mapa_salvo.get("cores", None)
                    obstaculos_custom = estado_mapa_salvo.get("obstaculos", None)
                else:
                    limpar_todos_os_saves()
                    limpar_todos_os_player()
                    config = mapa_procedural(nome=player.mapa_atual, largura=250, altura=10, seed=player.seed)
                    mapa_art_para_load = config["mapa"]
                    cores_custom = config.get("cores", None)
                    obstaculos_custom = config.get("obstaculos", None)
                x_p_load = player.x_mapa
                y_p_load = player.y_mapa
                mini_mapa(
                    x_l=0,
                    y_l=0,
                    player=player,
                    mapas_=mapa_art_para_load,
                    camera_w=35,
                    camera_h=15,
                    x_p=x_p_load,
                    y_p=y_p_load,
                    menager="",
                    mapa_nome=player.mapa_atual,
                    cores_custom=cores_custom,
                    obstaculos_custom=obstaculos_custom,
                    ESTADO_GLOBAL_LOAD=mapas_carregados
                )
                status_ale_menor = random.choice('atk', 'def', 'atk/mn', 'int')
                if status_ale_menor == 'atk':
                    player.atk -= 2
                elif status_ale_menor == 'def':
                    player.defesa -= 2
                elif status_ale_menor == 'atk/mn':
                    player.d_m -= 2
                elif status_ale_menor == 'int':
                    player.intt -= 2
            else:
                exit()
        
        tempo_decorrido = (time.time() - tempo_inicio) % TEMPO_TOTAL_DIA
        if PERIODOS["dia"][0] <= tempo_decorrido < PERIODOS["dia"][1]:
            periodo_atual = "dia"
        elif PERIODOS["tarde"][0] <= tempo_decorrido < PERIODOS["tarde"][1]:
            periodo_atual = "tarde"
        else:
            periodo_atual = "noite"
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
        mobs_chars = []
        boss = []
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
                clear()
                contagem_player = Counter(item.nome for item in player.inventario)
                conteudo_player = []
                for i, item_nome in enumerate(sorted(contagem_player.keys())):
                    quantidade = contagem_player[item_nome]
                    conteudo_player.append(f"{i+1}. {item_nome} ({quantidade}x)")
                
                conteudo_player_str = "\n".join(conteudo_player) or "Inventário vazio."

                draw_window(
                    term, 
                    x=x_l - 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=f"Inventário de {player.nome}",
                    text_content=conteudo_player_str
                )
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
                contagem_bau = Counter(item.nome for item in bau_inventario)
                conteudo_bau = []
                for i, item_nome in enumerate(sorted(contagem_bau.keys())):
                    quantidade = contagem_bau[item_nome]
                    conteudo_bau.append(f"{i+1}. {item_nome} ({quantidade}x)")
                
                conteudo_bau_str = "\n".join(conteudo_bau) or "Baú vazio."

                draw_window(
                    term, 
                    x=x_l + 35, 
                    y=y_l, 
                    width=30, 
                    height=15, 
                    title=term.bold_green("Itens do Baú"),
                    text_content=conteudo_bau_str
                )

            def processar_transferencia(origem_lista, destino_lista, titulo_escolha):
                """Gerencia a transferência de itens (Guardar/Pegar) com controle exato de quantidades."""
                if not origem_lista:
                    falas(f"A lista de origem ({titulo_escolha}) está vazia.")
                    return

                clear()
                contagem_origem = Counter(item.nome for item in origem_lista)
                itens_unicos = sorted(contagem_origem.keys())
                mapeamento_escolha = {i + 1: item_nome for i, item_nome in enumerate(itens_unicos)}

                # Mostra os itens disponíveis
                linhas_display = [
                    f"{i}. {nome} ({contagem_origem[nome]}x)"
                    for i, nome in mapeamento_escolha.items()
                ]
                draw_window(
                    term,
                    x=x_l,
                    y=y_l,
                    width=40,
                    height=15,
                    title=titulo_escolha,
                    text_content="\n".join(linhas_display)
                )

                with term.location(x=x_l, y=y_l + 16):
                    entrada = input(term.bold("Digite [Nº Item] [Quantia] ou 0 para cancelar: ")).strip().split()

                if not entrada or entrada[0].upper() == '0':
                    return

                # Processa a entrada
                try:
                    idx_escolhido = int(entrada[0])
                    quantia_desejada = int(entrada[1]) if len(entrada) > 1 else 1
                except ValueError:
                    falas("Entrada inválida. Use o formato: [Nº Item] [Quantia].")
                    return

                if idx_escolhido not in mapeamento_escolha:
                    falas("Número de item inválido.")
                    return

                item_nome_selecionado = mapeamento_escolha[idx_escolhido]
                quantidade_disponivel = contagem_origem[item_nome_selecionado]

                if quantia_desejada <= 0:
                    falas("A quantidade deve ser maior que zero.")
                    return
                if quantia_desejada > quantidade_disponivel:
                    falas(f"Você só tem {quantidade_disponivel}x de {item_nome_selecionado}.")
                    return

                # Transfere exatamente a quantia pedida
                itens_transferidos = 0
                novos_itens = []
                for item_obj in origem_lista[:]:  # cópia para evitar modificação durante iteração
                    if item_obj.nome == item_nome_selecionado:
                        destino_lista.append(item_obj)
                        origem_lista.remove(item_obj)
                        itens_transferidos += 1
                        if itens_transferidos >= quantia_desejada:
                            break

                if itens_transferidos > 0:
                    acao = "guardados no baú" if destino_lista is bau_inventario else "retirados do baú"
                    falas(f"{itens_transferidos}x {item_nome_selecionado} foram {acao}.")
                    salvar_mapa_estado(save_filename, mapa_id, ESTADO)
                else:
                    falas("Nenhum item foi transferido.")

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
        if player.mapa_atual == 'Mundo':
            draw_window(term, x=x_l, y=y_l, width=CAMERA_WIDTH + 4, height=CAMERA_HEIGHT + 2,title=f"{mapa_nome} - {periodo_atual.capitalize()}", text_content=mini_mapa_render)
        else:
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
            
        def verificar_proximidade_cruz(x, y, mapa_art):
            direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            proximidades = []
            for dx, dy in direcoes:
                nx, ny = x + dx, y + dy
                if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                    ch = mapa_art[ny][nx]
                    proximidades.append((nx, ny, ch))
            return proximidades

        proximos = verificar_proximidade_cruz(player.x_mapa, player.y_mapa, mapa_art)

        def verificar_frente(x, y, direcao, mapa_art):
            dir_map = {
                "cima": (0, -1),
                "baixo": (0, 1),
                "esquerda": (-1, 0),
                "direita": (1, 0)
            }
            dx, dy = dir_map[direcao]
            nx, ny = x + dx, y + dy
            if 0 <= nx < MAP_WIDTH and 0 <= ny < MAP_HEIGHT:
                return [(nx, ny, mapa_art[ny][nx])]
            return []

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

        if player.mapa_atual == f'Caverna - [{player.andar}]':
            if player.andar == 10:
                if player.boss['Suny']== False:
                    for px, py, ch in proximos:
                        if ch == "@":
                            fala = 'Um homem invadindo o meu meu lar? seu verme maldito irei te matar como matei os outros que já matei'
                            falas(fala)
                            status = sun(player_b=player, art=ascii)
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
                            batalha_cut(player_b=player, inimigo_b=inimigo_b)
                            if inimigo_b.hp <= 0:
                                player.inventario.append(TODOS_OS_ITENS['Chave do Dragão'])
                                player.boss['Suny'] = True
                                ESTADO_MAPAS[mapa_id]["inimigos_derrotados"].add((px, py))
                                linha_antiga = mapa_art[py]
                                mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

            obstaculos_inimigo = ['o', 'G', 'F', 'B', f'{player.skin}','u',"#",'c', "@", '\\']
            inimigo_chars = ["F","G"]
            boss = ['@']
            mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=boss, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=10)
            mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=5)
            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

        if player.mapa_atual == 'Mundo':
            largura = 800
            altura = 250
            total = largura * altura
            if periodo_atual == 'noite':
                adicionar_caracteres_aleatorios(mapa_id, ESTADO_MAPAS[mapa_id], caracteres_quantidades={'G': int(total * 0.0006), 'F': int(total * 0.0003)})
                obstaculos_inimigo = {'#', '♣', '&', "C", '‼', '¥', 'o', '0', '1', '„', '♠', 'x', '$', '+', 'P', 'N', 'I', 'G', 'F', '!', '/', 'O', '@', '%', '\\'}
                inimigo_chars = ['F', 'R']
                mover_inimigos_para_jogador(mapa_art, player=player, obstaculos=obstaculos_inimigo, inimigo_chars=inimigo_chars, estado_mapa=ESTADO_MAPAS[mapa_id], raio_visao=7)
                salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
            elif periodo_atual == 'dia':
                if player.boss['Suny'] == True:
                    if not ESTADO_MAPAS[mapa_id].get("boss_adicionado", False):
                        mapa_art = add_boss(mapa_art, player, mapa_id, ESTADO_MAPAS, num=0)
                        ESTADO_MAPAS[mapa_id]["boss_adicionado"] = True
                    if player.boss['Serafas']== False:
                        for px, py, ch in proximos:
                            if ch == "@":
                                fala = 'Jovem entras em minha igreja blasfema no nome de teu Deus e não querem que eu te mate'
                                falas(fala)
                                status = sern(player_b=player, art=ascii)
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
                                batalha_cut(player_b=player, inimigo_b=inimigo_b)
                                if inimigo_b.hp <= 0:
                                    player.boss['Serafas'] = True
                                    fala = 'Mesmo com minha morte meu deus ira te derrotar o tempo está passando todos seu caminhos levaram a ruina'
                                    falas(fala)
                                    ESTADO_MAPAS[mapa_id]["inimigos_derrotados"].add((px, py))
                                    linha_antiga = mapa_art[py]
                                    mapa_art[py] = linha_antiga[:px] + '.' + linha_antiga[px + 1:]
                                    salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])

                remover_caracteres(mapa_art, caracteres_para_remover=['F', 'G'])
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
        if entrada[0].lower() == "z":
            if len(entrada) > 1 and entrada[1].lower() in ["w", "a", "s", "d"]:
                direcao_input = entrada[1].lower()
                direcao_nome = {
                    "w": "cima",
                    "s": "baixo",
                    "a": "esquerda",
                    "d": "direita"
                }[direcao_input]
                player.direcao = direcao_nome
                feedback_message = f"Você agora está virado para {direcao_nome}."
            else:
                feedback_message = "Use Z + W/A/S/D para virar sem se mover."
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
        tecla_para_direcao = {
            "w": "cima",
            "s": "baixo",
            "a": "esquerda",
            "d": "direita"
        }

        if movi in direcoes:
            dx, dy = direcoes[movi]
            player.direcao = tecla_para_direcao[movi]
            for _ in range(quant):
                passo_x = player.x_mapa + dx
                passo_y = player.y_mapa + dy

                # Checa limites do mapa
                if 0 <= passo_x < MAP_WIDTH and 0 <= passo_y < MAP_HEIGHT:
                    caractere = mapa_art[passo_y][passo_x]

                    # Se não é obstáculo nem inimigo, anda
                    if caractere not in OBSTACULOS and caractere not in inimigo_chars:
                        player.x_mapa = passo_x
                        player.y_mapa = passo_y

                        # Interações automáticas com blocos especiais
                        if caractere in INTERACOES:
                            INTERACOES[caractere]()

                    # Feedback de plantações
                    if (player.x_mapa, player.y_mapa) in ESTADO_MAPAS[mapa_id].get("plantacoes", {}):
                        planta = ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)]
                        tipo = planta.get("item", "desconhecido")
                        feedback_message = f"Você está sobre uma semente de {tipo.capitalize()}."
                    elif caractere in ("*", "1"):
                        feedback_message = "Você está sobre uma semente plantada."
                    else:
                        feedback_message = "" 
        else:
            px, py = player.x_mapa, player.y_mapa
            caractere_atual = mapa_art[py][px]

            if movi == "i":
                player.inventario_(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=0, batalha=False)

            elif movi == 'help':
                def tutorail():
                    clear()
                    penis = '''[1] Para se mover digite WASD segugido de um numero (ex)
W 10 seu jogador ira se mover 10 para cima
[2] Para usar o Invenrario digite i 
[3] Para conversar, abrir o bau e para entrar em burado digete x
[4] Para quebrar blocos digite r alguns blocos quebram mais facil com 
itens melhores
[5] Para Equipar alguma coisa do entre no inventario e digite o numero
do objeto para o desequipar faz o mesmo porem com ele equipado
[6] Para colocar um bloco no chão equipe o bloco no inventario
depois digite o numero dele segundo o slot dele por (ex) 2 ira
utilisar o item na possição 2 dos slots de itens
[7] Para melhoras seus status digite up 
[8] Para entrar em um cavena equipe uma pá digite "e" no chão
[9] Para sair de uma caverna digite jump
[10] Para arar a terra equipe uma enchada digite "e" no chão
[11] Para plantar alguma coisa se for uma semente fique em cima da
terra arada e equipe a semente e digite o usar na terra arada
casa for uma muda a terra não pode estar arada 
[12] Para ver oque está equipado digite eq
[13] Para salvar o jogo digite save
[14] Para sair do jogo digite sair
                    '''
                    draw_window(term, x=x_l, y=y_l, width=90, height=27, text_content=penis)
                    with term.location(x=x_l+1, y= 22):
                        input()
                tutorail()
                  
            elif movi == "sair":
                exit()
            
            elif movi == "up":
                player.up(x=x_l + CAMERA_WIDTH + 5, y=y_l, werd=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT + 2, x_i = 1)
            
            elif movi == 'jump':
                player.andar = 0
                salvar_jogo_player(player)
                config_player = carregar_jogo_player()
                if config_player is None:
                    feedback_message = ""
                    continue
                config = mapa_procedural(
                    nome="Mundo",
                    largura=800,
                    altura=400,
                    seed=config_player.seed
                )
                mini_mapa(
                    x_l=0, y_l=0,
                    player=config_player,
                    mapas_=config["mapa"],
                    camera_w=35,
                    camera_h=15,
                    x_p=config_player.x_mapa,
                    y_p=config_player.y_mapa,
                    menager="",
                    cores_custom=config["cores"],
                    obstaculos_custom=config["obstaculos"],
                    mapa_nome=config["nome"]
                )
                break

            elif movi == 'r':
                frente = verificar_frente(player.x_mapa, player.y_mapa, player.direcao, mapa_art)
                for px, py, ch in frente:
                    feedback_message = interagir_com_objeto(
                        px, py, ch, player, mapa_art, mapa_id, interacoes_contagem,
                        ESTADO_MAPAS, TODOS_OS_ITENS, save_filename, mapas_,
                        salvar_mapa_estado, substituir_caractere
                    )
                    if feedback_message:
                        break

            elif movi == "e":
                chao_atual = mapa_art[player.y_mapa][player.x_mapa]
                if chao_atual == ".":
                    item_equipado = player.equipa.get("m_seg")
                    if item_equipado and item_equipado.nome.lower() == "enchada":
                        feedback_message = 'Você arou o chão'
                        substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, '=')
                        salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                    if item_equipado and item_equipado.nome.lower() == 'pá':
                        if caractere_atual == '.':
                            tipo = 'terra'
                            tempo_crescimento = 50
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, ",")
                            ESTADO_MAPAS[mapa_id]["plantacoes"][(player.x_mapa, player.y_mapa)] = {
                            "item": tipo,
                            "tempo_plantio": time.time(),
                            "tempo_crescimento": tempo_crescimento,}
                            salvar_mapa_estado(save_filename, mapa_id, ESTADO_MAPAS[mapa_id])
                            itens_ale = random.choice(["Semente/Trigo", "Semente/Milho", "Semente/Abobora",'Nada','Nada','Nada',
                                'Nada','Nada','Nada','Nada'])
                            if itens_ale == 'Nada':
                                pass 
                            else:
                                player.inventario.append(TODOS_OS_ITENS[f"{itens_ale}"])
                                feedback_message = f'Você cavou um buraco\nconseguio um {itens_ale}'

                        elif caractere_atual == ',':
                            feedback_message = 'Você já existe um buraco aqui'
                        elif caractere_atual == '=':
                            feedback_message = 'Você fez a terra arada em terra'
                            substituir_caractere(mapa_art, player.x_mapa, player.y_mapa, ".")
                frente = verificar_frente(player.x_mapa, player.y_mapa, player.direcao, mapa_art)
                for px, py, ch in frente:
                    if ch == "~":
                        item_equipado = player.equipa.get("m_seg")
                        if item_equipado and item_equipado.nome.lower() == "Vara de Pesca":
                            feedback_message = "Você jogol uma isca..."
                            time.sleep(2)
                            feedback_message = "Alguma coisa foi pegar!!"
                            time.sleep(2)
                            pesca = random.choice(["Tilapia", "Nada", "Salmão", "Nada", "Camarão", "Nada"])
                            if pesca == "Nada":
                                feedback_message = "Sem sorte não veio nada"
                                player.stm -= 5
                            else:
                                feedback_message = f"Você pescou um {pesca}"
                                player.inventario.append(TODOS_OS_ITENS[f"{pesca}"])
                                player.stm -= 5

            elif movi == 'x':
                if caractere_atual == ',':
                    player.andar += 1
                    limpar_todas_caverna()
                    ale_seed = random.randint(1, 50)
                    player.seed_caverna = ale_seed
                    config = mapa_caverna(nome=f"Caverna - [{player.andar}]", largura=800, altura=400, player_b=player,seed=player.seed_caverna)
                    mini_mapa(
                        x_l=0, y_l=0,
                        player=player,
                        mapas_=config["mapa"],
                        camera_w=35, camera_h=15,
                        x_p=player.x_mapa, y_p=player.y_mapa,
                        menager="",
                        cores_custom=config["cores"],
                        obstaculos_custom=config["obstaculos"],
                        mapa_nome=config["nome"]
                    )
                        
                for px, py, ch in proximos:
                    if ch == "$":
                        bau_armazenamento((px, py))
                        break
                    if ch == 'C':
                        player.craft(x=x_l, y=y_l, werd=CAMERA_WIDTH + 10, herd=CAMERA_HEIGHT + 2)
                    if ch == '%':
                        player.forja(x=x_l, y=y_l, werd=CAMERA_WIDTH + 10, herd=CAMERA_HEIGHT + 2)
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
                    if ch == 'P':
                        if player.boss['Suny'] == False:
                            padres = localizar_caractere(mapa_art, '@')
                            fala = random.choice([dialogo.padre_1, dialogo.padre_2, dialogo.padre_3])
                            falas(fala)
                        else:
                            falas(dialogo.padre_4)
                            player.aprender_magias(term ,x_menu=x_l + CAMERA_WIDTH + 5, y_menu=y_l, wend=CAMERA_WIDTH + 5, herd=CAMERA_HEIGHT)
                    if ch == '&':
                        if player.boss['Suny']== False:
                            fala = random.choice([dialogo.aldao_1, dialogo.aldao_2,dialogo.aldao_3])
                            falas(fala)
                        else:
                            fala = random.choice([dialogo.aldao_1, dialogo.aldao_2,dialogo.aldao_3,dialogo.aldao_4,dialogo.aldao_5])
                            falas(fala)
                            posicoes_alvo = localizar_caractere(mapa_art, '@')
                            if posicoes_alvo:
                                x_alvo, y_alvo = posicoes_alvo[0]
                                feedback_message = f"O Padre Argos está localizado em X: {x_alvo}, Y: {y_alvo}!"
                            else:
                                pass
                    if ch == 'V':
                        player.gerenciar_loja(x=0, y=0, largura=30)

            elif entrada[0].isdigit():
                    feedback_message = usar_item(
                        player, entrada, mapa_art, mapa_id, ESTADO_MAPAS,
                        TODOS_OS_ITENS, save_filename, mapas_,
                        salvar_mapa_estado, substituir_caractere
                    )

            elif movi == "eq":
                player.menu_status(x=x_l + CAMERA_WIDTH + 5, y=y_l, largura=40)

            elif movi == "save":
                salvar_jogo_global(player, ESTADO_MAPAS)
                feedback_message = "Jogo salvo com sucesso."
            
            else:
                feedback_message = f"Comando '{movi}' inválido. Use w/a/s/d/inventario/up/q."


