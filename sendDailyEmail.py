import sys
import getopt

from awesome.util.Notifications import Notifications
from awesome import app

PROG_NAME = "sendDailyEmail.py"

USAGE = '''
%(prog)s

The is meant to be tied to a cron job that sends the daily email to all users.

Usage: %(prog)s [OPTIONS]

    Options flags.
            -t, --test          Send single test email.
            -d, --do-it         Actually sends email to all users.
                                (If this isn't set, we just send a test email)

            -h, --help          Display help
'''

def Usage(msg=""):
    print USAGE % { 'prog' : PROG_NAME }
    if (msg != ""):
        print msg
    sys.exit(1)

def main(argv=None):
    # Get options
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:],
                                   "tdh",
                                   ["test", "do-it", "help"])
    except getopt.error, msg:
        Usage(msg)

    # Process options
    do_test = False
    do_it = False
    for o, a in opts:
        if o in ("-d", "--do-it"):
            do_it = True
        elif o in ("-t", "--test"):
            do_test = True
        elif o in ("-h", "--help"):
            Usage()
        else:
            Usage("ERROR: Invalid option: " + o)

    # One of these should be True
    if do_test == False and do_it == False:
        Usage("Need to do test email or real user email")

    # Create fake Flask request context and push onto context stack.
    # The request context is needed for render_template to work.
    ctx = app.test_request_context()
    ctx.push()

    # Now do whatever work we want in the request context
    notification = Notifications(test = not do_it)
    notification.sendDailyEmails()

    # Pop the request context
    ctx.pop()

    if not do_it:
        print "\n *** Sent test email ***\n"


if __name__ == '__main__':
    sys.exit(main())

# $eof
