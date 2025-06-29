# AWS Cognito Configuration for React App

## Current Configuration Status
✅ **Working vanilla JS config** - `prueba_cognito` folder  
🔄 **React app config** - `upnest` folder (being configured)

## Key Configuration Details

### User Pool Details
- **User Pool ID**: `eu-south-2_WInbcDDjo`
- **Client ID**: `75g0r5a7bbp1mgpmqrg3e1iibm`
- **Region**: `eu-south-2`
- **Cognito Domain**: `eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com`

### URLs Configuration (AWS Cognito Console)
Make sure these URLs are configured in your AWS Cognito App Client:

#### Callback URLs
```
http://localhost:5173/callback.html
http://localhost:3000/callback.html
https://your-production-domain.com/callback.html
```

#### Sign out URLs
```
http://localhost:5173/
http://localhost:3000/
https://your-production-domain.com/
```

### OAuth 2.0 Settings (AWS Cognito Console)
- **Allowed OAuth Flows**: Authorization code grant
- **Allowed OAuth Scopes**: email, openid, profile
- **Allowed OAuth Response Types**: code

## React App Configuration

### Environment Variables (.env)
```
VITE_COGNITO_USER_POOL_ID=eu-south-2_WInbcDDjo
VITE_COGNITO_CLIENT_ID=75g0r5a7bbp1mgpmqrg3e1iibm
VITE_COGNITO_DOMAIN=eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com
VITE_AWS_REGION=eu-south-2
VITE_REDIRECT_SIGN_IN=http://localhost:5173/callback.html
VITE_REDIRECT_SIGN_OUT=http://localhost:5173
VITE_REDIRECT_SILENT_RENEW=http://localhost:5173/silent-renew.html
```

### Files Modified/Created
1. ✅ `src/auth/cognitoConfig.js` - Main configuration file
2. ✅ `src/main.jsx` - Updated to use correct config
3. ✅ `src/App.jsx` - Updated logout function
4. ✅ `public/callback.html` - OAuth callback handler
5. ✅ `public/silent-renew.html` - Silent token renewal
6. ✅ `.env` - Environment variables
7. ✅ `vite.config.js` - Proxy configuration

## Testing Steps

1. **Start the dev server**:
   ```bash
   cd upnest
   npm run dev
   ```

2. **Access the app**: `http://localhost:5173`

3. **Test authentication flow**:
   - App should redirect to Cognito login
   - After login, should redirect to `/callback.html`
   - Then redirect back to main app

## Troubleshooting

### Common Issues
1. **CORS errors**: Check that domains match exactly in AWS console
2. **Redirect loops**: Verify callback URLs are correct
3. **Token errors**: Check that OAuth scopes are enabled
4. **Domain mismatch**: Ensure the domain in config matches AWS

### Debug Steps
1. Open browser dev tools
2. Monitor network requests to Cognito endpoints
3. Check console for authentication errors
4. Verify localStorage for user tokens

## Next Steps
1. Test the authentication flow
2. If working, deploy to production with correct domains
3. Update production environment variables
4. Configure production callback URLs in AWS
