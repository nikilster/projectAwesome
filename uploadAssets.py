import sys
import os
import getopt

from awesome.util.assets import genAssets

PROG_NAME = "gen_fb_item_url.py"

USAGE = '''
%(prog)s

Uploads static assets to S3

Usage: %(prog)s [OPTIONS]

    Options flags.
            -a, --all           Upload all assets (CSS, JS, images)
            -c, --css           Upload CSS
            -j, --js            Upload JS
            -i, --img           Upload images

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
                                   "acjih",
                                   ["all", "css", "js", "img"])
    except getopt.error, msg:
        Usage(msg)

    # Process options
    do_css = False
    do_js = False
    do_img = False
    for o, a in opts:
        if o in ("-a", "--all"):
            do_css = True
            do_js = True
            do_img = True
        elif o in ("-c", "--css"):
            do_css = True
        elif o in ("-j", "--js"):
            do_js = True
        elif o in ("-i", "--img"):
            do_img = True
        elif o in ("-h", "--help"):
            Usage()
        else:
            Usage("ERROR: Invalid option: " + o)
    if not (do_css or do_js or do_img):
        Usage("EXIT: Nothing to upload")

    cwd = os.getcwd()
    print "Current working directory: " + cwd
    staticDir = os.path.join(cwd, "awesome/static")
    if not os.path.isdir(staticDir):
        Usage("Cannot find static directory at " + staticDir)
    else:
        print "Static/assets: " + staticDir
    print ""

    # If uploading CSS or JS, generate minified versions first
    if do_css or do_js:
        print "---- Generate combined and minified assets ----"
        genAssets()
        print ""


    if do_img:
        print "---- Upload images to S3 ----"
        print "  Copying bootstrap images"
        os.system("cp -R awesome/static/opt/bootstrap/img awesome/static/gen/img")
        print "  Copying img folder"
        os.system("cp -R awesome/static/img/* awesome/static/gen/img")

        print "  Transfer to S3"
        os.system("s3put --bucket project-awesome-static --prefix " +
                        staticDir + " awesome/static/gen/img")
        print ""
    if do_css:
        print "---- Upload CSS to S3 ----"
        os.system("s3put --bucket project-awesome-static --prefix " +
                        staticDir + " awesome/static/gen/css")
        print ""
    if do_js:
        print "---- Upload JS to S3 ----"
        os.system("s3put --bucket project-awesome-static --prefix " +
                        staticDir + " awesome/static/gen/js")
        print ""

    print "Done."

if __name__ == '__main__':
    sys.exit(main())

# $eof
