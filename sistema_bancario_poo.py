from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n Você não tem saldo suficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("\n Saque realizado com sucesso!")
            return True
        else:
            print("\n Valor inválido. Operação falhou!")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n Deposito realizado com sucesso!")
        else:
            print("\n Valor inválido. Operação falhou!")
            return False
        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [
                transacao for transacao in self.historico.transacoes
                if transacao["tipo"] == Saque.__name__
            ]
        )
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n Falha! Valor acima do limite permitido.")
        elif excedeu_saques:
            print("\n Falha! Número máximo de saques excedidos.")
        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"""
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo": transacao.__class__.__name__,
                "valor": transacao.valor,
                "data": datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            }
        )


class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass

    @abstractclassmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)


menu = """\n
    Bem-vindo ao Banco Digital!\n
    Escolha uma opção:
    [1] Sacar
    [2] Depositar
    [3] Visualizar Extrato
    [4] Criar cliente
    [5] Criar conta
    [6] Sair

    => """


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def verificar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n Cliente não possui conta.")
        return
    return cliente.contas[0]


def criar_cliente(clientes):
    cpf = input("Digite o seu CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if cliente:
        print("\n Já existe cliente com esse CPF!")
        return

    nome = input("Digite o seu nome: ")
    data_nascimento = input("Digite a data de nascimento (dd-mm-aaaa): ")
    endereco = input(
        "Digite o endereço (logradouro, nro - bairro - cidade/sigla estado): "
    )

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco
    )
    clientes.append(cliente)

    print("\nCliente criado com sucesso!")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Digite o CPF: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Não foi possível encontrar um cliente com este CPF.")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print("\n Conta criada com sucesso!")


def saque(clientes):
    cpf = input("Digite o CPF aqui:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Não foi possível encontrar um cliente com este CPF.")
        return

    valor = float(input("Digite o valor do saque: "))
    transacao = Saque(valor)
    conta = verificar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def deposito(clientes):
    cpf = input("Digite o CPF aqui:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Não foi possível encontrar um cliente com este CPF.")
        return

    valor = float(input("Digite o valor do deposito: "))
    transacao = Deposito(valor)
    conta = verificar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def extrato_final(clientes):
    cpf = input("Digite o CPF aqui:")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("\n Não foi possível encontrar um cliente com este CPF.")
        return

    conta = verificar_conta_cliente(cliente)
    if not conta:
        return

    print("\n========== Extrato ==============")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao["tipo"]}: \n\tR$ {transacao["valor"]:.2f}"

    print(extrato)
    print(f"\nSeu saldo atual é de R$ {conta.saldo:.2f}")
    print("==================================")


def main():
    clientes = []
    contas = [] 

    while True:
        opcao = int(input(menu))

        if opcao == 1:
            saque(clientes)
        elif opcao == 2:
            deposito(clientes)
        elif opcao == 3:
            extrato_final(clientes)
        elif opcao == 4:
            criar_cliente(clientes)
        elif opcao == 5:
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)
        elif opcao == 6:
            break
        else:
            print("Opção inválida, tente novamente.")


main()
