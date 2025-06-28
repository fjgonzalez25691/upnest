// UpNest Baby Management Service
// Handles all baby-related database operations

import { babiesService, INDEXES, helpers, extractUserFromToken, withErrorHandling } from './dynamodbService.js';

export class BabyService {
  // Create a new baby profile
  async createBaby(babyData, userId) {
    const babyId = helpers.generateId('baby');
    
    const baby = {
      babyId,
      userId,
      name: babyData.name,
      profilePicture: babyData.profilePicture || null,
      dateOfBirth: babyData.dateOfBirth,
      gender: babyData.gender,
      premature: babyData.premature || false,
      gestationalWeek: babyData.gestationalWeek || null,
      birthWeight: babyData.birthWeight || null,
      birthHeight: babyData.birthHeight || null,
      isActive: true,
      medicalInfo: babyData.medicalInfo || {
        allergies: [],
        conditions: [],
        medications: [],
        pediatrician: null
      },
      milestones: {},
      createdAt: helpers.formatDateTime(),
      updatedAt: helpers.formatDateTime()
    };

    await babiesService.put(baby);
    return baby;
  }

  // Get all babies for a user
  async getUserBabies(userId) {
    const result = await babiesService.queryIndex(
      INDEXES.USER_BABIES_INDEX,
      'userId = :userId',
      { ':userId': userId },
      {
        FilterExpression: 'isActive = :active',
        ExpressionAttributeValues: {
          ':userId': userId,
          ':active': true
        },
        ScanIndexForward: false // Most recent first
      }
    );

    return result.items;
  }

  // Get a specific baby by ID
  async getBaby(babyId, userId) {
    const baby = await babiesService.get({ babyId });
    
    if (!baby) {
      throw new Error('Baby not found');
    }

    // Validate user access
    helpers.validateUserAccess(baby.userId, userId);
    
    return baby;
  }

  // Update baby information
  async updateBaby(babyId, updateData, userId) {
    // First verify the baby exists and user has access
    await this.getBaby(babyId, userId);

    const updateExpression = [];
    const expressionAttributeValues = {};
    const expressionAttributeNames = {};

    // Build dynamic update expression
    const allowedFields = [
      'name', 'profilePicture', 'dateOfBirth', 'gender', 
      'premature', 'gestationalWeek', 'birthWeight', 'birthHeight',
      'medicalInfo', 'milestones'
    ];

    allowedFields.forEach(field => {
      if (updateData[field] !== undefined) {
        updateExpression.push(`#${field} = :${field}`);
        expressionAttributeNames[`#${field}`] = field;
        expressionAttributeValues[`:${field}`] = updateData[field];
      }
    });

    if (updateExpression.length === 0) {
      throw new Error('No valid fields provided for update');
    }

    const finalUpdateExpression = `SET ${updateExpression.join(', ')}, updatedAt = :updatedAt`;

    const updatedBaby = await babiesService.update(
      { babyId },
      finalUpdateExpression,
      expressionAttributeValues,
      expressionAttributeNames
    );

    return updatedBaby;
  }

  // Soft delete a baby (mark as inactive)
  async deleteBaby(babyId, userId) {
    // Verify baby exists and user has access
    await this.getBaby(babyId, userId);

    const updatedBaby = await babiesService.update(
      { babyId },
      'SET isActive = :inactive, updatedAt = :updatedAt',
      { ':inactive': false }
    );

    return updatedBaby;
  }

  // Calculate baby's age in various formats
  calculateAge(dateOfBirth, asOf = new Date()) {
    const birth = new Date(dateOfBirth);
    const now = new Date(asOf);
    
    const months = (now.getFullYear() - birth.getFullYear()) * 12 + 
                   (now.getMonth() - birth.getMonth());
    
    const days = Math.floor((now - birth) / (1000 * 60 * 60 * 24));
    
    return {
      months,
      days,
      years: Math.floor(months / 12),
      formatted: this.formatAge(months)
    };
  }

  // Format age for display
  formatAge(months) {
    if (months < 1) {
      return 'Newborn';
    } else if (months < 12) {
      return `${months} month${months !== 1 ? 's' : ''}`;
    } else {
      const years = Math.floor(months / 12);
      const remainingMonths = months % 12;
      
      if (remainingMonths === 0) {
        return `${years} year${years !== 1 ? 's' : ''}`;
      } else {
        return `${years} year${years !== 1 ? 's' : ''}, ${remainingMonths} month${remainingMonths !== 1 ? 's' : ''}`;
      }
    }
  }

  // Get baby statistics (for dashboard)
  async getBabyStats(babyId, userId) {
    const baby = await this.getBaby(babyId, userId);
    const age = this.calculateAge(baby.dateOfBirth);
    
    // TODO: Get growth data, vaccination status, milestones achieved
    // This would query other tables - implement after those services are ready
    
    return {
      baby,
      age,
      // nextVaccination: null,
      // recentGrowth: null,
      // milestonesAchieved: 0,
      // totalMilestones: 0
    };
  }
}

// Lambda function handlers
export const babyService = new BabyService();

// Create baby Lambda handler
export const createBabyHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyData = JSON.parse(event.body);
  
  // Validate required fields
  if (!babyData.name || !babyData.dateOfBirth || !babyData.gender) {
    throw new Error('Missing required fields: name, dateOfBirth, gender');
  }

  const baby = await babyService.createBaby(babyData, user.userId);
  return baby;
});

// Get user's babies Lambda handler
export const getUserBabiesHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babies = await babyService.getUserBabies(user.userId);
  return { babies };
});

// Get single baby Lambda handler
export const getBabyHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  
  const baby = await babyService.getBaby(babyId, user.userId);
  return baby;
});

// Update baby Lambda handler
export const updateBabyHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  const updateData = JSON.parse(event.body);
  
  const updatedBaby = await babyService.updateBaby(babyId, updateData, user.userId);
  return updatedBaby;
});

// Delete baby Lambda handler
export const deleteBabyHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  
  await babyService.deleteBaby(babyId, user.userId);
  return { message: 'Baby deleted successfully' };
});

// Get baby statistics Lambda handler
export const getBabyStatsHandler = withErrorHandling(async (event) => {
  const user = extractUserFromToken(event);
  const babyId = event.pathParameters.babyId;
  
  const stats = await babyService.getBabyStats(babyId, user.userId);
  return stats;
});

export default babyService;
