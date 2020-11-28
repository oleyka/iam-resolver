AWS IAM Resolver
===

Resolve AROA\* and AIDA\* AWS IAM idenfifiers to their ARNs.

To use this tool you need to have permissions to put and get the policy of an S3 bucket. The original S3 bucket policy would be destroyed.

Usage
---

```
$ python3 iam_resolver.py --help
usage: iam_resolver.py [-h] -b BUCKET [-i INPUT] [--drop-policy]

IAM identifier resolver.

optional arguments:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        name of the bucket to use for identifier resolution
  -i INPUT, --input INPUT
                        file with IAM identifiers to resolve
  --drop-policy         drop current bucket policy prior to testing
```

There is also simple version in `bash`:
```
./resolver.sh -b <BUCKET_NAME> -i <INPUT_FILE>
```

