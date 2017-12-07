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
	is_web_browser = False
	for line in sockf:
		if not line.strip():
			break
		if 'Firefox' in line or 'Chrome' in line or 'Safari' in line:
			is_web_browser = True
		logging.debug("recv line from %r: %r", address, line)

	expired_seconds = seconds_since_dec_1()

	if is_web_browser:
		serve_index(sock, expired_seconds)
	elif expired_seconds < 0 or expired_seconds > SECONDS_IN_ADVENT:
		serve_error(sock, expired_seconds)
	else:
		serve_curlmas(sock, expired_seconds)

def serve_error(sock, _expired_seconds):
	sock.sendall(b"HTTP/1.1 500 Server error\r\n")
	sock.sendall(b"\r\n")
	sock.sendall(b"It is not christmas.")
	sock.close()

def serve_index(sock, _expired_seconds):
	sock.sendall(b"HTTP/1.1 200 OK\r\n")
	sock.sendall(b"Content-type: text/plain\r\n")
	sock.sendall(b"\r\n")
	sock.sendall(b"CURLmas: download at the same rate as christmas\r\n")
	sock.sendall(b"\r\n")
	sock.sendall(b"Better than any normal advent calendar.\r\n")
	sock.sendall(b"\r\n")
	sock.sendall(b"curl --progress-bar curlmas.dbatley.com > /dev/null\r\n")
	sock.sendall(b"wget -O- curlmas.dbatley.com > /dev/null\r\n")
	sock.close()

def serve_curlmas(sock, expired_seconds):
	# send
	sock.sendall(b"HTTP/1.1 200 OK\r\n")
	sock.sendall("Content-length: {:d}\r\n".format(CONTENT_LENGTH).encode("ascii"))
	sock.sendall(b"Connection: keep-alive\r\n")
	sock.sendall("Keep-Alive: timeout={:d}\r\n".format(2 * SEND_FREQUENCY).encode("ascii"))
	sock.sendall(b"\r\n")

	expired_count = expired_seconds // SEND_FREQUENCY
	sock.sendall(b"." * expired_count)

	for _ in range(expired_count, SECONDS_IN_ADVENT):
		sock.sendall(b".")
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

