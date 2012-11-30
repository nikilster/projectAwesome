#!/bin/bash
#
# Make sure to include version so that we maintain consistency across all
# working setups and production
#

. ../venv/bin/activate

pip install -I Flask==0.9
#pip install -I redis==2.7.1
pip install -I py_bcrypt==0.2
pip install -I Flask_SQLAlchemy==0.16
easy_install -U distribute
pip install -I MySQL_python==1.2.3
pip install -I boto==2.6.0

# $eof
