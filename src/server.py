# Серверная часть для мессенджера
# 12/12/2019
# ver 1.1.0
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:
            content = f"Сообщение от {self.login}: {content}"

            self.factory.history.append(content)

            for user in self.factory.clients:
                user.sendLine(content.encode())
        else:
            # login:admin -> admin

            if content.startswith("login:"):
                login = content.replace("login:", "")

                for user in self.factory.clients:
                    if user.login == login:
                        self.sendLine("Введите другой логин!!!".encode())
                        return

                self.login = login
                self.factory.clients.append(self)
                self.factory.send_history(self)

            else:
                self.sendLine("Неверный логин".encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    history: list

    def startFactory(self):
        self.clients = []
        self.history = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")

    def send_history(self, client: ServerProtocol):
        client.sendLine("Добро пожаловать!".encode())

        last_messages = self.history[-10:]

        for msg in last_messages:
            client.sendLine(msg.encode())


reactor.listenTCP(1334, Server())
reactor.run()
