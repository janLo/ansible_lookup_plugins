# (c) 2012, Daniel Hokka Zakrisson <daniel@hozac.com>
# (c) 2015, Jan Losinski <losinski@wh2.tu-dresden.de>
#
# The original file was part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import subprocess

from ansible import utils, errors
from ansible.errors import AnsibleError

class LookupModule(object):

    COMMAND="pass"
    CREDENIAL_DIR="credentials"

    def __init__(self, basedir=None, **kwargs):
        self.basedir = basedir

    def run(self, terms, inject=None, **kwargs):

        terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject) 

        if isinstance(terms, basestring):
            terms = [ terms ] 

        ret = []
        for term in terms:
            '''
            http://docs.python.org/2/library/subprocess.html#popen-constructor

            The shell argument (which defaults to False) specifies whether to use the 
            shell as the program to execute. If shell is True, it is recommended to pass 
            args as a string rather than as a sequence

            https://github.com/ansible/ansible/issues/6550
            '''
            term = str(term)

            keydir = os.path.join(self.basedir, self.CREDENIAL_DIR)

            env = dict(os.environ)
            env["PASSWORD_STORE_DIR"] = keydir

            command = "%s %s" % (self.COMMAND, term)

            p = subprocess.Popen(command,
                    cwd=self.basedir,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env)

            (stdout, stderr) = p.communicate()
            if p.returncode == 0:
                ret.append(stdout.decode("utf-8").rstrip())
            else:
                err = stderr.decode("utf-8").rstrip()
                raise AnsibleError("lookup_plugin.pass(%s) returned %d: %s" % (term, p.returncode, err))
        return ret
