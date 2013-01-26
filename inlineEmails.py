import os
import sys
import getopt
import glob
from pynliner import Pynliner
from BeautifulSoup import BeautifulSoup


PROG_NAME = "inlineEmails.py"

USAGE = '''
%(prog)s

Process email HTML so they have have inlined CSS. Lists templates found
by default. Pass -i/--inline to generate inline templates.

Usage: %(prog)s [OPTIONS]

    Options flags.
            -i, --inline        Do CSS inline and generate output files
            -n, --name <name>   Name of file to just inline one file
                                (e.g., daily)
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
                                   "hin:",
                                   ["inline", "help", "name="])
    except getopt.error, msg:
        Usage(msg)

    # Process options
    doInlining = False
    name = None
    for o, a in opts:
        if o in ("-i", "--inline"):
            doInlining = True
        elif o in ("-n", "--name"):
            name = a
        elif o in ("-h", "--help"):
            Usage()
        else:
            Usage("ERROR: Invalid option: " + o)

    templateDir = 'awesome/templates/email/'

    if not os.path.isdir(templateDir):
        Usage("Can't find email templates in : " + templatesDir)

    if name == None:
        print "\nLooking for template emails..."
        files = glob.glob(templateDir + "*.template.html")
    else:
        print "\nLooking for name: " + str(name)
        files = glob.glob(templateDir + str(name) + ".template.html")

     # Getting email.css
    print "\nGetting CSS..."
    cssFile = open(os.path.join(templateDir, "css/email.css"), "r")
    css = cssFile.read();
    cssFile.close()
   
    for name in files:
        print "    Found: " + name
        output = name.replace(".template.html", ".html")

        if doInlining:
            inputFile = open(name, 'r')
            origEmail = inputFile.read()
            inputFile.close()

            inliner = Pynliner().from_string(origEmail).with_cssString(css)
            inlinedEmail = inliner.run()
            prettyEmail = BeautifulSoup(inlinedEmail).prettify()

            outputFile = open(output, "w")
            outputFile.write(prettyEmail)
            outputFile.close()
                            
            print "      Gen: " + output
            print ""

    return

if __name__ == '__main__':
    sys.exit(main())

# $eof
