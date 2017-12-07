import gevent
import gevent.monkey; gevent.monkey.patch_all()
from gevent.server import StreamServer
import logging
import time
import datetime

SECONDS_IN_ADVENT = 25 * 24 * 60 * 60
SEND_FREQUENCY = 60
CONTENT_LENGTH = SECONDS_IN_ADVENT // SEND_FREQUENCY
PAGE = b"." * CONTENT_LENGTH

def handle_connection(sock, address):
	consume_http_headers(sock, address)

	expired_seconds = seconds_since_dec_1()
	if expired_seconds < 0 or expired_seconds > SECONDS_IN_ADVENT:
		serve_error(sock, expired_seconds)
	else:
		serve_curlmas(sock, expired_seconds)

def consume_http_headers(sock, address):
	sockf = sock.makefile()
	for line in sockf:
		if not line.strip():
			break
		logging.debug("recv line from %r: %r", address, line)

def serve_error(sock, _expired_seconds):
	sock.sendall(b"HTTP/1.1 500 Server error\r\n")
	sock.sendall(b"\r\n")
	sock.sendall(b"It is not christmas.")
	sock.close()

def serve_curlmas(sock, expired_seconds):
	# send
	sock.sendall(b"HTTP/1.1 200 OK\r\n")
	sock.sendall("Content-length: {:d}\r\n".format(CONTENT_LENGTH).encode("ascii"))
	sock.sendall(b"Connection: keep-alive\r\n")
	sock.sendall("Keep-Alive: timeout={:d}\r\n".format(2 * SEND_FREQUENCY).encode("ascii"))
	sock.sendall(b"\r\n")

	expired_count = expired_seconds // SEND_FREQUENCY
	sock.sendall(PAGE[:expired_count])

	for index in range(expired_count, SECONDS_IN_ADVENT):
		sock.sendall(PAGE[index:index+1])
		time.sleep(SEND_FREQUENCY)

def main():
	logging.basicConfig(level=logging.DEBUG)
	server = StreamServer(('127.0.0.1', 2525), handle_connection)
	server.serve_forever()

def seconds_since_dec_1():
	now = datetime.datetime.now()
	timedelta = now - datetime.datetime(now.year, 12, 1, 0, 0, 0)
	return int(timedelta.total_seconds())

if __name__=='__main__':
	main()

