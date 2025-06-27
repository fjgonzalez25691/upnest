// AWS Cognito configuration for React
// Based on working vanilla JS configuration

export const cognitoConfig = {
  // Authority using the Cognito Identity Provider
  authority: 'https://cognito-idp.eu-south-2.amazonaws.com/eu-south-2_WInbcDDjo',

  // App Client ID
  client_id: '75g0r5a7bbp1mgpmqrg3e1iibm',
  
  // Redirect URIs
  redirect_uri: `${window.location.origin}/callback`,
  post_logout_redirect_uri: `${window.location.origin}`,
  silent_redirect_uri: `${window.location.origin}/callback`,
  
  // OAuth configuration
  response_type: 'code',
  scope: 'email openid profile',
  
  // Additional configuration
  automaticSilentRenew: true,
  loadUserInfo: true,
  
  // Cognito domain (corrected from your working config)
  cognitoDomain: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com',
  
  // Manual metadata configuration (required for AWS Cognito)
  metadata: {
    issuer: 'https://cognito-idp.eu-south-2.amazonaws.com/eu-south-2_WInbcDDjo',
    authorization_endpoint: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com/oauth2/authorize',
    token_endpoint: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com/oauth2/token',
    userinfo_endpoint: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com/oauth2/userInfo',
    end_session_endpoint: 'https://eu-south-2winbcddjo.auth.eu-south-2.amazoncognito.com/logout',
    jwks_uri: 'https://cognito-idp.eu-south-2.amazonaws.com/eu-south-2_WInbcDDjo/.well-known/jwks.json'
  }
};
