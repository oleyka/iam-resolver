AWS IAM Resolver
===

Resolve AROA\* and AIDA\* AWS IAM idenfifiers to their ARNs.

To use this tool you need to have permissions to put and get the policy of an S3 bucket. The original S3 bucket policy would be destroyed.

Usage
---

```
./resolver.sh -b <BUCKET_NAME> -i <INPUT_FILE>
```

