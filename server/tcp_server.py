from twisted.internet import protocol, reactor, endpoints
from twisted.protocols import basic

class ServerProtocol(basic.LineReceiver):

    delimiter = '\n'

    def lineReceived(self, msg):
        self.transport.loseConnection()

server_endpoint = endpoints.serverFromString(reactor, "tcp:50000")
server_endpoint.listen(protocol.Factory.forProtocol(ServerProtocol))
reactor.run()
