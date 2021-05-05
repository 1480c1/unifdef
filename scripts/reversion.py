#!/usr/bin/env python
# Copyright (c) 2021 Tony Finch <dot@dotat.at>

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

"""
mimic's reversion.sh
    accepts a sourcedir as argv[1], default is '.'
    accepts a outdir as argv[2], default is '.'
"""

import os
import subprocess
import re
import time
import sys
V = ''
D = ''

sourcedir = '.'
outdir = '.'

if len(sys.argv) == 3:
    if os.path.isdir(sys.argv[2]):
        outdir = sys.argv[2]
if len(sys.argv) >= 2:
    if os.path.isdir(sys.argv[1]):
        sourcedir = sys.argv[1]

versionsh = os.path.join(outdir, 'version.sh')
sourceversionsh = os.path.join(sourcedir, 'version.sh')
gitdir = os.path.join(sourcedir, '.git')

if not os.path.isdir(gitdir) and not os.path.isfile(sourceversionsh):
    print('Your copy of unifdef is incomplete', file=sys.stderr)
    exit(1)

with open(versionsh if os.path.isfile(versionsh)
          else sourceversionsh if os.path.isfile(sourceversionsh) else
          os.devnull) as f:
    for line in f:
        if line.startswith('V='):
            V = line.split('"')[1::2][0]
        if line.startswith('D='):
            D = line.split('"')[1::2][0]

if os.path.isdir(gitdir):
    GV = re.sub('-g*', '.',
                re.sub('[.]', '-',
                       subprocess.run(['git', 'describe'],
                                      cwd=sourcedir,
                                      capture_output=True,
                                      text=True,
                                      universal_newlines=True).stdout)).rstrip()
    subprocess.run(['git', 'update-index', '-q', '--refresh'], cwd=sourcedir)
    if not subprocess.run(['git', 'diff-index', '--quiet', 'HEAD'], cwd=sourcedir).returncode:
        GD = subprocess.run(['git', 'show', '--pretty=format:%ai', '-s', 'HEAD'], cwd=sourcedir,
                            capture_output=True, text=True, universal_newlines=True).stdout
    else:
        GD = time.strftime('%Y-%m-%d %H:%M:%S %z')
        GV += '.XX'
    unifdef = os.path.join(outdir, 'unifdef')
    unifdefc = os.path.join(sourcedir, 'unifdef.c')
    unifdefh = os.path.join(sourcedir, 'unifdef.h')
    if D != '' and os.path.exists(unifdef) and (
            os.path.getctime(unifdef) > os.path.getctime(unifdefc) and
            os.path.getctime(unifdef) > os.path.getctime(unifdefh)):
        GD = D
    if GV != V or GD != D:
        print('version {} {}'.format(V, D), file=sys.stderr)
        print('     -> {} {}'.format(GV, GD), file=sys.stderr)
        V = GV
        D = GD
        with open(versionsh, mode='w') as f:
            print('V="{}"'.format(V), file=f)
            print('D="{}"'.format(D), file=f)

with open(os.path.join(outdir, 'version.h'), mode='w') as f:
    print('"@(#) $Version: {} $\\n"'.format(V), file=f)
    print('"@(#) $Date: {} $\\n"'.format(D), file=f)
