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
import six
import subprocess

from ansible import utils, errors
from ansible.plugins.lookup import LookupBase
from ansible.errors import AnsibleError

class LookupModule(LookupBase):

    COMMAND="pass"
    CREDENIAL_DIR="credentials"

#def __init__(self, basedir=None, **kwargs):
#        super(LookupModule, self).__init__()
#        self.basedir = basedir

    def run(self, terms, inject=None, variables=None, **kwargs):

        candidates = []
        basedir = self.get_basedir(variables)
        basepath = self._loader.path_dwim_relative(basedir, "", self.CREDENIAL_DIR)
        if basepath:
            candidates.append(basepath)

        if inject is not None and "playbook_dir" in inject:
            candidates.append(os.path.join(inject['playbook_dir'], self.CREDENIAL_DIR))

        keydir = None
        for candidate in candidates:
            if os.path.exists(candidate):
                keydir = candidate
                break
        if 'listify_lookup_plugin_terms' in globals():
            terms = utils.listify_lookup_plugin_terms(terms, self.basedir, inject) 

        if isinstance(terms, six.string_types):
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

            if keydir is None:
                raise AnsibleError("lookup_plugin.pass(%s) No 'credentials' dir found in playbook dir. candidates: %s" % (term, candidates))

            env = dict(os.environ)
            env["PASSWORD_STORE_DIR"] = keydir

            command = "%s %s" % (self.COMMAND, term)

            p = subprocess.Popen(command,
                    cwd=basedir,
                    shell=True,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env)

            (stdout, stderr) = p.communicate()
            if p.returncode == 0:
                ret.append(stdout.decode("utf-8").splitlines()[0].rstrip())
            else:
                err = stderr.decode("utf-8").rstrip()
                raise AnsibleError("lookup_plugin.pass(%s) returned %d: %s" % (term, p.returncode, err))
        return ret
