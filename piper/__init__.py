import os
import sys
from subprocess import Popen, PIPE, CalledProcessError

def fork_and_pump(input, handle):
    """Send input to handle in a child process.

This is needed to avoid deadlocks in bidirectional communication with
processes. In general, 'handle' should be int standard input of a
running command. This function forks a child process, and the child
reads lines from the iterable input and writes them to the handle.
When the input is exhausted, the child process closes the handle and
exits.

The child process ignores IOErrors, because they probably signify an
error somewhere else in the program."""
    if os.fork():
        # Parent
        handle.close()
    else:
        # Child
        try:
            handle.writelines(input)
            handle.close()
        # Ignore SIGPIPE
        except IOError, e:
            if e.errno == errno.EPIPE:
                # EPIPE error
                pass
        except KeyboardInterrupt:
            pass
        exit()

class CommandPipeline(object):
    """A class that sets up a pipeline of commands.

The constructor takes a list of commands, and an input source. Each
command should be a list of strings, so the command list is a list of
lists of strings. The input source can be anything that
subprocess.Popen will accept as the 'stdin' argument. Additionally,
the input may be any iterable, which will be assumed to yields lines
of input for the pipeline to consume. This iterable will be consumed
in a separate thread (by forking) in order to prevent deadlocks.

The commands in the list are started, and each command's standard
output is attached to the standard input of the succeeding command.
The standard output of the final command in the pipeline is available
from the 'stdout' property."""

    def __init__(self, command_list, input, suppress_stderr=True):
        assert len(command_list) >= 1
        if suppress_stderr:
            error_handle = open(os.devnull, "w")
        else:
            error_handle = sys.stderr
        commands = iter(command_list)
        first_command = next(commands)
        # The first proc needs special treatment to read from an input
        # iterable that isn't a file.
        try:
            first_proc = Popen(first_command, stdin=input, stdout=PIPE, stderr=error_handle)
        except:
            first_proc = Popen(first_command, stdin=PIPE, stdout=PIPE, stderr=error_handle)
            input_iterator = iter(input)
            fork_and_pump(input_iterator, first_proc.stdin)
        # Append the rest of the commands to the pipeline, chaining
        # inputs to outputs
        self.procs = [first_proc]
        for cmd in commands:
            next_proc = Popen(cmd, stdin=self.procs[-1].stdout, stdout=PIPE, stderr=error_handle)
            self.procs[-1].stdout.close()
            self.procs.append(next_proc)
        # The last proc's stdout is the output of the pipeline
        self.stdout = self.procs[-1].stdout

    def close(self):
        """Close standard output and finish all processes."""
        self.stdout.close()
        for proc in self.procs:
            proc.wait()

    def poll(self):
        """See subprocess.Popen.poll"""
        for proc in self.procs:
            proc.poll()

    def returncodes(self):
        """Return the list of return codes from all processes."""
        self.poll()
        return [proc.returncode for proc in self.procs]

    def failed(self):
        """Return True if any process failed."""
        return any(rc not in (0, None) for rc in self.returncodes())

    def succeeded(self):
        """Return True if every process succeeded."""
        return all(rc == 0 for rc in self.returncodes())

    def finished(self):
        """Return true if every process finished."""
        return all(rc is not None for rc in self.returncodes())
