AWS IAM Resolver
===

The tool resolves `AROA*` and `AIDA*` AWS IAM idenfifiers to their full ARNs. It also optionally converts account IDs to their `root` ARNs.

It takes as input a file with identifiers to resolve, one per line, and outputs the resolution status for each identifier in a CSV format. The possible values are:

* AWS ARN of the identifier,
* `UNRESOLVED` when an identifier fails to resolve, and
* `SKIPPED` when an identifier does not appear to conform to AWS id format.

__Note__: To use this tool you need to have permissions to put and get policies of an S3 bucket.


Usage
---

```
$ python3 iam_resolver.py --help
usage: iam_resolver.py [-h] -b BUCKET [-c int[3, 20]] [-i INPUT]
                       [--drop-policy] [--resolve-accounts]

AWS identifier resolver.

optional arguments:
  -h, --help            show this help message and exit
  -b BUCKET, --bucket BUCKET
                        name of an existing bucket to use for identifier
                        resolution
  -c int[3, 20], --count int[3, 20]
                        count of IAM identifiers in a batch (default=10)
  -i INPUT, --input INPUT
                        file with IAM identifiers to resolve
  --drop-policy         drop current bucket policy prior to testing
  --resolve-accounts    resolve account IDs as well
```

There is also a rudimentary version written in `bash`. The original S3 bucket policy would be destroyed. Here's how to run it:
```
$ ./resolver.sh -b <BUCKET_NAME> -i <INPUT_FILE>
```

