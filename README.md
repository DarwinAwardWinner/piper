# piper: Easily set up shell pipelines in Python

## Example

    from piper import CommandPipeline
    commands = [["command1", "arg"],
                ["command2", "arg"],
                ["command3", "arg", "another arg"]]
    p = CommandPipeline(commands)
    for line in p.stdout:
        print "Read a line: %s" % line
    p.close()
    if p.failed():
        raise Exception("Pipeline failed")


