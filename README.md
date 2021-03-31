# Breakpoint Magick

Get a list with VS Code breakpoints.

This can help you to convert breakpoints from VS Code to a format accepted in an external debugger.

The advantage of setting breakpoints in VS Code is that they are dynamic, so they move up and down with the code as lines are removed or inserted.

# Real example

Convert VS Code breakpoints to TRACE32 breakpoints.

Copy and paste the breakpoints in TRACE32 to set them. You can also insert them in your CMM file.

```python
# Convert VS Code breakpoints to TRACE32 breakpoints
from breakpoint_magick import GetVSCodeBreakpoints
from breakpoint_magick import SetTrace32Breakpoints
breakpoint_list = GetVSCodeBreakpoints()
trace32_breakpoint_str = SetTrace32Breakpoints(breakpoint_list)
print(trace32_breakpoint_str)
```

Example output:

```
Break.RESet
Break.Set AES_ECBEncrypt /Program
Break.Set AES_ECBEncrypt\18 /Program
Break.Set AES_ECBDecrypt /Program
Break.Set AES_ECBDecrypt\16 /Program
```

# Dummy example

Convert VS Code breakpoints to a made-up language.

```python
# Import things
from breakpoint_magick import GetVSCodeBreakpoints

# Get a list with VS Code breakpoints
breakpoint_list = GetVSCodeBreakpoints()

# Example of processing to new format
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
```

Example output:

```
SetBreakpoint "DIR/source/aes.c" 467 Enabled
SetBreakpoint "DIR/source/aes.c" 485 Enabled
SetBreakpoint "DIR/source/aes.c" 531 Enabled
SetBreakpoint "DIR/source/aes.c" 547 Enabled
```
