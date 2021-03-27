#!/usr/bin/python3
# Breakpoint Magick - Get VS Code Breakpoints
#
# Helps to convert breakpoints from VS Code to a format accepted in an external
# debugger. The advantage of setting breakpoints in VS Code is that they are
# dynamic, so they move up and down with the code as lines are removed or
# inserted.

import os
import glob
import sqlite3
import json
import collections

BreakpointTuple = collections.namedtuple('Breakpoint', ['file', 'line', 'enabled'])

def GetVSCodeBreakpoints():
    # VS Code saves breakpoints in a SQLite3 database, in the table ItemTable,
    # with key='debug.breakpoint', and value=JSON_DATA.
    # The databases can be found in:
    #     Windows %APPDATA%\Code\User\workspaceStorage\*\state.vscdb
    #     Linux   $HOME/.config/Code/User/workspaceStorage/*/state.vscdb

    break_point_list = list()

    # OS dependent path for databases
    if os.name == 'nt':
        path_breakpoints = os.getenv('APPDATA') + r'\Code\User\workspaceStorage\*\state.vscdb'
    elif os.name == 'posix':
        path_breakpoints = os.getenv('HOME') + r'/.config/Code/User/workspaceStorage/*/state.vscdb'
    else:
        raise Exception('Unknown os.name: "%s"' % os.name)

    # Open all the state.vscdb SQLite3 databases and output breakpoint data to
    # the list 'break_point_list'
    for file_path in glob.glob(path_breakpoints):
        with sqlite3.connect(file_path) as con:
            # Read SQLite3 database
            cur = con.cursor()
            cur.execute("SELECT value FROM ItemTable where key='debug.breakpoint'")
            res = cur.fetchall()
            for tuple_json_data in res:
                # Read JSON_DATA
                for json_data in tuple_json_data:
                    brk_list = json.loads(json_data)
                    # Process breakpoints
                    for brk in brk_list:
                        # Add each breakpoint to the list 'break_point_list'
                        brk_path = brk['uri']['path']
                        brk_line = brk['lineNumber']
                        brk_en = brk['enabled']
                        if os.name == 'nt':
                            # Fix path for Windows: remove prefixed backslash
                            brk_path = brk_path[1:]
                        brk_tuple = BreakpointTuple(brk_path, brk_line, brk_en)
                        break_point_list.append(brk_tuple)

    return break_point_list

if __name__ == '__main__':
    # Get a list with breakpoints
    break_point_list = GetVSCodeBreakpoints()

    # Dummy example of processing into new format
    print("# Breakpoints")
    for brk in break_point_list:
        file_name = brk.file.replace('"', '\\"')
        file_line = brk.line
        enabled = 'Enabled' if brk.enabled else 'Disabled'
        print("SetBreakpoint \"%s\" %d %s" % (file_name, file_line, enabled))
