import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { Amplify } from 'aws-amplify'
import amplifyOutputs from '../amplify_outputs.json'
import './index.css'
import App from './App.tsx'

// Use environment variables if available, otherwise fall back to amplify_outputs.json
const userPoolId = import.meta.env.VITE_USER_POOL_ID || amplifyOutputs.auth.user_pool_id;
const userPoolClientId = import.meta.env.VITE_USER_POOL_CLIENT_ID || amplifyOutputs.auth.user_pool_client_id;
const identityPoolId = import.meta.env.VITE_IDENTITY_POOL_ID || amplifyOutputs.auth.identity_pool_id;
const awsRegion = import.meta.env.VITE_AWS_REGION || amplifyOutputs.auth.aws_region;
const cognitoDomain = import.meta.env.VITE_COGNITO_DOMAIN || amplifyOutputs.auth.oauth.domain;
const apiEndpoint = import.meta.env.VITE_API_ENDPOINT || amplifyOutputs.custom.api.StrandsAgentAPI.endpoint;

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
