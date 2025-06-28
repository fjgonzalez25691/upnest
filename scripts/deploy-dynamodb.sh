#!/bin/bash

# UpNest DynamoDB Tables Deployment Script
# This script deploys all DynamoDB tables for the UpNest application

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
REGION="eu-south-2"
STACK_NAME=""
BILLING_MODE="PAY_PER_REQUEST"

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Deploy UpNest DynamoDB tables using CloudFormation"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Environment (dev, staging, prod) [default: dev]"
    echo "  -r, --region REGION      AWS region [default: eu-south-2]"
    echo "  -s, --stack-name NAME    CloudFormation stack name [default: upnest-dynamodb-ENV]"
    echo "  -b, --billing-mode MODE  Billing mode (PAY_PER_REQUEST, PROVISIONED) [default: PAY_PER_REQUEST]"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e dev -r eu-south-2"
    echo "  $0 --environment prod --region us-west-2"
    echo "  $0 -e staging -s my-custom-stack-name"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            REGION="$2"
            shift 2
            ;;
        -s|--stack-name)
            STACK_NAME="$2"
            shift 2
            ;;
        -b|--billing-mode)
            BILLING_MODE="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Set default stack name if not provided
if [ -z "$STACK_NAME" ]; then
    STACK_NAME="upnest-dynamodb-${ENVIRONMENT}"
fi

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    echo -e "${RED}Error: Environment must be dev, staging, or prod${NC}"
    exit 1
fi

# Validate billing mode
if [[ ! "$BILLING_MODE" =~ ^(PAY_PER_REQUEST|PROVISIONED)$ ]]; then
    echo -e "${RED}Error: Billing mode must be PAY_PER_REQUEST or PROVISIONED${NC}"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

# Check if CloudFormation template exists
TEMPLATE_FILE="aws/infrastructure/dynamodb-tables.yaml"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}Error: CloudFormation template not found: $TEMPLATE_FILE${NC}"
    exit 1
fi

# Print deployment info
echo -e "${BLUE}🚀 UpNest DynamoDB Deployment${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "Environment: ${YELLOW}$ENVIRONMENT${NC}"
echo -e "Region: ${YELLOW}$REGION${NC}"
echo -e "Stack Name: ${YELLOW}$STACK_NAME${NC}"
echo -e "Billing Mode: ${YELLOW}$BILLING_MODE${NC}"
echo -e "Template: ${YELLOW}$TEMPLATE_FILE${NC}"
echo ""

# Check if stack already exists
echo -e "${BLUE}Checking if stack exists...${NC}"
if aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$REGION" &>/dev/null; then
    echo -e "${YELLOW}Stack exists. This will be an update operation.${NC}"
else
    echo -e "${GREEN}Stack does not exist. This will be a create operation.${NC}"
fi

# Validate CloudFormation template
echo -e "${BLUE}Validating CloudFormation template...${NC}"
if aws cloudformation validate-template --template-body file://"$TEMPLATE_FILE" --region "$REGION" &>/dev/null; then
    echo -e "${GREEN}✅ Template is valid${NC}"
else
    echo -e "${RED}❌ Template validation failed${NC}"
    exit 1
fi

# Deploy the stack
echo -e "${BLUE}Deploying CloudFormation stack...${NC}"
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --parameter-overrides \
        Environment="$ENVIRONMENT" \
        BillingMode="$BILLING_MODE" \
    --capabilities CAPABILITY_IAM \
    --no-fail-on-empty-changeset

# Check deployment status
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    
    # Get stack outputs
    echo -e "${BLUE}Stack Outputs:${NC}"
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' \
        --output table
        
    echo ""
    echo -e "${GREEN}🎉 All DynamoDB tables have been deployed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "1. Update your Lambda functions to use these table names"
    echo -e "2. Update your frontend API endpoints"
    echo -e "3. Test the database connections"
    echo -e "4. Run integration tests"
    
else
    echo -e "${RED}❌ Deployment failed${NC}"
    exit 1
fi

# Optional: Show table status
echo -e "${BLUE}Checking table status...${NC}"
TABLES=(
    "UpNest-Users-${ENVIRONMENT}"
    "UpNest-Babies-${ENVIRONMENT}"
    "UpNest-GrowthData-${ENVIRONMENT}"
    "UpNest-Vaccinations-${ENVIRONMENT}"
    "UpNest-Milestones-${ENVIRONMENT}"
)

for table in "${TABLES[@]}"; do
    STATUS=$(aws dynamodb describe-table --table-name "$table" --region "$REGION" --query 'Table.TableStatus' --output text 2>/dev/null || echo "NOT_FOUND")
    if [ "$STATUS" = "ACTIVE" ]; then
        echo -e "  ${GREEN}✅ $table: $STATUS${NC}"
    else
        echo -e "  ${YELLOW}⏳ $table: $STATUS${NC}"
    fi
done

echo ""
echo -e "${GREEN}🚀 UpNest DynamoDB deployment completed!${NC}"
