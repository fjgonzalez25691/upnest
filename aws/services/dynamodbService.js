// UpNest DynamoDB Service Configuration
// This file contains all DynamoDB table configurations and service helpers

import AWS from 'aws-sdk';

// DynamoDB Configuration
const dynamoConfig = {
  region: process.env.AWS_REGION || 'us-east-1',
  endpoint: process.env.DYNAMODB_ENDPOINT || undefined, // For local development
};

// Initialize DynamoDB clients
export const dynamodb = new AWS.DynamoDB(dynamoConfig);
export const docClient = new AWS.DynamoDB.DocumentClient(dynamoConfig);

// Environment-based table names
const environment = process.env.ENVIRONMENT || 'dev';

export const TABLES = {
  USERS: `UpNest-Users-${environment}`,
  BABIES: `UpNest-Babies-${environment}`,
  GROWTH_DATA: `UpNest-GrowthData-${environment}`,
  VACCINATIONS: `UpNest-Vaccinations-${environment}`,
  MILESTONES: `UpNest-Milestones-${environment}`,
};

// Global Secondary Indexes
export const INDEXES = {
  // Users table
  EMAIL_INDEX: 'EmailIndex',
  
  // Babies table
  USER_BABIES_INDEX: 'UserBabiesIndex',
  ACTIVE_BABIES_INDEX: 'ActiveBabiesIndex',
  
  // Growth Data table
  BABY_GROWTH_INDEX: 'BabyGrowthIndex',
  USER_GROWTH_DATA_INDEX: 'UserGrowthDataIndex',
  BABY_MEASUREMENT_TYPE_INDEX: 'BabyMeasurementTypeIndex',
  
  // Vaccinations table
  BABY_VACCINATIONS_INDEX: 'BabyVaccinationsIndex',
  USER_VACCINATIONS_INDEX: 'UserVaccinationsIndex',
  UPCOMING_VACCINATIONS_INDEX: 'UpcomingVaccinationsIndex',
  
  // Milestones table
  BABY_MILESTONES_INDEX: 'BabyMilestonesIndex',
  USER_MILESTONES_INDEX: 'UserMilestonesIndex',
  MILESTONE_TYPE_INDEX: 'MilestoneTypeIndex',
};

// Common DynamoDB operations wrapper
export class DynamoDBService {
  constructor(tableName) {
    this.tableName = tableName;
  }

  async get(key) {
    try {
      const result = await docClient.get({
        TableName: this.tableName,
        Key: key,
      }).promise();
      return result.Item;
    } catch (error) {
      console.error(`Error getting item from ${this.tableName}:`, error);
      throw error;
    }
  }

  async put(item) {
    try {
      await docClient.put({
        TableName: this.tableName,
        Item: {
          ...item,
          createdAt: item.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      }).promise();
      return item;
    } catch (error) {
      console.error(`Error putting item to ${this.tableName}:`, error);
      throw error;
    }
  }

  async update(key, updateExpression, expressionAttributeValues, expressionAttributeNames = {}) {
    try {
      const params = {
        TableName: this.tableName,
        Key: key,
        UpdateExpression: updateExpression,
        ExpressionAttributeValues: {
          ...expressionAttributeValues,
          ':updatedAt': new Date().toISOString(),
        },
        ReturnValues: 'ALL_NEW',
      };

      if (Object.keys(expressionAttributeNames).length > 0) {
        params.ExpressionAttributeNames = expressionAttributeNames;
      }

      const result = await docClient.update(params).promise();
      return result.Attributes;
    } catch (error) {
      console.error(`Error updating item in ${this.tableName}:`, error);
      throw error;
    }
  }

  async delete(key) {
    try {
      await docClient.delete({
        TableName: this.tableName,
        Key: key,
      }).promise();
      return true;
    } catch (error) {
      console.error(`Error deleting item from ${this.tableName}:`, error);
      throw error;
    }
  }

  async query(keyConditionExpression, expressionAttributeValues, options = {}) {
    try {
      const params = {
        TableName: this.tableName,
        KeyConditionExpression: keyConditionExpression,
        ExpressionAttributeValues: expressionAttributeValues,
        ...options,
      };

      const result = await docClient.query(params).promise();
      return {
        items: result.Items,
        lastEvaluatedKey: result.LastEvaluatedKey,
        count: result.Count,
        scannedCount: result.ScannedCount,
      };
    } catch (error) {
      console.error(`Error querying ${this.tableName}:`, error);
      throw error;
    }
  }

  async queryIndex(indexName, keyConditionExpression, expressionAttributeValues, options = {}) {
    return this.query(keyConditionExpression, expressionAttributeValues, {
      ...options,
      IndexName: indexName,
    });
  }

  async scan(options = {}) {
    try {
      const result = await docClient.scan({
        TableName: this.tableName,
        ...options,
      }).promise();
      return {
        items: result.Items,
        lastEvaluatedKey: result.LastEvaluatedKey,
        count: result.Count,
        scannedCount: result.ScannedCount,
      };
    } catch (error) {
      console.error(`Error scanning ${this.tableName}:`, error);
      throw error;
    }
  }
}

// Specific service instances
export const usersService = new DynamoDBService(TABLES.USERS);
export const babiesService = new DynamoDBService(TABLES.BABIES);
export const growthDataService = new DynamoDBService(TABLES.GROWTH_DATA);
export const vaccinationsService = new DynamoDBService(TABLES.VACCINATIONS);
export const milestonesService = new DynamoDBService(TABLES.MILESTONES);

// Helper functions for common operations
export const helpers = {
  // Generate UUIDs for primary keys
  generateId: (prefix = '') => {
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
    return prefix ? `${prefix}-${uuid}` : uuid;
  },

  // Format dates consistently
  formatDate: (date = new Date()) => {
    return date.toISOString().split('T')[0]; // YYYY-MM-DD
  },

  formatDateTime: (date = new Date()) => {
    return date.toISOString(); // Full ISO string
  },

  // Validate user ownership (security helper)
  validateUserAccess: (itemUserId, requestUserId) => {
    if (itemUserId !== requestUserId) {
      throw new Error('Access denied: User can only access their own data');
    }
  },

  // Build query parameters for date ranges
  buildDateRangeQuery: (startDate, endDate) => {
    if (startDate && endDate) {
      return {
        keyCondition: 'measurementDate BETWEEN :startDate AND :endDate',
        values: {
          ':startDate': startDate,
          ':endDate': endDate,
        },
      };
    } else if (startDate) {
      return {
        keyCondition: 'measurementDate >= :startDate',
        values: {
          ':startDate': startDate,
        },
      };
    } else if (endDate) {
      return {
        keyCondition: 'measurementDate <= :endDate',
        values: {
          ':endDate': endDate,
        },
      };
    }
    return { keyCondition: '', values: {} };
  },

  // Pagination helper
  buildPaginationParams: (limit = 20, lastEvaluatedKey = null) => {
    const params = { Limit: limit };
    if (lastEvaluatedKey) {
      params.ExclusiveStartKey = lastEvaluatedKey;
    }
    return params;
  },
};

// Error handling wrapper for Lambda functions
export const withErrorHandling = (handler) => {
  return async (event, context) => {
    try {
      const result = await handler(event, context);
      return {
        statusCode: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
          'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        },
        body: JSON.stringify(result),
      };
    } catch (error) {
      console.error('Lambda execution error:', error);
      
      // Determine appropriate HTTP status code
      let statusCode = 500;
      if (error.message.includes('Access denied')) {
        statusCode = 403;
      } else if (error.message.includes('not found')) {
        statusCode = 404;
      } else if (error.message.includes('validation')) {
        statusCode = 400;
      }

      return {
        statusCode,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
        },
        body: JSON.stringify({
          error: error.message,
          requestId: context.requestId,
        }),
      };
    }
  };
};

// JWT token helper for extracting user info
export const extractUserFromToken = (event) => {
  try {
    // In API Gateway with Cognito authorizer, user info is in requestContext
    if (event.requestContext && event.requestContext.authorizer) {
      const claims = event.requestContext.authorizer.claims;
      return {
        userId: claims.sub,
        email: claims.email,
        name: claims.name || claims.given_name + ' ' + claims.family_name,
      };
    }

    // Fallback: try to decode JWT from Authorization header
    const authHeader = event.headers?.Authorization || event.headers?.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      const token = authHeader.substring(7);
      // Note: In production, you should validate the JWT signature
      const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
      return {
        userId: payload.sub,
        email: payload.email,
        name: payload.name || payload.given_name + ' ' + payload.family_name,
      };
    }

    throw new Error('No valid authentication token found');
  } catch (error) {
    console.error('Error extracting user from token:', error);
    throw new Error('Invalid or missing authentication token');
  }
};

export default {
  TABLES,
  INDEXES,
  DynamoDBService,
  usersService,
  babiesService,
  growthDataService,
  vaccinationsService,
  milestonesService,
  helpers,
  withErrorHandling,
  extractUserFromToken,
};
