from awesome import app

if app.config['LOCAL_DB'] == False:
    print "** DON'T WIPE THE PRODUCTION DB **"
    sys.exit(1)

from awesome.api.data import DB

print "Dropping all tables"
DB.drop_all();
print "Creating all tables"
DB.create_all();

print "Done."
