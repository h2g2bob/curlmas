import gevent
import gevent.monkey; gevent.monkey.patch_all()
from gevent.server import StreamServer
import logging
import time
import datetime

SECONDS_IN_ADVENT = 25 * 24 * 60 * 60
SEND_FREQUENCY = 60
CONTENT_LENGTH = SECONDS_IN_ADVENT // SEND_FREQUENCY

def handle_connection(sock, address):
	sockf = sock.makefile()

	# consume http headers
	for line in sockf:
		if not line.strip():
			break
		logging.debug("recv line from %r: %r", address, line)

	# send
	sock.sendall(b"HTTP/1.1 200 OK\r\n")
	sock.sendall("Content-length: {:d}\r\n".format(CONTENT_LENGTH).encode("ascii"))
	sock.sendall(b"Connection: keep-alive\r\n")
	sock.sendall("Keep-Alive: timeout={:d}\r\n".format(2 * SEND_FREQUENCY).encode("ascii"))
	sock.sendall(b"\r\n")

	expired_count = seconds_since_dec_1() // SEND_FREQUENCY
	sock.sendall(b"." * expired_count)

	for _ in xrange(expired_count, SECONDS_IN_ADVENT):
		sock.sendall(b".")
		time.sleep(SEND_FREQUENCY)

def main():
	logging.basicConfig(level=logging.DEBUG)
	server = StreamServer(('127.0.0.1', 2525), handle_connection)
	server.serve_forever()

def seconds_since_dec_1():
	timedelta = datetime.datetime.now() - datetime.datetime(2017, 12, 1, 0, 0, 0)
	return int(timedelta.total_seconds())

if __name__=='__main__':
	main()

