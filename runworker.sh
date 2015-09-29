#!/bin/bash

# Download required files from S3.
wget https://s3.amazonaws.com/er9akd/wkhtmltopdf/fonts.zip -P /tmp -q
if [ $? -ne 0 ]; then
    echo "`basename "$0"`: download fonts.zip failed"
    exit 1
fi

wget https://s3.amazonaws.com/er9akd/wkhtmltopdf/bin.zip -P /tmp -q
if [ $? -ne 0 ]; then
    echo "`basename "$0"`: download bin.zip failed"
    exit 2
fi

# Extract zip files to home directories.
unzip -oq /tmp/fonts.zip -d ~/.fonts/
if [ $? -ne 0 ]; then
    echo "`basename "$0"`: unzip fonts.zip failed"
    exit 3
fi

unzip -oq /tmp/bin.zip -d ~/bin/
if [ $? -ne 0 ]; then
    echo "`basename "$0"`: unzip bin.zip failed"
    exit 4
fi

chmod a+x ~/bin/*
echo "`basename "$0"`: init done. starting worker..."
python manage.py rqworker high low
exit 0
