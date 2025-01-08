# No DPI [ver. 1.2]
Uses simple SSL fragmentation to avoid DPI.
No system privileges needed.

Alternatives: [GoodbyeDPI](https://github.com/ValdikSS/GoodbyeDPI)

## How to install

Requires: Python >= 3.8

1) Download file nodpi.py and run `python3 nodpi.py` or open nodpi.py file
2) Configure browser to use proxy on 127.0.0.1:8881
![browser setting](nodpi_browser_setting.png)

## Known Bugs

- Doesn't bypass IP block
- Only TCP
- Doesn't work for HTTP only
- Not working with sites with old TLS
