class Visitor(object):
    def visit(self, host):
        accepter = type(host).__name__
        if accepter == 'Protocol':
            return self.visitProtocol(host)
        if accepter == 'Interface':
            return self.visitInterface(host)
        if accepter == 'Enumeration':
            return self.visitEnumeration(host)
        if accepter == 'Structure':
            return self.visitStructure(host)
        if accepter == 'Signal':
            return self.visitSignal(host)
        if accepter == 'Method':
            return self.visitMethod(host)
        if accepter == 'Argument':
            return self.visitArgument(host)
        print('Unkown accepter %s' % accepter)
        return False

    def visitProtocol(self, protocol):
        pass

    def visitInterface(self, iface):
        pass

    def visitEnumeration(self, enum):
        pass

    def visitStructure(self, struct):
        pass

    def visitSignal(self, signal):
        pass

    def visitMethod(self, method):
        pass

    def visitArgument(self, arg):
        pass
