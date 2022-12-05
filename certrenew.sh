#!/bin/bash

/usr/bin/aws s3 cp s3://otto-certs/aws.ottomotors.com/privkey.pem  /etc/ssl/private/aws.ottomotors.com.key
/usr/bin/aws s3 cp s3://otto-certs/aws.ottomotors.com/cert.pem /etc/ssl/certs/aws.ottomotors.pem

/etc/init.d/nginx restart
