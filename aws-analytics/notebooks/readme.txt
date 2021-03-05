==============Steps to create development end point roles and polices=================

[centos@ip-172-31-44-109 ci]$ GLUE_ROLE=`aws iam create-role --role-name glue-role --assume-role-policy-document file://policy.json | grep Arn | sed -e 's/"//g' -e 's/,//g' -e 's/Arn//g' -e 's/ //g' -e 's/://' `;echo

[centos@ip-172-31-44-109 ci]$ aws iam delete-role --role-name glue-role
[centos@ip-172-31-44-109 ci]$ GLUE_ROLE=`aws iam create-role --role-name glue-role --assume-role-policy-document file://policy.json | grep Arn | sed -e 's/"//g' -e 's/,//g' -e 's/Arn//g' -e 's/ //g' -e 's/://' `;echo $GLUE_ROLE
arn:aws:iam::369626215919:role/glue-role
[centos@ip-172-31-44-109 ci]$ aws iam attach-role-policy --role-name glue-role --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
[centos@ip-172-31-44-109 ci]$ aws iam attach-role-policy --role-name glue-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole
[centos@ip-172-31-44-109 ci]$ POLICY_ARN=`aws iam create-policy --policy-name passrole --policy-document file://passrole.json | grep Arn | sed 's/"Arn"://' | sed 's/"//g' | sed 's/,//g'`;echo $POLICY_ARN
arn:aws:iam::369626215919:policy/passrole

===========Steps to validate notebook creation=================================

[centos@ip-172-31-44-109 ci]$ aws iam attach-role-policy --role-name glue-role --policy-arn $POLICY_ARN
[centos@ip-172-31-44-109 ci]$ GLUE_ARN=` aws iam get-role --role-name glue-role | grep Arn | sed 's/"Arn"://' | sed 's/"//g' | sed 's/,//g'`;echo $GLUE_ARN
arn:aws:iam::369626215919:role/glue-role

[centos@ip-172-31-44-109 ci]$ aws glue create-dev-endpoint --endpoint-name test --role-arn $GLUE_ARN --number-of-nodes 2
{
    "EndpointName": "test",
    "Status": "PROVISIONING",
    "SecurityGroupIds": [],
    "RoleArn": "arn:aws:iam::369626215919:role/glue-role",
    "ZeppelinRemoteSparkInterpreterPort": 0,
    "NumberOfNodes": 2,
    "AvailabilityZone": "us-east-1a",
    "CreatedTimestamp": "2020-09-29T12:07:20.146000-04:00"
}

===================Steps to create notebook role===============================
[centos@ip-172-31-44-109 ci]$ NBPOLICY_ARN=`aws iam create-policy --policy-name nbpolicy --policy-document file://nbpolicy.json | grep Arn | sed 's/"Arn"://' | sed 's/"//g' | sed 's/,//g'`;echo $NBPOLICY_ARN
arn:aws:iam::369626215919:policy/nbpolicy
[centos@ip-172-31-44-109 ci]$ NOTEBOOK_ROLE=`aws iam create-role --role-name notebook-role --assume-role-policy-document file://sagemakerpolicy.json | grep Arn | sed -e 's/"//g' -e 's/,//g' -e 's/Arn//g' -e 's/ //g' -e 's/://' `;echo $NOTEBOOK_ROLE
arn:aws:iam::369626215919:role/notebook-role
[centos@ip-172-31-44-109 ci]$ aws iam attach-role-policy --role-name notebook-role --policy-arn $NBPOLICY_ARN