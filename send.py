#!/usr/bin/python
from PyQt5 import QtDBus, QtWidgets

class ServerIfc(QtDBus.QDBusAbstractInterface):

  def __init__(self, service, path, connection, parent=None):
      super(ServerIfc, self).__init__(service, path, 'cz.base48.Basebar.C', connection, parent)

  def newProductCode(self, code=None):
    if code is None:
      code = 'EAN-13:5901234123457'
      code = 'EAN-13:4029764001883'

    m = self.call('newProductCode', code)
    print m.errorMessage()

if __name__ == '__main__':
  import sys
  app = QtWidgets.QApplication(sys.argv)


  server = ServerIfc('cz.base48.Basebar', '/C',
            QtDBus.QDBusConnection.sessionBus())

  if len(sys.argv) == 1:
    server.newProductCode()
  elif sys.argv[1] == '-':
    while (not sys.stdin.closed):
      server.newProductCode(sys.stdin.readline().strip())
  else:
    server.newProductCode(sys.argv[1])

#  sys.exit(app.exec_())
