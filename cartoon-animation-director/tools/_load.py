"""Shared loader for the read-only checkers. Imports an episode file WITHOUT rendering it.

Nothing here writes to the project. An episode is run with a module name other than '__main__', so its
`if __name__ == '__main__'` block (render, sheet) does not execute. As a second guard, Show.main and
Stage.render are replaced in memory for the duration of the load. No file on disk is changed.
"""
import contextlib, io, os, runpy, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ENGINE = os.path.join(ROOT, 'toon-slapstick', 'engine')
if ENGINE not in sys.path:
    sys.path.insert(0, ENGINE)


def load_stage(path):
    """Return (stage, namespace) for an episode or shot file."""
    import toon, show
    saved = (show.Show.main, toon.Stage.render, list(sys.argv))
    show.Show.main = lambda self, file: None
    toon.Stage.render = lambda self, *a, **k: None
    sys.argv = [path]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            ns = runpy.run_path(path, run_name='__checker__')
    finally:
        show.Show.main, toon.Stage.render, sys.argv = saved
    st = ns.get('st')
    if st is None and ns.get('ep') is not None:
        st = ns['ep'].st
    if st is None:
        cands = [v for v in ns.values() if isinstance(v, toon.Stage)]
        st = cands[0] if cands else None
    if st is None:
        raise SystemExit('no Stage found in %s (expected a variable named st or ep)' % path)
    return st, ns


def name_of(actor, ns):
    for k, v in ns.items():
        if v is actor and not k.startswith('_'):
            return k
    return type(actor).__name__
