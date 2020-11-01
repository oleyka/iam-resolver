#!/bin/bash

INPUT="input.txt"
POLICY_TEMPLATE=./policy.json
POLICY_GENERATED=./policy-gen.json

function usage {
    echo "Usage: $0 -b <BUCKET_NAME> -i <INPUT_FILE>"
    exit 1
}

while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        -b|--bucket)
        BUCKET="$2"
        shift; shift
        ;;
        -i|--input)
        INPUT="$2"
        shift; shift
        ;;
    esac
done

if [ "x$BUCKET" = "x" ] || [ "x$INPUT" = "x" ]; then
    usage
fi

for userid in $(cat $INPUT); do
    sed -e "s/BUCKET/$BUCKET/" -e "s/USERID/$userid/" $POLICY_TEMPLATE > $POLICY_GENERATED
    if aws s3api put-bucket-policy --bucket $BUCKET --policy file://$POLICY_GENERATED 2> /dev/null; then
        arn=$(aws s3api get-bucket-policy --bucket $BUCKET --output text | jq -r .Statement[0].Principal.AWS)
    else
        arn="UNRESOLVED"
    fi
    echo $userid,$arn
done

rm -f $POLICY_GENERATED
