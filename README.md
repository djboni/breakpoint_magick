# Breakpoint Magick

Get a list with VS Code breakpoints.

This can help you to convert breakpoints from VS Code to a format accepted in an external debugger.

The advantage of setting breakpoints in VS Code is that they are dynamic, so they move up and down with the code as lines are removed or inserted.

# Example

```python
# Import things
from breakpoint_magick import GetVSCodeBreakpoints

# Get a list with VS Code breakpoints
break_point_list = GetVSCodeBreakpoints()

# Example of processing to new format
print("# Breakpoints")
for brk in break_point_list:
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
