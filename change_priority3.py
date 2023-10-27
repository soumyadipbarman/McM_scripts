#python change_priority3.py --request <start range 1>,<end range 1>;<start range 2>,<end range 2>;<individual request 1>;<individual request 2> --block 2
import sys
import argparse
sys.path.append('/afs/cern.ch/cms/PPD/PdmV/tools/McM/')
from rest import McM


parser = argparse.ArgumentParser(description='Change priority in McM')
parser.add_argument('--ticket', type=str)
parser.add_argument('--request', type=str)
parser.add_argument('--priority', type=int)
parser.add_argument('--block', type=int)
parser.add_argument('--dry', default=False, action='store_true')
parser.add_argument('--debug', default=False, action='store_true')

args = parser.parse_args()
debug = args.debug
dry = args.dry
if debug:
    print('Args: %s' % (args))

if args.priority:
    priority = int(args.priority)
elif args.block:
    block = int(args.block)
    if block == 1:
        priority = 110000
    elif block == 2:
        priority = 90000
    elif block == 3:
        priority = 85000
    elif block == 4:
        priority = 80000
    elif block == 5:
        priority = 70000
    elif block == 6:
        priority = 63000
    else:
        print('Unknown block "%s"' % (block))
        sys.exit(1)
else:
    print('Either block or priority must be specified')
    sys.exit(1)

if priority < 20000 or priority > 400000:
    print('Unconventional priority "%s"' % (priority))
    sys.exit(1)

mcm = McM(dev=False)

requests = []
print ("Shit happens here 1")
if args.ticket:
    ticket_prepids = args.ticket.split(',')
    for ticket_prepid in ticket_prepids:
        print ("Shit happens here 1 1")
        requests_in_ticket = mcm.root_requests_from_ticket(ticket_prepid)
        print ("Shit happens here 1 2")
        requests.extend(requests_in_ticket)
        print ("Shit happens here 1 3")
if args.request:
    range_string = args.request.replace(';', '\n').replace(',', ' -> ')
    requests.extend(mcm.get_range_of_requests(range_string))

print ("Shit happens here 2")
print('Found %s requests' % (len(requests)))
request_status = {}
for request in requests:
    status = '%s-%s' % (request['approval'], request['status'])
    request_status[status] = request_status.get(status, 0) + 1

print ("Shit happens here 3")
print('Requests by status:')
for status, count in request_status.items():
    print(' %s - %s' % (status, count))

requests = [x for x in requests if x['status'] != 'done']
print('Picked %s requests are not done' % (len(requests)))
requests = [x for x in requests if x['priority'] != priority]
print('Picked %s requests with priority !=%s' % (len(requests), priority))


print('Priority: %s' % (priority))
request_prepids = sorted(list(set(x['prepid'] for x in requests)))
print('Prepids (%s): %s' % (len(request_prepids), ','.join(request_prepids)))

if not dry:
    for prepid in request_prepids:
        print('Changing %s to %s...' % (prepid, priority))
        result = mcm._McM__post('restapi/requests/priority_change', [{'prepid': prepid, 'priority_raw': priority}])
        print('Result: %s' % (result))
