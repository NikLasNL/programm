from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def connectionMade(self):
        self.factory.clients.append(self)
        print(self.factory.clients)

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def lineReceived(self, line: bytes):
        content = line.decode()

        if self.login is not None:

            content = f"Messages from {self.login}: {content}"

            if content == "User" :
                self.sendLine("User Online" , self.factory.clients)

            for client in self.factory.clients:
                if client is not self:
                    client.sendLine(content.encode())

        else:
            #            (login:admin) -> admin
            if content.startswith("Login:"):
                self.login = content.replace("Login:", "")
                self.sendLine("Welcome!!!".encode())
            else:
                self.sendLine("Invalid Login!".encode())


            if content == "User" :
                self.sendLine("User Online" , self.factory.clients)



class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list

    def startFactory(self):
        self.clients = []
        super().startFactory()
        print("Server Started")

    def stopFactory(self):
        print("Server Closed")


reactor.listenTCP(1224, Server())
reactor.run()
