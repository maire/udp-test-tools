# Example communication
# C = client S = server
#
# TCP
#   C - start:1000
#   S - ok:55122
# UDP
#   C - start
#   S - 1
#   ...
#   S - 1000
#   S - done
# TCP
#   C - report:12

import socket
import threading
import time

def SpeedClient(tsock, addr):
  data = tsock.recv(4096)
  _, size = data.split(':')

  print 'connection from', addr

  # Open the UDP socket
  usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  usock.bind(('0.0.0.0', 0))

  # Send the UDP port for comms
  tsock.send('ok:{0}'.format(usock.getsockname()[1]))

  # Wait for UDP
  data, uaddr = usock.recvfrom(4096)

  # Send the speedtest data
  for i in range(int(size)):
    usock.sendto(str(i), uaddr)
    time.sleep(0.005)
  usock.sendto('done', uaddr)
  usock.close()

  tsock.send('done')

  # Get the report
  data = tsock.recv(4096)
  _, loss = data.split(':')

  tsock.close()
  print 'loss', loss, addr


class TCPSpeedServer(object):
  def __init__(self, addr):
    self.addr = addr
    self.sock = socket.socket()
    self.sock.bind(addr)

  def listen(self, bl):
    self.sock.listen(bl)
    while True:
      client, addr = self.sock.accept()
      t = threading.Thread(target=SpeedClient, args=(client, addr))
      t.start()

if __name__ == '__main__':
  server = TCPSpeedServer(('0.0.0.0', 42069))
  server.listen(2)
