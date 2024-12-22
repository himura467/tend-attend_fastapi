## Before Init

Run this:

```sh
aws s3api create-bucket --bucket tend-attend-terraform-state --region "ap-northeast-1" --create-bucket-configuration LocationConstraint="ap-northeast-1"
aws s3api put-bucket-versioning  --bucket tend-attend-terraform-state --versioning-configuration Status=Enabled
aws s3api put-bucket-encryption --bucket tend-attend-terraform-state --server-side-encryption-configuration "{\"Rules\" : [{\"ApplyServerSideEncryptionByDefault\" : {\"SSEAlgorithm\" : \"AES256\"}}]}"
aws s3api put-public-access-block --bucket tend-attend-terraform-state --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```
