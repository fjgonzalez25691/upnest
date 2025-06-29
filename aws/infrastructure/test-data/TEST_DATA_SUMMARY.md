# Test Data Summary for JWT Testing

## JWT Token IDs (from jwt_generator.py)
- user-1-test-123456: User One (user1@test.com)
- user-2-test-789012: User Two (user2@test.com)  
- admin-test-456789: Admin User (admin@test.com)

## Updated Test Data Files

### Users
- users-test-data.json ✓ (contains all 3 users with correct IDs)
- user-test.json ✓ (user-1-test-123456)
- user2-test.json ✓ (user-2-test-789012)

### Babies
- baby1-user1.json ✓ (Emma Sofia - user-1-test-123456)
- baby1-user2.json ✓ (Lucas Miguel - user-2-test-789012)
- baby-test.json ✓ (baby-test-001-user1 - user-1-test-123456)
- baby-test-user2.json ✓ (baby-test-002-user2 - user-2-test-789012)
- baby-user1.json ✓ (baby-001-user1 - user-1-test-123456)

### Growth Data
- growth-data-test.json ✓ (user-1-test-123456)
- growth-data-test-user2.json ✓ (user-2-test-789012)

### Milestones
- milestone-test.json ✓ (user-1-test-123456)
- milestone-test-user2.json ✓ (user-2-test-789012)

### Vaccinations
- vaccination-test.json ✓ (user-1-test-123456)

### Query Files
- user-query.json ✓ (user-1-test-123456)
- user-id-query.json ✓ (user-1-test-123456)
- user2-query.json ✓ (user-2-test-789012)
- email-query.json ✓ (user1@test.com)
- email-query-user2.json ✓ (user2@test.com)

## Data Consistency
✅ All userIds now match JWT sub claims
✅ All dates are consistent and recent
✅ Field names standardized (modifiedAt vs updatedAt)
✅ All items include proper DynamoDB format with type descriptors
✅ Cross-references between users, babies, and related data are consistent

## Next Steps
1. Load this test data into local DynamoDB tables
2. Run unit tests for JWT validation and DynamoDB utilities
3. Test all CRUD endpoints with proper JWT authorization
4. Validate data isolation between users
