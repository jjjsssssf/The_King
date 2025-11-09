from collections import defaultdict

class Item:
    def __init__(self, nome, tipo, nivel = 0, bonus_hp=0, bonus_stm = 0,bonus_mana=0, bonus_atk=0, bonus_def=0, bonus_atk_mana=0, bonus_hp_max=0,preco=0, slot_equip=None, vendivel=True, comprável=True):
        self.nome = nome
        self.vendivel = vendivel
        self.comprável = comprável
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_hp_max = bonus_hp_max
        self.bonus_mana = bonus_mana
        self.bonus_stm = bonus_stm
        self.bonus_atk = bonus_atk
        self.preco = preco
        self.bonus_atk_mana = bonus_atk_mana
        self.bonus_def = bonus_def
        self.slot_equip = slot_equip
        self.nivel = nivel

    def __repr__(self):
        return f"Item(nome='{self.nome}', tipo='{self.tipo}', comprável={self.comprável})"

TODOS_OS_ITENS = {
    ###ARMAS
    "Espada": Item(nome=f"Espada", tipo="Equipavel", preco=100, bonus_atk=10, slot_equip="m_pri", nivel=1),
    "Picareta/Madeira": Item(nome='Picareta/Madeira', tipo='Equipavel', preco=100, bonus_def=2, slot_equip="m_ter",nivel=1),
    "Picareta/Pedra": Item(nome='Picareta/Pedra', tipo='Equipavel', preco=100, bonus_def=4, slot_equip="m_ter",nivel=1),
    "Pá": Item(nome='Pá', tipo='Equipavel', preco=100, slot_equip="m_ter", nivel=1),
    "Enchada": Item(nome='Enchada', tipo='Equipavel', preco=100, slot_equip="m_ter", nivel=1),
    'Machado/Pedra': Item(nome='Machado/Pedra', tipo='Equipavel', preco=100, bonus_atk=4, slot_equip="m_ter", nivel=1),
    'Machado/Madeira': Item(nome='Machado/Madeira', tipo='Equipavel', preco=100, bonus_atk=2, slot_equip="m_ter", nivel=1),
    ##CONS
    "Fruta": Item(nome="Fruta", tipo="Consumivel", preco=50, bonus_hp=25, bonus_stm=25),
    'Bolo de Milho': Item(nome="Bolo de Milho", tipo="Consumivel", preco=50, bonus_hp=25, bonus_stm=25),
    "Elixir": Item(nome="Elixir", tipo="Consumivel", preco=50, bonus_mana=50),
    "Suco": Item(nome="Suco", tipo="Consumivel", preco=50, bonus_stm=50),
    "Pão": Item(nome="Pão", tipo="Consumivel", preco=50, bonus_hp=50, bonus_stm=50),
    "Torta de Abobora": Item(nome="Torta de Abobora", tipo="Consumivel", preco=50, bonus_hp=100, bonus_stm=50),
    'Poção de Cura': Item(nome="Poção de Cura", tipo="Consumivel", preco=100, bonus_hp=int(100*0.5)),
    ##ARDUR
    "Peitoral": Item(nome="Peitoral", tipo="Equipavel", preco=150, bonus_def=5, bonus_hp_max=50,slot_equip="p_pet"),
    "Elmo/Ferro": Item(nome="Elmo/Ferro", tipo="Equipavel", preco=100, bonus_def=2, bonus_hp_max=25,slot_equip="c_cap"),
    ##Chaves
    "Chave": Item(nome='Chave', tipo="Chave", preco=0, vendivel=False, comprável=False),
    "Chave do Dragão": Item(nome='Chave do Dragão', tipo="Chave", preco=0, vendivel=False, comprável=False),
    ##Coletaveis
    "Madeira": Item(nome="Madeira", tipo="Material", slot_equip="slots"),
    "Chão": Item(nome="Chão", tipo="Material", slot_equip="slots"),
    "Porta": Item(nome="Porta", tipo="Material", slot_equip="slots"),
    "Bau": Item(nome="Bau", tipo="Material", slot_equip="slots"),
    "Pedra": Item(nome="Pedra", tipo="Material", slot_equip="slots"),
    "Bancada": Item(nome="Bancada", tipo="Material", slot_equip="slots"),
    "Semente/Trigo": Item(nome="Semente/Trigo", tipo="Material", slot_equip="slots"),
    "Semente/Abobora": Item(nome="Semente/Abobora", tipo="Material", slot_equip="slots"),
    "Semente/Milho": Item(nome="Semente/Milho", tipo="Material", slot_equip="slots"),
    'Muda/Arvore': Item(nome="Muda/Arvore", tipo="Material", slot_equip="slots"),
    'Semente/Arbusto': Item(nome="Semente/Arbusto", tipo="Material", slot_equip="slots"),
    'Forja': Item(nome="Forja", tipo="Material", slot_equip="slots"),

    ##Produtors
    "Trigo": Item(nome="Trigo", tipo="Produto", preco=10),
    "Milho": Item(nome="Milho", tipo="Produto", preco=25,),
    "Graveto": Item(nome="Graveto", tipo="Produto"),
    "Carvão": Item(nome="Carvão", tipo="Produto"),
    "Ferro": Item(nome="Ferro", tipo="Produto"),
    "Abobora": Item(nome="Abobora", tipo="Produto", preco=50),
    "Barra/Ferro": Item(nome="Barra/Ferro", tipo="Produto"),
}


class CraftRecipe:
    def __init__(self, nome_item, materiais, quantidade=1):
        self.nome_item = nome_item
        self.materiais = materiais
        self.quantidade = quantidade

RECEITAS_EQUIPAMENTOS = {
    'Espada': CraftRecipe('Espada',{'Madeira': 5, 'Graveto': 4}),
    'Pá': CraftRecipe('Pá',{'Madeira': 10, 'Graveto': 5}),
    'Enchada': CraftRecipe('Enchada',{'Pedra':5 , 'Graveto': 5}),
    'Picareta/Madeira': CraftRecipe('Picareta/Madeira',{'Madeira': 5, 'Graveto': 4}),
    'Machado/Madeira': CraftRecipe('Machado/Madeira',{'Madeira': 5, 'Graveto': 4}),
    'Picareta/Pedra': CraftRecipe('Picareta/Pedra',{'Pedra': 5, 'Graveto': 4}),
    'Machado/Pedra': CraftRecipe('Machado/Pedra',{'Pedra': 5, 'Graveto': 4}),
    'Elmo/Ferro': CraftRecipe('Elmo/Ferro', {'Barra/Ferro': 10}),
    'Peitoral': CraftRecipe('Peitoral', {'Barra/Ferro': 25}),
}

RECEITAS_MATERIAIS = {
    'Bau': CraftRecipe('Bau', {'Madeira': 5, 'Pedra': 1}),
    'Porta': CraftRecipe('Porta', {'Madeira': 6}),
    'Chão': CraftRecipe('Chão', {'Madeira': 2}, quantidade=4),
    'Forja': CraftRecipe('Forja', {'Pedra': 5, 'Carvão': 5}),
    'Graveto': CraftRecipe('Graveto', {'Madeira': 2}, quantidade=4),
    'Semente/Trigo': CraftRecipe('Semente/Trigo', {'Trigo':1}, quantidade=3),
    'Semente/Abobora': CraftRecipe('Semente/Abobora', {'Abobora':1}, quantidade=3),
    'Semente/Milho': CraftRecipe('Semente/Milho', {'Milho':1}, quantidade=3),
}

RECEITAS_CONSUMIVEIS = {
    'Pão': CraftRecipe('Pão',{'Trigo':3}),
    'Bolo de Milho': CraftRecipe('Bolo de Milho',{'Milho':5}),
    'Torta de Abobora': CraftRecipe('Torta de Abobora',{'Trigo':3, 'Abobora':1}),

}

class magias:
    def __init__(self, nome, tipo, bonus_hp=0, bonus_atk=0, bonus_def=0, bonus_stm=0, batalhas=False, mana_gasta=0, xp=0):
        self.nome = nome
        self.tipo = tipo
        self.bonus_hp = bonus_hp
        self.bonus_atk = bonus_atk
        self.bonus_def = bonus_def
        self.bonus_stm = bonus_stm
        self.batalhas = batalhas
        self.mana_gasta = mana_gasta
        self.xp = xp

    def __repr__(self):
        return f"magias(nome='{self.nome}', tipo='{self.tipo}')"

TODAS_AS_MAGIAS = {
    "Cura Leve": magias(nome="Cura Leve", tipo="Cura", bonus_hp=20, mana_gasta=10, xp=5),
    "Benção da Natureza": magias(nome="Benção da Natureza", tipo="Cura", bonus_hp=50, bonus_stm=10, mana_gasta=25, xp=10),
    "Tempestade de Raios": magias(nome="Tempestade de Raios", tipo="Ataque", bonus_atk=30, batalhas=True, mana_gasta=30, xp=10),
    "Bola de Fogo": magias(nome="Bola de Fogo", tipo="Ataque", bonus_atk=15, batalhas=True, mana_gasta=15, xp=5),
}