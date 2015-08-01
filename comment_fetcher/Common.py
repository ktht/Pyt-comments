import sys

def handle_wrong_cmdargs(msg, action=None):
    sys.stderr.write(msg + "\n\n")
    if action is not None: action()
    sys.exit(2)

def print_if_verbose(msg, verbose, add_newline=True, flush=False):
    if verbose:
        sys.stdout.write(msg)
        if add_newline: sys.stdout.write('\n')
        if flush:       sys.stdout.flush()