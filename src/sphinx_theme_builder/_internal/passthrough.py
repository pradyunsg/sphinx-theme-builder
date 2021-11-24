"""CLI passthrough, on pty-supporting systems.

Based on code licensed as:

    Copyright (c) 2015-2017, Terminal Labs
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:
        * Redistributions of source code must retain the above copyright
        notice, this list of conditions and the following disclaimer.
        * Redistributions in binary form must reproduce the above copyright
        notice, this list of conditions and the following disclaimer in the
        documentation and/or other materials provided with the distribution.
        * Neither the name of Terminal Labs nor the
        names of its contributors may be used to endorse or promote products
        derived from this software without specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL TERMINAL LABS BE LIABLE FOR ANY
    DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
    ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Largely adapted from https://github.com/terminal-labs/cli-passthrough at commit
9337fbbaa59d12a1daaaba31a6dec9ce3107f8c7 (filename: cli_passthrough/_passthrough.py),
which in turn was adapted from StackOverflow.
"""

import sys
from typing import List

if sys.platform != "win32":
    import errno
    import fcntl
    import os
    import pty
    import shutil
    import struct
    import termios
    from itertools import chain
    from select import select
    from subprocess import Popen

    (_COLUMNS, _ROWS) = shutil.get_terminal_size(fallback=(80, 20))

    def _set_size(fd: int) -> None:
        """Found at: https://stackoverflow.com/a/6420070"""
        size = struct.pack("HHHH", _ROWS, _COLUMNS, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, size)

    def passthrough_run(args: List[str]) -> int:
        """Largely found in https://stackoverflow.com/a/31953436"""
        masters, slaves = zip(pty.openpty(), pty.openpty())
        for fd in chain(masters, slaves):
            _set_size(fd)

        with Popen(args, stdin=sys.stdin, stdout=slaves[0], stderr=slaves[1]) as p:
            for fd in slaves:
                os.close(fd)  # no input
            readable = {
                masters[0]: sys.stdout.buffer,  # store buffers separately
                masters[1]: sys.stderr.buffer,
            }
            while readable:
                for fd in select(readable, [], [])[0]:
                    try:
                        data = os.read(fd, 1024)  # read available
                    except OSError as e:
                        if e.errno != errno.EIO:
                            # time to clean up!
                            p.kill()
                            for fd in masters:
                                os.close(fd)
                            raise
                        del readable[fd]  # EIO means EOF on some systems
                    else:
                        if not data:  # EOF
                            del readable[fd]
                        else:
                            readable[fd].write(data)
                            readable[fd].flush()
        for fd in masters:
            os.close(fd)
        return p.returncode


else:
    import subprocess

    def passthrough_run(args: List[str]) -> int:
        p = subprocess.run(args)
        return p.returncode
