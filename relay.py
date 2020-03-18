#!/usr/bin/python3

import sys
import json

debug = False

def switch(s,a,b):
    if a == s:
        return b
    elif b == s:
        return a
    else:
        msg("unexpected neighbour: " + s)
        return s

def dbg (s):
    if debug:
        sys.stderr.write(s)
        sys.stderr.write("\n")
        sys.stderr.flush()

def msg (s):
    sys.stderr.write(s)
    sys.stderr.write("\n")
    sys.stderr.flush()
    
ack = True
  
def api (s):
    dbg("<<" + s)
    sys.stdout.write(s)
    sys.stdout.write("\n")
    sys.stdout.flush()
    if not ack:
        return
    else:
        line = sys.stdin.readline().strip()

        if "done" == line:
            return
        elif "error" == line:
            msg("error after" + s)
        else:
            msg("unexpected response: [" + line +"]")

switcher = {}

def jswitch(address):
    try:
        return switcher[address['peer']]
    except Exception:
        msg("unexpected neighbour:" + str(address))
        return address

def add_local(address):
    if h1 == address['peer']:
        switcher[h2]=(address)
    elif h2 == address['peer']:
        switcher[h1]=(address)
    else:
        msg("unexpected neighbour:" + str(address))

def jsony ():
    while True:
        line = sys.stdin.readline().strip()
        try:
            z = json.loads(line)
        except Exception:
            msg("failed to read json " + line)
            break

        peer = z['neighbor']['address']['peer']
        typ  =  z['type']
        if typ == 'update':
            dbg("update from " + peer + " : " + str(z))
            z['neighbor']['address'] = jswitch(z['neighbor']['address'])
            dbg("switched to : " + str(z))
            api(json.dumps(z))
        elif typ == 'state':
            if 'up' == z['neighbor']['state']:
                local = z['neighbor']['address']['local']
                msg("peer " + peer + " up, local=" +  local)
                add_local(z['neighbor']['address'])
            else:
                pass
        else:
            msg("got: " + typ + " from " + peer )
            msg(str(z))

def half_jsony ():
    
    while True:
        line = sys.stdin.readline().strip()
        try:
            z = json.loads(line)
        except Exception:
            msg("failed to read json [" + line + "]")
            break

        peer = z['neighbor']['address']['peer']
        typ  =  z['type']
        # encoding notes -
        #  NLRI encoding is a little non-intuitive - the next-hop is encoded as the singleton key (property name)
        # in a structure which looks like this: 
        #    ['neighbor']['message']['update']['announce']['ipv4 unicast']['7.0.0.2'][..,..]
        #   where the array mmebers are single member dictioarys like this....
        #      [{'nlri': '172.16.0.98/32'}, {'nlri': '172.16.0.99/32'}]
        if typ == 'update':
            dbg("update from " + peer)
            update = z['neighbor']['message']['update']
            attributes = update['attribute']
            (nexthop,nlridicts) = list(dict.items(update['announce']['ipv4 unicast']))[0]

            nlris=[]
            for d in nlridicts:
                nlris.append(d['nlri'])

            neighbor = switch(peer,h1,h2)
            origin = attributes['origin']
            aspath = (str(attributes['as-path']).replace(',',''))

            # api string is like: "neighbor 7.0.0.6 announce route 172.16.0.99/32 next-hop 7.0.0.2 origin igp as-path [ 65001 100 101 ]"

            # it does not seem possible to send packed NLRI with the API
            # api(f'neighbor {neighbor} announce start')
            for prefix in nlris:
                response = f'neighbor {neighbor} announce route {prefix} next-hop {nexthop} origin {origin} as-path {aspath}'
                api(response)
            # api(f'neighbor {neighbor} announce end')

        elif typ == 'state':
            if 'up' == z['neighbor']['state']:
                local = z['neighbor']['address']['local']
                msg("peer " + peer + " up, local=" +  local)
                add_local(z['neighbor']['address'])
            else:
                pass
        else:
            msg("got: " + typ + " from " + peer )
            msg(str(z))
"""
The text based packed NLRI format is:
>> neighbor 7.0.0.2 receive update start
>> neighbor 7.0.0.2 receive update announced 172.16.0.98/32 next-hop 7.0.0.2 origin igp as-path [ 65001 100 101 ]
>> neighbor 7.0.0.2 receive update announced 172.16.0.99/32 next-hop 7.0.0.2 origin igp as-path [ 65001 100 101 ]
>> neighbor 7.0.0.2 receive update end
Unfortunately, the API is not symmetric and this scheme is not allowed on the sending side
"""
def texty ():
    global ack
    ack = False

    while True:
        line = sys.stdin.readline().strip()
        if line:
            words = line.split()
            if words[0] == "done":
                pass
            elif words[0] == "neighbor":
                neighbour = words[1]
                if words[2] == "receive" and words[3] == "update":
                    if words[4] == "announced" or words[4] == "withdrawn":
                        route = ' '.join(words[5::])
                        dbg(">> " + line)
                        response = "neighbor " + switch(neighbour,h1,h2)
                        response = response + ( " announce route " if words[4] == "announced" else " withdraw route " )
                        response = response + route
                        api(response)
                    elif words[4] == "start":
                        dbg(">> " + line)
                    elif words[4] == "end":
                        dbg(">> " + line)
                    else:
                        msg("unexpected update message: " + line)
                elif words[2] == "up":
                    msg("neighbour " + neighbour + " up" )
                elif words[2] == "connected":
                    msg("neighbour " + neighbour + " connected" )
                else:
                    msg("unexpected neighbour message: " + line)
            else:
                msg("unexpected input: " + line)

msg("relay starting")

if len(sys.argv) < 2 :
    msg("error - looking for two parameters (ip addrs 1 & 2)")
    exit()
else:
    h1 = sys.argv[1]
    h2 = sys.argv[2]
    msg(f'mapping updates between {h1} and {h2}')
    # texty()
    half_jsony()
msg("Done\n")