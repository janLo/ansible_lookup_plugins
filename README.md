Collection of custom ansible lookup modules
===========================================

## `pass` Module

This is a module to lookup a [pass](http://www.passwordstore.org/) password store located at `./credentials` from the toplevel playbook directory. It is a slightly modified [pipe](https://github.com/ansible/ansible/blob/stable-1.9/lib/ansible/runner/lookup_plugins/pipe.py) plugin.

It takes a password path within the pass storage as argument:

    - name: test pass lookup
      debug: msg={{ lookup('pass', 'path/to/password') }}


