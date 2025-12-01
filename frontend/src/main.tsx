import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import amplifyOutputs from '../amplify_outputs.json'
import './index.css'
import App from './App.tsx'

// Always use amplify_outputs.json (ignore environment variables)
const userPoolId = amplifyOutputs.auth.user_pool_id;
const userPoolClientId = amplifyOutputs.auth.user_pool_client_id;
const identityPoolId = amplifyOutputs.auth.identity_pool_id;
const awsRegion = amplifyOutputs.auth.aws_region;
const cognitoDomain = amplifyOutputs.auth.oauth.domain;
const apiEndpoint = amplifyOutputs.custom.api.StrandsAgentAPI.endpoint;

// Debug: Log configuration being used
console.log('🔧 Amplify Configuration Debug:');
console.log('  Region:', awsRegion);
console.log('  User Pool ID:', userPoolId);
console.log('  Cognito Domain:', cognitoDomain);
console.log('  API Endpoint:', apiEndpoint);
console.log('  Full amplify_outputs.json:', amplifyOutputs);

// Configure Amplify with authentication and API settings
Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId,
      userPoolClientId,
      identityPoolId,
      loginWith: {
        oauth: {
          domain: cognitoDomain,
          scopes: amplifyOutputs.auth.oauth.scope,
          redirectSignIn: [amplifyOutputs.auth.oauth.redirect_sign_in],
          redirectSignOut: [amplifyOutputs.auth.oauth.redirect_sign_out],
          responseType: amplifyOutputs.auth.oauth.response_type as 'code' | 'token'
        },
        email: true
      }
    }
  },
  API: {
    REST: {
      StrandsAgentAPI: {
        endpoint: apiEndpoint,
        region: awsRegion
      }
    }
  }
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
