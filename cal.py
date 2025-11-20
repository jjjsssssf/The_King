import random, sys, os
def clear():
	os.system("cls")
class id:
	def __init__(self, nome=str, idade=int, ativo=bool):
		self.nome = nome
		self.idade = idade
		self.idente = {
		"id_1": int(0),
		"id_2": int(0),
		"id_3": int(0)
		}
		self.ativo = ativo

	def info(self):
		print(f"Nome: [{self.nome}]")
		print(f"Idade: [{self.idade}]")
		for i, e in self.idente.items():
			print(f"id {i} {e}")
		print("")
		print(f"Ativo: [{self.ativo}]")

	def random_mize(self):
		nomes = random.choice(["Lucia", "Edinaldo", "Juraci", "Vardemar", "Vandesca"])
		idades =  random.randint(1, 50)
		id_1 = random.randint(1, 20)
		id_2 = random.randint(100, 500)
		id_3 = random.randint(50, 200)
		ativo_ = random.randint(0, 1)
		self.nome = nomes 
		self.idade = idades
		self.idente["id_1"] = id_1
		self.idente["id_2"] = id_2
		self.idente["id_3"] = id_3
		if ativo_ == 0:
			self.ativo = False
		elif ativo_ == 1:
			self.ativo = True

clear()
identificao = id(nome="", idade=0, ativo=None)
identificao.random_mize()
identificao.info()
input("")
