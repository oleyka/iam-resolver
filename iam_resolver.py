""" Resolve IAM user and role IDs. """

import argparse
import json

import boto3
from botocore.exceptions import ClientError


DEBUG = False


def parse_args():
    """ Parse the args """
    parser = argparse.ArgumentParser(description='AWS identifier resolver.')
    parser.add_argument('-b', '--bucket', dest='bucket', required=True,
                        help='name of an existing bucket to use for identifier resolution'
                       )
    parser.add_argument('-c', '--count', dest='batch_size', type=int, default=10,
                        choices=list(range(3, 21)), metavar='int[3, 20]',
                        help='count of IAM identifiers in a batch (default=10)'
                       )
    parser.add_argument('-i', '--input', dest='input', default='input.txt',
                        help='file with IAM identifiers to resolve'
                       )
    parser.add_argument('--drop-policy', dest='drop_policy', action='store_true',
                        help='drop current bucket policy prior to testing'
                       )
    parser.add_argument('--resolve-accounts', dest='resolve_accounts', action='store_true',
                        help='resolve account IDs as well'
                       )

    args = parser.parse_args()
    return args


def build_policy(bucket, src_policy, ids):
    """ Append AWS ids to the policy """
    if not src_policy:
        src_policy = '{ "Version" : "2012-10-17", "Statement" : [] }'
    jpolicy = json.loads(src_policy)

    for aid in ids:
        stmt = {
            "Sid" : aid,
            "Action" : "s3:ListBucket",
            "Effect" : "Deny",
            "Resource" : "arn:aws:s3:::" + bucket,
            "Principal" : { "AWS" : [ aid ] }
        }
        jpolicy["Statement"].append(stmt.copy())

    if DEBUG:
        print("--", "Constructed policy:", jpolicy)

    return json.dumps(jpolicy)


def put_policy(client, bucket, policy):
    """ Update bucket policy """
    # pylint: disable=no-else-return
    try:
        client.BucketPolicy(bucket).put(Policy=policy)
    except ClientError as err:
        if err.response['Error']['Code'] == "MalformedPolicy":
            if DEBUG:
                print("--", "Bucket policy could not be applied")
            return False
        else:
            raise err
    return True


def get_policy(client, bucket):
    """ Save current bucket policy """
    try:
        response = client.BucketPolicy(bucket)
        policy = response.policy
        if DEBUG:
            print("--", "Saved policy:", policy)
    except ClientError as err:
    # buckets with no policy would throw NoSuchBucketPolicy here
        if err.response['Error']['Code'] == "NoSuchBucketPolicy":
            policy = ""
            if DEBUG:
                print("--", "No bucket policy to save")
        else:
            raise err
    return policy


def validate_id(aid, resolve_accounts):
    """ Verify a string is of a valid AWS id format """
    base32chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    digits = "0123456789"

    if resolve_accounts and len(aid) == 12:
        for sym in aid:
            if sym not in digits:
                return False
        return True
    if len(aid) == 21:
        if aid[0:4] not in ["AROA", "AIDA"]:
            return False
        for sym in aid[4:]:
            if sym not in base32chars:
                return False
        return True
    return False


def get_ids(fname, resolve_accounts):
    """ Read the list of ids to resolve """
    with open(fname) as file:
        lines = file.read().splitlines()

    noquote_lines = [line.replace("\"", "").replace("'", "") for line in lines]
    valid_aids = [aid for aid in noquote_lines if validate_id(aid, resolve_accounts)]
    for aid in noquote_lines:
        if not aid in valid_aids:
            if ',' in aid:
                aid = "\""+aid+"\""
            print(aid, "SKIPPED", sep=",")
    return valid_aids


def resolve_batch(client, bucket, src_policy, test_aids):
    """ Resolve a batch of ids """
    if DEBUG:
        print("--", "Attempting to resolve ids", test_aids)
    test_policy = build_policy(bucket, src_policy, test_aids)
    success = put_policy(client, bucket, test_policy)
    if success:
        resolved_policy = get_policy(client, bucket)
        resolvedj = json.loads(resolved_policy)
        if DEBUG:
            print("--", "Resolved policy:", resolved_policy)
        for statement in resolvedj['Statement']:
            aid = statement['Sid']
            if aid in test_aids:
                if  statement['Principal']['AWS'] != aid:
                    print(aid, statement['Principal']['AWS'], sep=",")
                else:
                    print(aid, 'VALID_UNRESOLVED', sep=",")
    else:
        if len(test_aids) > 1:
            if DEBUG:
                print("--", "Bulk policy upload for", test_aids, "did not succeed")
            for aid in test_aids:
                resolve_batch(client, bucket, src_policy, [aid])
        else:
            print(test_aids[0], 'UNRESOLVED', sep=",")
    return True


def resolve_aids(client, bucket, src_policy, test_aids, batch_size):
    """ Resolve all """
    # pylint: disable=invalid-name

    n = batch_size
    batches = [
        test_aids[i * n:(i + 1) * n] for i in range((len(test_aids) + n - 1) // n )
    ]
    for batch in batches:
        resolve_batch(client, bucket, src_policy, batch)


def main():
    """ Main """
    main_args = parse_args()
    aids = get_ids(main_args.input, main_args.resolve_accounts)

    saved_policy = ""
    s3_client = boto3.resource('s3')
    if not main_args.drop_policy:
        saved_policy = get_policy(s3_client, main_args.bucket)

    resolve_aids(s3_client, main_args.bucket, saved_policy, aids, main_args.batch_size)

    if saved_policy and not main_args.drop_policy:
        if DEBUG:
            print("--", "Restore bucket policy")
        put_policy(s3_client, main_args.bucket, saved_policy)
    else:
        if DEBUG:
            print("--", "Remove bucket policy")
        s3_client.BucketPolicy(main_args.bucket).delete()
    return True


if __name__ == "__main__":
    main()
