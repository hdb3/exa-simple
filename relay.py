#!/usr/bin/python3

import sys

def switch(s,a,b):
    if a == s:
        return b
    elif b == s:
        return a
    else:
        msg("unexpected neighbour: " + s)
        return s
    
def api (s):
    sys.stdout.write(s)
    sys.stdout.write("\n")
    sys.stdout.flush()

def msg (s):
    sys.stderr.write(s)
    sys.stderr.write("\n")
    sys.stderr.flush()

msg("relay starting")

if len(sys.argv) < 2 :
    msg("error - looking for two parameters (ip addrs 1 & 2)")
    exit()
else:
    h1 = sys.argv[1]
    h2 = sys.argv[2]
    msg(f'mapping updates between {h1} and {h2}')

for line in sys.stdin:
    s = line.rstrip()
    if s:
        # msg(f'>> {s}')
        words = s.split()
        if words[0] == "done":
            pass
        elif words[0] == "neighbor":
            neighbour = words[1]
            if words[2] == "receive" and words[3] == "update":
                if words[4] == "announced" or words[4] == "withdrawn":
                    route = ' '.join(words[5::])
                    msg(">> " + s)
                    response = "neighbor " + switch(neighbour,h1,h2)
                    response = response + ( " announce route " if words[4] == "announced" else " withdraw route " )
                    response = response + route
                    msg("<< " + response)
                    api(response)
                elif words[4] == "start":
                    pass
                elif words[4] == "end":
                    pass
                else:
                    msg("unexpected update message: " + s)
            elif words[2] == "up":
                msg("neighbour " + neighbour + " up" )
            elif words[2] == "connected":
                msg("neighbour " + neighbour + " connected" )
            else:
              msg("unexpected neighbour message: " + s)
        else:
            msg("unexpected input: " + s)


sys.stderr.write("Done\n")