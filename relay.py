#!/usr/bin/python3

import sys

def msg (s):
    sys.stderr.write(s)
    sys.stderr.write("\n")
    sys.stderr.flush

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
        if words[0] == "neighbor":
            neighbour = words[1]
            if words[2] == "receive" and words[3] == "update":
                if words[4] == "announced":
                    route = ' '.join(words[5::])
                    msg("send: " + route)
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

"""     if h1 in line:
        newline = line.replace(h1,h2)
    else:
        newline = line.replace(h2,h1)
    sys.stdout.write(newline)
    sys.stdout.write("\n")
    sys.stdout.flush 
    sys.stderr.write(f'Put:{newline}\n')
    sys.stderr.flush   """      

sys.stderr.write("Done\n")