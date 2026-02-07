#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { PaystubProcessorStack } from '../lib/main-stack';

const app = new cdk.App();

const env = {
  account: process.env.CDK_DEFAULT_ACCOUNT || '123456789012',
  region: process.env.CDK_DEFAULT_REGION || 'us-east-1'
};

new PaystubProcessorStack(app, 'PaystubProcessorStack', {
  env,
  description: 'Paystub processing solution'
});

app.synth();
