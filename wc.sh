#!/bin/bash

WC="wc *.py \
   *.sh \
   awesome/*.py \
   awesome/util/*.py \
   awesome/api/*.py \
   awesome/api/data/*.py \
   awesome/templates/*.html \
   awesome/templates/email/*.template.html \
   awesome/templates/email/css/*.less \
   awesome/static/js/*.js \
   awesome/static/js/models/*.js \
   awesome/static/js/collections/*.js \
   awesome/static/js/views/*.js \
   awesome/static/js/routers/*.js \
   awesome/static/css/*.less"

echo ""
echo "Python"
$WC | grep py | awk '{sum+=$1} END {print sum}'
echo ""
echo "Javascript"
$WC | grep js | awk '{sum+=$1} END {print sum}'
echo ""
echo "HTML"
$WC | grep html | awk '{sum+=$1} END {print sum}'
echo ""
echo "LESS"
$WC | grep less | awk '{sum+=$1} END {print sum}'
echo ""
echo "ALL"
$WC | grep "total" | awk '{sum+=$1} END {print sum}'
echo ""

