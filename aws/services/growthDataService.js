// UpNest Growth Data Management Service
// Handles all growth measurement database operations

import { 
  growthDataService, 
  INDEXES, 
  helpers, 
  extractUserFromToken, 
  withErrorHandling 
} from './dynamodbService.js';

export class GrowthDataService {
  // Create a new growth measurement
  async createGrowthData(measurementData, userId) {
    const dataId = helpers.generateId('growth');
    
    const growthData = {
      dataId,
      babyId: measurementData.babyId,
      userId,
      measurementDate: measurementData.measurementDate,
      measurementType: measurementData.measurementType, // weight, height, head_circumference, bmi
      value: parseFloat(measurementData.value),
      unit: measurementData.unit,
      percentile: measurementData.percentile || null,
      zscore: measurementData.zscore || null,
      measurementSource: measurementData.measurementSource || 'manual',
      deviceInfo: measurementData.deviceInfo || null,
      notes: measurementData.notes || '',
      isEstimated: measurementData.isEstimated || false,
      createdAt: helpers.formatDateTime(),
      updatedAt: helpers.formatDateTime()
    };

    await growthDataService.put(growthData);
    return growthData;
  }

  // Get all growth data for a baby
  async getBabyGrowthData(babyId, userId, options = {}) {
    const {
      measurementType = null,
      startDate = null,
      endDate = null,
      limit = 100
    } = options;

    let indexName = INDEXES.BABY_GROWTH_INDEX;
    let keyCondition = 'babyId = :babyId';
    let expressionAttributeValues = { ':babyId': babyId };
    let filterExpression = 'userId = :userId';
    
    expressionAttributeValues[':userId'] = userId;

    // Add date range if specified
    if (startDate && endDate) {
      keyCondition += ' AND measurementDate BETWEEN :startDate AND :endDate';
      expressionAttributeValues[':startDate'] = startDate;
      expressionAttributeValues[':endDate'] = endDate;
    } else if (startDate) {
      keyCondition += ' AND measurementDate >= :startDate';
      expressionAttributeValues[':startDate'] = startDate;
    } else if (endDate) {
      keyCondition += ' AND measurementDate <= :endDate';
      expressionAttributeValues[':endDate'] = endDate;
    }

    // Add measurement type filter if specified
    if (measurementType) {
      filterExpression += ' AND measurementType = :measurementType';
      expressionAttributeValues[':measurementType'] = measurementType;
    }

    const result = await growthDataService.queryIndex(
      indexName,
      keyCondition,
      expressionAttributeValues,
      {
        FilterExpression: filterExpression,
        Limit: limit,
        ScanIndexForward: false // Most recent first
      }
    );

    return result.items;
  }

  // Get specific growth data entry
  async getGrowthData(dataId, userId) {
    const growthData = await growthDataService.get({ dataId });
    
    if (!growthData) {
      throw new Error('Growth data not found');
    }

    // Validate user access
    helpers.validateUserAccess(growthData.userId, userId);
    
    return growthData;
  }

  // Update growth data
  async updateGrowthData(dataId, updateData, userId) {
    // First verify the data exists and user has access
    await this.getGrowthData(dataId, userId);

    const updateExpression = [];
    const expressionAttributeValues = {};

    // Build dynamic update expression
    const allowedFields = [
      'value', 'unit', 'percentile', 'zscore', 'notes', 
      'isEstimated', 'deviceInfo', 'measurementSource'
    ];

    allowedFields.forEach(field => {
      if (updateData[field] !== undefined) {
        updateExpression.push(`${field} = :${field}`);
        expressionAttributeValues[`:${field}`] = updateData[field];
      }
    });

    if (updateExpression.length === 0) {
      throw new Error('No valid fields provided for update');
    }

    const finalUpdateExpression = `SET ${updateExpression.join(', ')}, updatedAt = :updatedAt`;

    const updatedData = await growthDataService.update(
      { dataId },
      finalUpdateExpression,
      expressionAttributeValues
    );

    return updatedData;
  }

  // Delete growth data
  async deleteGrowthData(dataId, userId) {
    // Verify data exists and user has access
    await this.getGrowthData(dataId, userId);

    await growthDataService.delete({ dataId });
    return true;
  }

  // Get growth data for chart visualization
  async getGrowthChart(babyId, userId, measurementTypes = ['weight', 'height']) {
    const chartData = {};

    for (const type of measurementTypes) {
      const data = await this.getBabyGrowthData(babyId, userId, {
        measurementType: type,
        limit: 200 // Enough for detailed chart
      });

      chartData[type] = data.map(item => ({
        date: item.measurementDate,
        value: item.value,
        percentile: item.percentile,
        zscore: item.zscore,
        notes: item.notes
      }));
    }

    return chartData;
  }

  // Get recent growth trends
  async getGrowthTrends(babyId, userId, days = 30) {
    const startDate = new Date();
    startDate.setDate(startDate.getDate() - days);
    
    const recentData = await this.getBabyGrowthData(babyId, userId, {
      startDate: helpers.formatDate(startDate),
      limit: 50
    });

    // Group by measurement type
    const trends = {};
    recentData.forEach(item => {
      if (!trends[item.measurementType]) {
        trends[item.measurementType] = [];
      }
      trends[item.measurementType].push(item);
    });

    // Calculate trend direction for each type
    const trendAnalysis = {};
    Object.keys(trends).forEach(type => {
      const measurements = trends[type].sort((a, b) => 
        new Date(a.measurementDate) - new Date(b.measurementDate)
      );
      
      if (measurements.length >= 2) {
        const first = measurements[0];
        const last = measurements[measurements.length - 1];
        const change = last.value - first.value;
        const percentChange = (change / first.value) * 100;
        
        trendAnalysis[type] = {
          direction: change > 0 ? 'increasing' : change < 0 ? 'decreasing' : 'stable',
          change,
          percentChange: Math.round(percentChange * 100) / 100,
          measurements: measurements.length,
          latest: last,
          oldest: first
        };
      }
    });

    return trendAnalysis;
  }

  // Batch create multiple measurements (for importing data)
  async batchCreateGrowthData(measurementsArray, userId) {
    const createdItems = [];
    
    for (const measurement of measurementsArray) {
      try {
        const created = await this.createGrowthData(measurement, userId);
        createdItems.push(created);
      } catch (error) {
        console.error(`Failed to create measurement:`, measurement, error);
        // Continue with other measurements
      }
    }
    
    return {
      created: createdItems.length,
      total: measurementsArray.length,
      items: createdItems
    };
  }

  // Get growth statistics summary
  async getGrowthSummary(babyId, userId) {
    const allData = await this.getBabyGrowthData(babyId, userId);
    
    const summary = {
      totalMeasurements: allData.length,
      measurementTypes: [...new Set(allData.map(item => item.measurementType))],
      dateRange: {
        first: null,
        last: null
      },
      averagePercentiles: {},
      recentTrends: await this.getGrowthTrends(babyId, userId, 30)
    };

    if (allData.length > 0) {
      const sortedByDate = allData.sort((a, b) => 
        new Date(a.measurementDate) - new Date(b.measurementDate)
      );
      
      summary.dateRange.first = sortedByDate[0].measurementDate;
      summary.dateRange.last = sortedByDate[sortedByDate.length - 1].measurementDate;

      // Calculate average percentiles by type
      const typeGroups = {};
      allData.forEach(item => {
        if (!typeGroups[item.measurementType]) {
          typeGroups[item.measurementType] = [];
        }
        if (item.percentile !== null) {
          typeGroups[item.measurementType].push(item.percentile);
        }
      });

      Object.keys(typeGroups).forEach(type => {
        const percentiles = typeGroups[type];
        if (percentiles.length > 0) {
          summary.averagePercentiles[type] = 
            Math.round((percentiles.reduce((sum, p) => sum + p, 0) / percentiles.length) * 10) / 10;
        }
      });
    }

    return summary;
  }
}

// Lambda function handlers
export const growthDataService_instance = new GrowthDataService();

// Create growth data Lambda handler
export const createGrowthDataHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const measurementData = JSON.parse(event.body);
  
  // Validate required fields
  const required = ['babyId', 'measurementDate', 'measurementType', 'value', 'unit'];
  for (const field of required) {
    if (!measurementData[field]) {
      throw new Error(`Missing required field: ${field}`);
    }
  }

  const growthData = await growthDataService_instance.createGrowthData(measurementData, user.userId);
  return growthData;
});

// Get baby's growth data Lambda handler
export const getBabyGrowthDataHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  const queryParams = event.queryStringParameters || {};
  
  const options = {
    measurementType: queryParams.type,
    startDate: queryParams.startDate,
    endDate: queryParams.endDate,
    limit: queryParams.limit ? parseInt(queryParams.limit) : 100
  };

  const growthData = await growthDataService_instance.getBabyGrowthData(babyId, user.userId, options);
  return { data: growthData };
});

// Get growth chart data Lambda handler
export const getGrowthChartHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  const queryParams = event.queryStringParameters || {};
  
  const types = queryParams.types ? queryParams.types.split(',') : ['weight', 'height'];
  const chartData = await growthDataService_instance.getGrowthChart(babyId, user.userId, types);
  
  return chartData;
});

// Update growth data Lambda handler  
export const updateGrowthDataHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const dataId = event.pathParameters.dataId;
  const updateData = JSON.parse(event.body);
  
  const updatedData = await growthDataService_instance.updateGrowthData(dataId, updateData, user.userId);
  return updatedData;
});

// Delete growth data Lambda handler
export const deleteGrowthDataHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const dataId = event.pathParameters.dataId;
  
  await growthDataService_instance.deleteGrowthData(dataId, user.userId);
  return { message: 'Growth data deleted successfully' };
});

// Get growth summary Lambda handler
export const getGrowthSummaryHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  
  const summary = await growthDataService_instance.getGrowthSummary(babyId, user.userId);
  return summary;
});

// Batch create growth data Lambda handler
export const batchCreateGrowthDataHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const { measurements } = JSON.parse(event.body);
  
  if (!Array.isArray(measurements)) {
    throw new Error('measurements must be an array');
  }

  const result = await growthDataService_instance.batchCreateGrowthData(measurements, user.userId);
  return result;
});

export default growthDataService_instance;
