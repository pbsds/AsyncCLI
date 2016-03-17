# AsyncCLI


For a [chat server and client](https://github.com/pbsds/TTM4100-Chat) i madef or an assignment, i needed a way to print and read from stdout at the same time.
That code has been generalized and been put into ´CLI.py´
But to achieve this i needed a way to read from stdin asyncronously.
This was simple on windows, but not so easy on unix.
This is an attempt to make a interface inspired by msvcrt, but which is also cross-platform.