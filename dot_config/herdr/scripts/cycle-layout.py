#!/usr/bin/env python3
"""Toggle the invoking Herdr tab between columns and rows."""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--session')
    parser.add_argument('--pane')
    parser.add_argument('--focused', action='store_true', help='Target the UI-focused pane for a keyboard shortcut')
    args = parser.parse_args()
    import logging
    logging.basicConfig(filename=str(Path(__file__).with_suffix('.log')), level=logging.INFO)
    logging.info('invoked pane=%s session=%s', os.environ.get('HERDR_PANE_ID'), os.environ.get('HERDR_SESSION'))
    cli = ['herdr'] + (['--session', args.session] if args.session else [])

    def call(*arguments):
        result = subprocess.run(cli + list(arguments), text=True, capture_output=True, check=True)
        return json.loads(result.stdout)['result']

    # Shell keybindings have session context but no pane environment.
    # Capture the focused pane once, then use explicit IDs for every mutation.
    target = (call('pane', 'current')['pane']['pane_id'] if args.focused
              else args.pane or os.environ.get('HERDR_PANE_ID'))
    if not target:
        raise RuntimeError('No invoking Herdr pane context')
    key = hashlib.sha256((args.session or os.environ.get('HERDR_SOCKET', '')).encode()).hexdigest()[:16]
    lock_dir = Path(os.environ.get('XDG_RUNTIME_DIR', str(Path.home() / '.cache'))) / 'herdr-layout'
    lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (lock_dir / (key + '.lock')).open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        layout = call('pane', 'layout', '--pane', target)['layout']
        panes = sorted(layout['panes'], key=lambda p: (p['rect']['y'], p['rect']['x']))
        if len(panes) < 2:
            return
        columns = len({p['rect']['y'] for p in panes}) == 1
        direction = 'down' if columns else 'right'
        if layout['zoomed']:
            call('pane', 'zoom', '--pane', target, '--off')
        anchor = panes[0]['pane_id']
        for index in range(len(panes) - 1, 0, -1):
            moved = call('pane', 'move', panes[index]['pane_id'], '--new-tab',
                         '--label', 'layout-transition', '--no-focus')['move_result']['pane']['pane_id']
            call('pane', 'move', moved, '--tab', layout['tab_id'],
                 '--target-pane', anchor, '--split', direction,
                 '--ratio', str(index / (index + 1)),
                 '--focus' if panes[index]['pane_id'] == layout['focused_pane_id'] else '--no-focus')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, KeyError) as error:
        import logging
        logging.exception('Layout shortcut failed')
        print(f'herdr-cycle-layout: {error}', file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError):
            print(error.stderr, file=sys.stderr)
        sys.exit(1)
