# TD Network Dumper v2.1
# https://github.com/tomorrow-lab-open/touchdesigner-analysis
#
# USAGE (in TouchDesigner Textport — Alt+T):
#   exec(open('C:/path/to/td_dump.py').read())
#
# OUTPUT: td-dump.json on your Desktop
#
# Dumps every operator, parameter, connection, script, table,
# and CHOP channel in your project to a single JSON file.
# Feed it to any AI (Claude, ChatGPT, Gemini) for instant analysis.

import json
import os
import datetime

# -------------------------------------------------------------------
# CONFIG — edit these if needed
# -------------------------------------------------------------------
ROOT_PATH = '/project1'          # Starting operator path
MAX_DEPTH = 15                   # How deep to recurse
OUTPUT_DIR = None                # None = Desktop, or set a path
SKIP_PATHS = ['/ui', '/local', '/sys', '/perform']  # TD internal paths

# -------------------------------------------------------------------
# CORE
# -------------------------------------------------------------------

def should_skip(path):
    for s in SKIP_PATHS:
        if path.startswith(s):
            return True
    return False


def dump_op(operator, depth=0):
    """Recursively dump an operator and all its children to a dict."""
    if depth > MAX_DEPTH:
        return None
    if should_skip(operator.path):
        return None

    info = {
        'name': operator.name,
        'path': operator.path,
        'type': operator.type,
        'family': operator.family,
    }

    # --- Non-default parameters ---
    params = {}
    for p in operator.pars():
        try:
            if not p.isDefault and p.mode == ParMode.CONSTANT:
                val = p.eval()
                if isinstance(val, (int, float, str, bool)):
                    params[p.name] = val
            elif p.mode == ParMode.EXPRESSION:
                params[p.name] = {'expr': p.expr, 'val': str(p.eval())}
        except:
            pass
    if params:
        info['params'] = params

    # --- Input connections ---
    inputs = []
    try:
        for i, conn in enumerate(operator.inputConnectors):
            for c in conn.connections:
                inputs.append({
                    'index': i,
                    'from': c.owner.path,
                    'from_output': c.index
                })
    except:
        pass
    if inputs:
        info['inputs'] = inputs

    # --- Output connections ---
    outputs = []
    try:
        for i, conn in enumerate(operator.outputConnectors):
            for c in conn.connections:
                outputs.append({
                    'index': i,
                    'to': c.owner.path,
                    'to_input': c.index
                })
    except:
        pass
    if outputs:
        info['outputs'] = outputs

    # --- DAT content (scripts + tables) ---
    if operator.family == 'DAT':
        try:
            if operator.isTable:
                rows = []
                for row in range(operator.numRows):
                    r = []
                    for col in range(operator.numCols):
                        r.append(operator[row, col].val)
                    rows.append(r)
                info['table'] = rows
            else:
                text = operator.text
                if text and len(text) < 50000:
                    info['text'] = text
        except:
            pass

    # --- CHOP channels ---
    if operator.family == 'CHOP':
        try:
            channels = []
            for chan in operator.chans():
                channels.append({'name': chan.name, 'val': chan.eval()})
            if channels:
                info['channels'] = channels
        except:
            pass

    # --- TOP resolution ---
    if operator.family == 'TOP':
        try:
            info['resolution'] = [operator.width, operator.height]
        except:
            pass

    # --- SOP point/prim count ---
    if operator.family == 'SOP':
        try:
            info['points'] = operator.numPoints
            info['prims'] = operator.numPrims
        except:
            pass

    # --- Children (COMPs only) ---
    if operator.isCOMP:
        try:
            children = []
            for child in operator.children:
                if not should_skip(child.path):
                    child_info = dump_op(child, depth + 1)
                    if child_info:
                        children.append(child_info)
            if children:
                info['children'] = children
        except:
            pass

    return info


# -------------------------------------------------------------------
# RUN
# -------------------------------------------------------------------

root = op(ROOT_PATH)
if root is None:
    print(f'ERROR: No operator found at {ROOT_PATH}')
    print('Change ROOT_PATH at the top of the script.')
else:
    result = dump_op(root)
    count = len(root.findChildren(depth=-1))

    output = {
        'tool': 'touchdesigner-analysis',
        'version': '2.1',
        'td_version': app.version,
        'file': project.name,
        'timestamp': str(datetime.datetime.now()),
        'operator_count': count,
        'network': result
    }

    # Determine output path
    if OUTPUT_DIR:
        out_dir = OUTPUT_DIR
    else:
        out_dir = os.path.join(os.path.expanduser('~'), 'Desktop')

    filename = f'td-dump-{project.name}.json'
    output_path = os.path.join(out_dir, filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str, ensure_ascii=False)

    print(f'')
    print(f'=== TD Network Dumper ===')
    print(f'Project:    {project.name}')
    print(f'Operators:  {count}')
    print(f'Output:     {output_path}')
    print(f'')
    print(f'Now feed the JSON to your AI:')
    print(f'  "Analyze this TouchDesigner network. What does it do?"')
    print(f'=========================')
