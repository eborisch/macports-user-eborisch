#!/usr/bin/env python
#
# Author:
#  Eric A. Borisch <eborisch@macports.org>
#
# Copyright (c) 2016 Eric A. Borisch <eborisch@macports.org>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright owner nor the names of contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
Usage: update_checksums.py portname [port ...]
Performs checksum step and updates any incorrect values in specified port[s].
"""

from __future__ import print_function

import sys
import re

from subprocess import check_output, STDOUT, CalledProcessError

PORTFILE_PATTERN = re.compile(r'^Portfile checksum: .* ([0-9a-f]+)$')
DISTFILE_PATTERN = re.compile(r'^Distfile checksum: .* ([0-9a-f]+)$')


def create_sed_input(repls):
    "Takes dictionary of replacements and creates sed command strings."
    sed_input = []
    for k in repls.keys():
        sed_input.extend(['-e', 's/{}/{}/'.format(k, repls[k])])
    return tuple(sed_input)


def run_cmd(*args, **kwargs):
    "Wrapper around check_output with stderr redirected to stdout."
    return check_output(*args,
                        stderr=STDOUT,
                        universal_newlines=True,
                        **kwargs)


def run_sed(filename, commands):
    "Runs sed commands on filename in place (without backup.)"
    try:
        run_cmd(('sed', '-i', '') + commands + (filename,))
    except CalledProcessError as err:
        print("Error while updating portfile [{}]: [{}]".format(filename,
                                                                str(err)))
        print("Process output:")
        for line in err.output.split('\n'):
            print (">> " + line)


def get_portfile(portname):
    "Returns the path to the requested port's Portfile."
    return run_cmd(('port', 'file', portname)).strip()


def get_replacements(portname):
    """Checks the selected port for any checksums that need updating.

    Returns a dictionary of replacements[old] = new"""

    try:
        result = run_cmd(('port', '-v', 'checksum', portname))
    except CalledProcessError as err:
        if err.returncode != 1:
            raise
        result = err.output

    replacements = {}
    orig = None
    new = None
    for line in result.split('\n'):
        # port -v checksum lists first what is in the Portfile, and then what
        # the distfile's checksum actually is.
        if orig is None:
            orig = PORTFILE_PATTERN.match(line)
            if orig:
                orig = orig.group(1)
        elif new is None:
            new = DISTFILE_PATTERN.match(line)
            if new:
                new = new.group(1)

        if orig and new:
            replacements[orig] = new
            orig = None
            new = None
    return replacements


def process(portname):
    """
    Perform all actions required on specified port to update out-of date
    checksums.
    """
    portfile = get_portfile(portname)
    replacements = get_replacements(portname)
    sed_input = create_sed_input(replacements)
    if len(sed_input):
        print("Updating: " + portfile)
        run_sed(portfile, sed_input)
    else:
        print("No updates required: " + portfile)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage {} portname [port ...]".format(sys.argv[0]))
    for n in sys.argv[1:]:
        process(n)
