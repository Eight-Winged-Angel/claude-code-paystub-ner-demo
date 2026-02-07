"""
PaystubProcessor Document Processor

Processes Paystub documents using AWS Textract and custom extraction logic.
"""

import json
import boto3
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')
dynamodb = boto3.resource('dynamodb')

# Environment variables
DOCUMENT_BUCKET = os.environ.get('DOCUMENT_BUCKET')
DOCUMENT_TABLE = os.environ.get('DOCUMENT_TABLE')


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for document processing.

    Args:
        event: S3 event or API Gateway event
        context: Lambda context

    Returns:
        Processing result
    """
    logger.info(f"Processing event: {json.dumps(event)}")

    try:
        # Extract document info from event
        document_key = extract_document_key(event)

        if not document_key:
            return error_response(400, "No document key found in event")

        # Process document with Textract
        extraction_result = process_document(document_key)

        # Store results
        document_id = store_results(document_key, extraction_result)

        return success_response({
            'documentId': document_id,
            'documentKey': document_key,
            'extractedFields': extraction_result.get('fields', {}),
            'confidence': extraction_result.get('confidence', 0.0)
        })

    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return error_response(500, str(e))


def extract_document_key(event: Dict[str, Any]) -> Optional[str]:
    """Extract S3 document key from event."""
    # S3 event
    if 'Records' in event:
        for record in event['Records']:
            if record.get('eventSource') == 'aws:s3':
                return record['s3']['object']['key']

    # API Gateway event
    if 'body' in event:
        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        return body.get('documentKey')

    # Direct invocation
    return event.get('documentKey')


def process_document(document_key: str) -> Dict[str, Any]:
    """
    Process document using AWS Textract.

    Args:
        document_key: S3 object key

    Returns:
        Extraction results with fields and confidence
    """
    # Call Textract
    response = textract_client.analyze_document(
        Document={
            'S3Object': {
                'Bucket': DOCUMENT_BUCKET,
                'Name': document_key
            }
        },
        FeatureTypes=['FORMS', 'TABLES']
    )

    # Extract key-value pairs
    fields = {}
    total_confidence = 0.0
    field_count = 0

    key_map = {}
    value_map = {}
    block_map = {}

    for block in response['Blocks']:
        block_id = block['Id']
        block_map[block_id] = block

        if block['BlockType'] == 'KEY_VALUE_SET':
            if 'KEY' in block.get('EntityTypes', []):
                key_map[block_id] = block
            elif 'VALUE' in block.get('EntityTypes', []):
                value_map[block_id] = block

    # Match keys with values
    for key_id, key_block in key_map.items():
        key_text = get_text(key_block, block_map)

        for rel in key_block.get('Relationships', []):
            if rel['Type'] == 'VALUE':
                for value_id in rel['Ids']:
                    value_block = value_map.get(value_id, {})
                    value_text = get_text(value_block, block_map)

                    if key_text and value_text:
                        fields[key_text] = value_text
                        confidence = key_block.get('Confidence', 0) / 100
                        total_confidence += confidence
                        field_count += 1

    avg_confidence = total_confidence / field_count if field_count > 0 else 0.0

    return {
        'fields': fields,
        'confidence': round(avg_confidence, 4),
        'raw_blocks': len(response['Blocks'])
    }


def get_text(block: Dict[str, Any], block_map: Dict[str, Any]) -> str:
    """Extract text from a Textract block."""
    text = ''

    for rel in block.get('Relationships', []):
        if rel['Type'] == 'CHILD':
            for child_id in rel['Ids']:
                child_block = block_map.get(child_id, {})
                if child_block.get('BlockType') == 'WORD':
                    text += child_block.get('Text', '') + ' '

    return text.strip()


def store_results(document_key: str, extraction_result: Dict[str, Any]) -> str:
    """Store extraction results in DynamoDB."""
    table = dynamodb.Table(DOCUMENT_TABLE)

    document_id = document_key.replace('/', '-').replace('.', '-')
    timestamp = datetime.utcnow().isoformat()

    item = {
        'documentId': document_id,
        'timestamp': timestamp,
        'documentKey': document_key,
        'extractedFields': extraction_result.get('fields', {}),
        'confidence': str(extraction_result.get('confidence', 0.0)),
        'status': 'PROCESSED',
        'createdAt': timestamp
    }

    table.put_item(Item=item)

    return document_id


def success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create a success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }


def error_response(status_code: int, message: str) -> Dict[str, Any]:
    """Create an error response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message
        })
    }
