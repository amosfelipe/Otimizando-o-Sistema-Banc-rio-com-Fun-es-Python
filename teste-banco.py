import os
import pytz
from datetime import datetime, timedelta, timezone

# Funções de Manipulação de Usuários e Contas
def salvar_usuarios(usuarios, arquivo="usuarios.txt"):
    with open(arquivo, "w") as f:
        for cpf, dados in usuarios.items():
            linha = f"{cpf},{dados['nome']},{dados['data_nascimento']},{dados['endereco']}\n"
            f.write(linha)
            print("Diretório atual:", os.getcwd())

def carregar_usuarios(arquivo="usuarios.txt"):
    usuarios = {}
    try:
        with open(arquivo, "r") as f:
            
            for linha in f:
                linhas = linha.strip().split(",")
                if len(linhas) == 4:
                    cpf, nome, data_nascimento, endereco = linhas
                    usuarios[cpf] = {
                    "nome": nome,
                    "data_nascimento": data_nascimento,
                    "endereco": endereco
                }
    except FileNotFoundError:
        print("Arquivo de usuários não encontrado, iniciando com lista vazia.")
    
    return usuarios

def criar_usuario(usuarios):
    cpf = input("Digite o CPF (apenas números): ")
    if cpf in usuarios:
        print("Usuário já existe com este CPF!")
        return usuarios

    nome = input("Digite o nome: ")
    data_nascimento = input("Digite a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Digite o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuarios[cpf] = {
        "nome": nome,
        "data_nascimento": data_nascimento,
        "endereco": endereco
    }
    
    salvar_usuarios(usuarios)
    print("Usuário cadastrado com sucesso!")
    return usuarios

def salvar_contas(contas, arquivo="contas.txt"):
    with open(arquivo, "w") as f:
        for conta in contas:
            linha = f"{conta['agencia']},{conta['numero_conta']},{conta['usuario']}\n"
            f.write(linha)

def carregar_contas(arquivo="contas.txt"):
    contas = []
    try:
        with open(arquivo, "r") as f:
            for linha in f:
                agencia, numero_conta, usuario = linha.strip().split(",")
                contas.append({
                    "agencia": agencia,
                    "numero_conta": numero_conta,
                    "usuario": usuario
                })
    except FileNotFoundError:
        print("Arquivo de contas não encontrado, iniciando com lista vazia.")
    
    return contas

def criar_conta_corrente(contas, usuarios):
    cpf = input("Digite o CPF do usuário: ")
    if cpf not in usuarios:
        print("Usuário não encontrado. Por favor, registre o usuário antes de criar uma conta.")
        return contas
    
    numero_conta = str(len(contas) + 1).zfill(4)
    agencia = "0001"

    conta = {
        "agencia": agencia,
        "numero_conta": numero_conta,
        "usuario": cpf
    }
    
    contas.append(conta)
    salvar_contas(contas)
    print(f"Conta {numero_conta} criada com sucesso para o usuário {usuarios[cpf]['nome']}!")
    return contas

def validar_login(usuarios):
    cpf = input("Digite seu CPF: ")
    if cpf in usuarios:
        print(f"Bem-vindo(a), {usuarios[cpf]['nome']}!")
        return cpf
    else:
        print("Usuário não encontrado. Por favor, crie um usuário.")
        return None

# Funções de Depósito, Saque e Exibir Extrato
def depositar(saldo, extrato):
    data = datetime.now(pytz.timezone("America/Sao_Paulo"))
    mascara_ptbr = "%d/%m/%Y %H:%M"
    valor = float(input("Informe o valor para depósito: "))
    if valor > 0:
        saldo += valor
        extrato += f"Depósito: R$ {valor:.2f} {data.strftime(mascara_ptbr)}\n"
    else:
        print("Valor inválido para depósito")
    return saldo, extrato

def sacar(saldo, limite, LIMITE_SAQUE, numero_saque, extrato):   
    data = datetime.now(pytz.timezone("America/Sao_Paulo"))
    mascara_ptbr = "%d/%m/%Y %H:%M"
    valor = float(input("Informe o valor para saque: "))
    if valor > 0:
        excede_saldo = valor > saldo
        excedeu_limite = valor > limite
        excede_saque = numero_saque >= LIMITE_SAQUE
        
        if excede_saldo:
            print("Operação falhou! Você não tem saldo suficiente.")
        elif excedeu_limite:
            print("Operação falhou! O valor do saque excede o limite permitido.")
        elif excede_saque:
            print(f"Operação falhou! Número máximo de {LIMITE_SAQUE} saques excedido.")
        else:
            saldo -= valor
            extrato += f"Saque: R$ {valor:.2f} {data.strftime(mascara_ptbr)}\n"
            numero_saque += 1
    else:
        print("Operação falhou! O valor informado é inválido.")
    return saldo, limite, LIMITE_SAQUE, numero_saque, extrato

def exibir_extrato(saldo, extrato, data, mascara_ptbr):
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo: R$ {saldo:.2f} {data.strftime(mascara_ptbr)}")
    print("==========================================")

# Tela de Login e Registro
def tela_login(usuarios, contas):
    while True:
        print("""
        ======= Sistema Bancário =======
        [1] Criar Usuário (Cliente)
        [2] Criar Conta Corrente
        [3] Login
        [4] Sair
        """)
        
        opcao = input("Escolha uma opção desejada (1-4): ")
        if opcao == "1":
            usuarios = criar_usuario(usuarios)
        elif opcao == "2":
            contas = criar_conta_corrente(contas, usuarios)
        elif opcao == "3":
            cpf = validar_login(usuarios)
            if cpf:
                return cpf
        elif opcao == "4":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Tela de Operações Bancárias
def tela_operacoes(usuarios, contas, cpf):
    conta_corrente = next((conta for conta in contas if conta['usuario'] == cpf), None)
    if not conta_corrente:
        print("Usuário não possui conta corrente cadastrada.")
        return
    
    saldo = 0
    numero_saque = 0
    extrato = ""
    limite = 500
    LIMITE_SAQUE = 10

    data = datetime.now(pytz.timezone("America/Sao_Paulo"))
    mascara_ptbr = "%d/%m/%Y %H:%M"

    while True:
        print(f"""
        ======= Operações Bancárias =======
        Conta: {conta_corrente['numero_conta']}
        Agência: {conta_corrente['agencia']}

        [1] Depositar
        [2] Sacar
        [3] Extrato
        [4] Sair
        """)
        
        opcao = input("Escolha uma opção desejada (1-4): ")
        if opcao == "1":
            saldo, extrato = depositar(saldo, extrato)
        elif opcao == "2":
            saldo, limite, LIMITE_SAQUE, numero_saque, extrato = sacar(saldo, limite, LIMITE_SAQUE, numero_saque, extrato)
        elif opcao == "3":
            exibir_extrato(saldo, extrato, data, mascara_ptbr)
        elif opcao == "4":
            print("Saindo das operações bancárias...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Função Principal
def main():
    usuarios = carregar_usuarios()
    contas = carregar_contas()

    while True:
        cpf = tela_login(usuarios, contas)
        if cpf:
            tela_operacoes(usuarios, contas, cpf)
        else:
            break

if __name__ == "__main__":
    main()
