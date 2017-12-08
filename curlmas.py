import gevent
import gevent.monkey; gevent.monkey.patch_all()
from gevent.server import StreamServer
import logging
import time
import datetime
import re
import itertools

DAYS_IN_ADVENT = 24
SECONDS_PER_DAY = 24 * 60 * 60
SECONDS_IN_ADVENT = DAYS_IN_ADVENT * SECONDS_PER_DAY

SEND_FREQUENCY = 5
CONTENT_LENGTH = SECONDS_IN_ADVENT // SEND_FREQUENCY
DAY_CONTENT_LENGTH = SECONDS_PER_DAY // SEND_FREQUENCY

global_ids=itertools.count(0)
def read_svg(filename):
	with open(filename, 'r', encoding='utf8') as f:
		contents = f.read()
	for non_unique_id in re.findall(r'id="([^"]+)"', contents):
		contents = contents.replace(non_unique_id, "gl{}".format(next(global_ids)))
	out = re.sub(r"\s+", " ", contents)
	assert len(out) < DAY_CONTENT_LENGTH, filename
	return out

def make_page():
	svgnames = [
		"openclipart/Anonymous-Christmas-tree.svg",
		"openclipart/cfry-Holly.svg",
		"openclipart/karderio-Christmas-pudding.svg",
		# "openclipart/Purple-present.svg",
		# "openclipart/Snowflakes-Arvin61r58.svg",
		"openclipart/TheresaKnott-Santa-Hat.svg",
		# "openclipart/Wreath.svg",
		"openclipart/zeimusu-Santa-line-art.svg",
	]

	content = [
		('CURLmas: download at the same rate as christmas<br><br>Better than any normal advent calendar.<br><br><pre>curl --progress-bar curlmas.dbatley.com &gt; /dev/null\nwget -O- curlmas.dbatley.com &gt; /dev/null</pre><style>div{display:none}</style>', ''),
	] + [
		('<div id="d{nextday}"><h2>Day {nextday}</h2>{svg}</div>'.format(nextday=day+1, svg=read_svg(svgname)),
			'<style>#d{nextday}{{display:block}} #d{day}{{display:none}}</style>'.format(nextday=day+1, day=day))
		for (day, svgname) in zip(range(2, 24), itertools.cycle(svgnames))
	] + [
		('<div id="d{nextday}"><h2>Merry Christmas</h2>{svg}</div>'.format(nextday=25, svg=read_svg('openclipart/Anonymous-Christmas-tree.svg')),
			'<style>#d{nextday}{{display:block}} #d{day}{{display:none}}</style>'.format(nextday=25, day=24))
	]
	content = [(prefix.encode("utf8"), suffix.encode("utf8")) for (prefix, suffix) in content]
	assert len(content) == DAYS_IN_ADVENT

	return b"".join(
		prefix
		+ (b" " * (DAY_CONTENT_LENGTH - len(prefix) - len(suffix)))
		+ suffix
		for prefix, suffix in content)

PAGE = make_page()
assert len(PAGE) == CONTENT_LENGTH

def handle_connection(sock, address):
	consume_http_headers(sock, address)

	# handle values outside of the range by sending entire page
	expired_seconds = seconds_since_dec_1()
	if expired_seconds < 0 or expired_seconds > SECONDS_IN_ADVENT:
		expired_seconds = SECONDS_IN_ADVENT

	serve_curlmas(sock, expired_seconds)

def consume_http_headers(sock, address):
	sockf = sock.makefile()
	for line in sockf:
		if not line.strip():
			break
		logging.debug("recv line from %r: %r", address, line)

def serve_curlmas(sock, expired_seconds):
	# send
	sock.sendall(b"HTTP/1.1 200 OK\r\n")
	sock.sendall("Content-length: {:d}\r\n".format(CONTENT_LENGTH).encode("ascii"))
	sock.sendall(b"Connection: keep-alive\r\n")
	sock.sendall(b"Content-type: text/html\r\n")
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
	# now = datetime.datetime(now.year, 12, 3, 23, 59, 45)
	# now = datetime.datetime(now.year, 12, 25, 12, 0, 0)
	timedelta = now - datetime.datetime(now.year, 12, 1, 0, 0, 0)
	return int(timedelta.total_seconds())

if __name__=='__main__':
	main()

