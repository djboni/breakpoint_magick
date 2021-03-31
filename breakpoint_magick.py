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
import re

BreakpointTuple = collections.namedtuple('Breakpoint', ['file', 'line', 'enabled', 'hit_count', 'cond'])

def GetVSCodeBreakpoints():
    # VS Code uses file names and lines of the files to set breakpoints.
    #
    # This function outputs a list of tuples that contain breakpoint information
    # extracted form VS Code.
    #
    # VS Code saves breakpoints in a SQLite3 database, in the table ItemTable,
    # with key='debug.breakpoint', and value=JSON_DATA.
    # The databases can be found in:
    #     Windows %APPDATA%\Code\User\workspaceStorage\*\state.vscdb
    #     Linux   $HOME/.config/Code/User/workspaceStorage/*/state.vscdb

    breakpoint_list = list()

    # OS dependent path for databases
    if os.name == 'nt':
        path_breakpoints = os.getenv('APPDATA') + r'\Code\User\workspaceStorage\*\state.vscdb'
    elif os.name == 'posix':
        path_breakpoints = os.getenv('HOME') + r'/.config/Code/User/workspaceStorage/*/state.vscdb'
    else:
        raise Exception('Unknown os.name: "%s"' % os.name)

    # Open all the state.vscdb SQLite3 databases and output breakpoint data to
    # the list 'breakpoint_list'
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
                        # Add each breakpoint to the list 'breakpoint_list'
                        brk_path = brk['uri']['path']
                        if os.name == 'nt':
                            # Fix path for Windows: remove prefixed backslash
                            brk_path = brk_path[1:]

                        brk_line = brk['lineNumber']
                        brk_en = brk['enabled']

                        if 'hitCondition' in brk:
                            brk_hit = int(brk['hitCondition'])
                        else:
                            brk_hit = None

                        if 'condition' in brk:
                            brk_cond = brk['condition']
                        else:
                            brk_cond = None

                        brk_tuple = BreakpointTuple(brk_path, brk_line, brk_en, brk_hit, brk_cond)
                        breakpoint_list.append(brk_tuple)

    return breakpoint_list

def SetTrace32Breakpoints(breakpoint_list):
    # TRACE32 uses function names and lines of the functions to set breakpoints.
    #
    # This function outputs a string that contain breakpoint information in
    # TRACE32 language (named PRACTICE).
    #
    # This function converts (file,file_line) breakpoints into
    # (function,func_line) and writes breakpoints to TRACE32 language.

    trace32_breakpoint_str = 'Break.RESet\n'

    # Regex to process files
    # Accept only .C source files
    accepted_files_regex = r'''.*?\.[cC]$'''
    accepted_files_regex = re.compile(accepted_files_regex)

    # Regex to find function definition
    #                     Function Return Ptr*   FunctionName   (args   )    {
    func_def_regex = r'''^([a-zA-Z0-9_]+[\s\*]+)+([a-zA-Z0-9_]+)\([^\)]*\)\s*\{'''
    func_def_regex = re.compile(func_def_regex, re.DOTALL)

    # For each breakpoint
    for brk in breakpoint_list:

        if accepted_files_regex.match(brk.file) == None:
            # Do not process this type of file
            print('Ignoring file: %s' % brk.file)
            continue

        # Read file
        with open(brk.file, 'r') as fp:
            source_lines = fp.readlines()

        # Find function definition using regex
        function_source = ''
        for i in range(brk.line - 1, -1, -1):
            function_source = source_lines[i] + function_source
            res = func_def_regex.match(function_source)
            if res != None:
                break
        else:
            s = "Function not found for %s" % str(brk)
            raise Exception(s)

        # Get function name and line number
        function_name = res.group(2)
        function_line = brk.line -1 - i - res.group(0).count('\n')
        function_line = '' if function_line == 0 else ("\\%d" % function_line)
        enabled = '' if brk.enabled else " /DISable"
        hit_count = '' if brk.hit_count == None else (" /COUNT %d." % brk.hit_count)
        cond = '' if brk.cond == None else (" /VarCONDition (%s)" % brk.cond)

        trace32_breakpoint_str += """Break.Set %s%s /Program%s%s%s\n""" % (function_name, function_line, enabled, hit_count, cond)

    return trace32_breakpoint_str

if __name__ == '__main__':
    # Get a list with breakpoints
    breakpoint_list = GetVSCodeBreakpoints()

    if True:
        # Convert to TRACE32 breakpoints
        trace32_breakpoint_str = SetTrace32Breakpoints(breakpoint_list)
        print(trace32_breakpoint_str)
    else:
        # Dummy example of processing to new format
        print("# Breakpoints")
        for brk in breakpoint_list:
            file_name = brk.file.replace('"', '\\"')
            file_line = brk.line
            enabled = 'Enabled' if brk.enabled else 'Disabled'
            hit_count = brk.hit_count
            cond = brk.cond
            if cond != None:
                cond = cond.replace('"', '\\"')

            if hit_count != None and cond != None:
                print("SetBreakpointHitCountCondition \"%s\" %d %s %d \"%s\"" % (file_name, file_line, enabled, hit_count, cond))
            elif hit_count != None:
                print("SetBreakpointHitCount \"%s\" %d %s %d" % (file_name, file_line, enabled, hit_count))
            elif cond != None:
                print("SetBreakpointCondition \"%s\" %d %s \"%s\"" % (file_name, file_line, enabled, cond))
            else:
                print("SetBreakpoint \"%s\" %d %s" % (file_name, file_line, enabled))
