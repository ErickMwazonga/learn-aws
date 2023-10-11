import * as cdk from 'aws-cdk-lib';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as ddb from 'aws-cdk-lib/aws-dynamodb';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';

export class InfraStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // 👇 use the Bucket construct
    const bucket = new s3.Bucket(this, 'users-bucket', {
      // if the bucket is empty at the time we delete our stack, it will also get deleted.
      removalPolicy: cdk.RemovalPolicy.DESTROY, 
      autoDeleteObjects: true, // delete even if with objects
    });

    // Create a Dynamo DB table
    const table = new ddb.Table(this, "Tasks", {
      partitionKey: { name: "task_id", type: ddb.AttributeType.STRING },
      billingMode: ddb.BillingMode.PAY_PER_REQUEST,
      timeToLiveAttribute: "ttl",
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      pointInTimeRecovery: true,
    });

    // Add GSI for the ddb table above
    table.addGlobalSecondaryIndex({
      indexName: "user-index",
      partitionKey: { 
        name: "user_id", 
        type: ddb.AttributeType.STRING 
      },
      sortKey: {
        name: "created_time", 
        type: ddb.AttributeType.NUMBER 
      },
    })

    // Lambda function for the python API
    const api_function = new lambda.Function(this, "API", {
      runtime: lambda.Runtime.PYTHON_3_11,
      // code: lambda.Code.fromAsset('../api'),
      code: lambda.Code.fromAsset("../api/lambda_function.zip"),
      handler: "todo.handler",
      timeout: cdk.Duration.minutes(5),
      memorySize: 512,
      architecture: lambda.Architecture.ARM_64,
      environment: {
        TABLE_NAME: table.tableName,
      }
    });

    // add lambda function url
    const functionUrl = api_function.addFunctionUrl({
      authType: lambda.FunctionUrlAuthType.NONE,
      cors: {
        allowedMethods: [lambda.HttpMethod.ALL],
        allowedOrigins: ['*'],
        allowedHeaders: ['*'], 
      }
    });

    // grant lambda function access permissions
    table.grantReadWriteData(api_function);

     // 👇 create a policy statement
     const listBucketsPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['s3:ListAllMyBuckets'],
      resources: ['arn:aws:s3:::*'],
    });

    // 👇 attach the policy to the function's role
    api_function.role?.attachInlinePolicy(
      new iam.Policy(this, 'list-buckets', {
        statements: [listBucketsPolicy],
      }),
    );

    // output the API function url
    new cdk.CfnOutput(this, "APIUrl", {
      value: functionUrl.url,
    });

    new cdk.CfnOutput(this, 'tableName', {
      value: table.tableName,
      description: 'The name of the s3 bucket',
      exportName: 'users-bucket',
    });

    new cdk.CfnOutput(this, 'myBucketArn', {
      value: bucket.bucketArn,
      description: 'The arn of the s3 bucket',
    });
  }
}

