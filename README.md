Some people use legacy paper-based advent calendar technology, but I use
cloud-based time tracking technology.

Downloading http://curlmas.dbatley.com/ will finish on Christmas morning, and
the progress bar of `curl` gives the percentage of advent which has happened.


Usage
=====

Run with
`python3 curlmas.py`


Test with a webbrowser or:
```sh
(echo $'GET / HTTP/1.1\r\n\r\n' && cat) | nc localhost 2525
```


About the code
==============

License: GPLv3 or later

SVG images from: https://openclipart.org/ (cc-zero)

This is a silly thing hacked together quickly, it probably has lots of bugs.

It currently sends one byte every 5 seconds, which means the total size is
about 500 KB. If you include the tcp packet headers, etc, it would be about
64 times that size (32MB).
