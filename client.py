import socket
import sys
import time

verbose = False
if sys.argv[1] == '-v':
  verbose = True
  sys.argv = sys.argv[1:]

size = int(sys.argv[1])

# TCP socket
taddr = (sys.argv[2], 42069)
tsock = socket.socket()
tsock.connect(taddr)

tsock.send('start:{0}'.format(size))

data = tsock.recv(4096)
_, uport = data.split(':')

# UDP socket
usock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
usock.connect((taddr[0], int(uport)))
usock.settimeout(2)
usock.sendall('ok')

current = 0
order = 0
count = 0

start = time.time()

while True:
  try:
    data = usock.recv(4096)
    if data == 'done':
      break
    count += 1

    # order test
    if int(current) > int(data):
      if verbose:
        print 'expected {0} got {1}'.format(int(current) + 1, data)
      order += 1

    current = data

    # seconds elapsed
    ctime = time.time() - start

    if verbose:
      # current progress as a float
      done = float(count) / size
      # estimed time left in minutes and seconds
      m, s = divmod((ctime / done) - ctime, 60)

      sys.stdout.write('\r{0:2.2f}% eta {1}:{2:02} '.format(
        done * 100, int(m), int(s)))
      sys.stdout.flush()
  except socket.timeout:
    break

usock.close()
if verbose:
  sys.stdout.write('\r' + ' '*15 + '\r')
  sys.stdout.flush()

data = tsock.recv(4096)
if 'done' in data:
  loss = size - count
  tsock.send('report:{0}'.format(loss))
  m, s = divmod(ctime, 60)
  if verbose:
    print 'time:  {0}:{1:02}'.format(int(m), int(s))
    print 'loss:  {0} ({1}%)'.format(loss, (float(loss) / size) * 100)
    print 'order: {0}'.format(order)
  else:
    print 't: {0}:{1:02} l: {2} ({3}%) o: {4}'.format(int(m), int(s), loss, (float(loss)/size) * 100, order)

tsock.close()
