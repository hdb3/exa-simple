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
  
def api (s):
    dbg("<<" + s)
    global req
    req = s
    sys.stdout.write(s)
    sys.stdout.write("\n")
    sys.stdout.flush()

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

def half_jsony ():

    update_count = 0
    prefix_count = 0
    max_prefix_count = 0
    
    while True:
        line = sys.stdin.readline().strip()

        global req
        if "done" == line:
            continue
        elif "error" == line:
            msg("error after" + req)

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

            if 'eor' in z['neighbor']['message']:
                sys.stderr.write(str(max_prefix_count) + " : " + str(update_count) + " : " + str(prefix_count) + " =\n")
                continue
            elif 'update' not in z['neighbor']['message']:
                msg("update field not in message [" + line + "]")
                exit
            update = z['neighbor']['message']['update']
            neighbor = switch(peer,h1,h2)

            if 'withdraw' in update:
                nlris=[]
                for d in update['withdraw']['ipv4 unicast']:
                    nlris.append(d['nlri'])
                for prefix in nlris:
                    api(f'neighbor {neighbor} withdraw route {prefix}')

            if 'announce' in update:
                attributes = update['attribute']
                (nexthop,nlridicts) = list(dict.items(update['announce']['ipv4 unicast']))[0]

                prefixes = ""
                for d in nlridicts:
                    prefixes = prefixes + str(d['nlri']) + " "
                    
                origin = attributes['origin']
                aspath = (str(attributes['as-path']).replace(',',''))
                update_count += 1
                this_prefix_count = len(nlridicts)
                prefix_count += this_prefix_count
                max_prefix_count = this_prefix_count if this_prefix_count > max_prefix_count else max_prefix_count 
                if 0 == update_count % 100:
                    sys.stderr.write(str(max_prefix_count) + " : " + str(update_count) + " : " + str(prefix_count) + "\r")
                api(f'neighbor {neighbor} announce attributes next-hop {nexthop} origin {origin} as-path {aspath} nlri {prefixes}')

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