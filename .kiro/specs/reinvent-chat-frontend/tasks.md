# Implementation Plan

- [x] 1. Set up React project structure and dependencies
  - Initialize Vite + React 19 + TypeScript project in `frontend/` directory
  - Install core dependencies: react-router-dom v7, tailwindcss, aws-amplify, zustand, lucide-react
  - Install shadcn/ui CLI and configure with Tailwind
  - Set up project folder structure as defined in design document
  - Configure Vite build settings with code splitting
  - Create `.env.local` template with required environment variables
  - _Requirements: 7.1, 7.4, 9.5_

- [x] 2. Configure AWS Amplify and authentication infrastructure
  - Create `amplify_outputs.json` configuration file with Cognito and API Gateway settings
  - Configure Amplify in `main.tsx` with authentication and API settings
  - Set up Cognito user pool with custom attributes (custom:company_name, custom:company_website)
  - Update IAC to include Cognito user pool and identity pool configuration
  - Configure API Gateway CORS settings for frontend origin
  - _Requirements: 1.3, 1.7, 2.5, 7.2, 7.3_

- [ ] 3. Implement authentication service and store
  - Create `services/authService.ts` with Cognito integration methods (signUp, signIn, signOut, getCurrentUser)
  - Create `store/authStore.ts` with Zustand for authentication state management
  - Implement sign-up with custom Cognito attributes (company_name, company_website)
  - Implement persistent authentication with token refresh
  - _Requirements: 1.3, 1.5, 1.7, 2.5_

- [x] 4. Build authentication UI components
  - Install and configure shadcn/ui components (Button, Input, Form, Label, Alert, Card)
  - Create `components/auth/SignUpForm.tsx` with email, password, company name, and company website fields
  - Create `components/auth/SignInForm.tsx` with email and password fields
  - Implement form validation for email format and URL format
  - Create `pages/auth/SignUp.tsx` and `pages/auth/SignIn.tsx` pages
  - Add error display for authentication failures
  - _Requirements: 1.1, 1.2, 1.4, 1.6, 2.1, 2.2, 2.3, 2.4, 8.3_

- [x] 5. Implement routing and layout structure
  - Create `routes.tsx` with public and private route configuration
  - Create `components/layout/PublicLayout.tsx` for auth pages
  - Create `components/layout/PrivateLayout.tsx` with sidebar and main content area
  - Create `components/layout/AppSidebar.tsx` with navigation links (Dashboard, Chat, Settings, Sign Out)
  - Implement route protection for authenticated routes
  - Add responsive mobile layout for sidebar
  - _Requirements: 5.2, 6.4_

- [x] 6. Create agent service and chat store
  - Create `services/agentService.ts` with API integration to Strands Agent endpoint
  - Implement `sendMessage()` method with proper request/response handling
  - Create error transformation for user-friendly messages
  - Create `store/chatStore.ts` with Zustand for chat state (messages, session, loading, errors)
  - Implement `sendMessage()` action with optimistic updates
  - Implement `clearMessages()` and `startNewSession()` actions
  - _Requirements: 3.1, 3.3, 3.4, 6.2, 8.1, 8.2, 8.4_

- [x] 7. Build chat interface components
  - Install shadcn/ui components (ScrollArea, Avatar, Badge, Skeleton, Textarea)
  - Create `components/chat/MessageBubble.tsx` for individual message display
  - Create `components/chat/ChatMessage.tsx` with user/assistant styling
  - Create `components/chat/ChatHistory.tsx` with auto-scroll and virtualization
  - Create `components/chat/ChatInput.tsx` with send button and Enter key support
  - Implement loading states with skeleton components
  - Implement empty message validation
  - _Requirements: 3.1, 3.2, 3.5, 4.1, 4.2, 4.5, 5.4, 5.5_

- [x] 8. Implement main chat page
  - Create `pages/Chat.tsx` with full-height layout
  - Integrate ChatHistory and ChatInput components
  - Implement message sending with loading states
  - Implement error handling and display
  - Add auto-scroll to latest message on new messages
  - Implement conversation history persistence in localStorage
  - Restore conversation on page refresh
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.2, 4.3, 9.2, 9.3_

- [x] 9. Create dashboard and settings pages
  - Create `pages/Dashboard.tsx` with welcome message and quick start guide
  - Display user's company name from Cognito attributes
  - Add sample queries section to help users get started
  - Create `pages/Settings.tsx` with user information display
  - Add clear conversation history functionality
  - Implement sign-out functionality
  - _Requirements: 5.1, 5.3_

- [x] 10. Implement new chat functionality
  - Add "New Chat" button to sidebar
  - Implement session reset on new chat
  - Clear conversation history and generate new session ID
  - Display welcome message or placeholder on new chat
  - Auto-focus input field on new chat
  - _Requirements: 6.1, 6.2, 6.3, 6.5_

- [x] 11. Add error handling and user feedback
  - Create `components/ErrorAlert.tsx` using shadcn Alert component
  - Implement network error detection and messaging
  - Implement service unavailable (503) error handling
  - Add retry functionality for failed requests
  - Implement actionable error suggestions
  - Create `store/uiStore.ts` for UI state management
  - _Requirements: 8.1, 8.2, 8.4, 8.5_

- [x] 12. Optimize performance and implement caching
  - Implement code splitting with React.lazy for pages
  - Add Suspense boundaries with loading fallbacks
  - Implement localStorage caching for conversation history
  - Add cache TTL and cleanup on sign out
  - Configure Vite build with manual chunks for vendor code
  - Implement message virtualization for long conversations (react-window or react-virtual)
  - _Requirements: 9.1, 9.2, 9.4, 9.5_

- [x] 13. Implement responsive design and styling
  - Configure Tailwind with Dati branding colors:
    - Primary: #655CC6 (purple)
    - Secondary: #5abceb (light blue)
    - Accent 1: #1fa0f3 (blue)
    - Accent 2: #f59d01 (orange)
    - Accent 3: #a4df64 (green)
    - Accent 4: #6838e8 (deep purple)
    - Background: #ffffff (white)
  - Use Dati logo from `frontend/public/dati-logo.png` in header/sidebar
  - Implement mobile-first responsive layouts
  - Add desktop optimizations for larger screens
  - Ensure proper spacing and visual hierarchy
  - Add focus states and keyboard navigation support
  - Test on multiple screen sizes
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [x] 14. Add accessibility features
  - Implement keyboard navigation for all interactive elements
  - Add proper ARIA labels and semantic HTML
  - Ensure WCAG AA color contrast compliance
  - Add alt text for images and icons
  - Test with screen readers
  - Implement focus management for modals and navigation
  - _Requirements: 5.4_

- [x] 15. Create FrontendStack CDK construct for S3 + CloudFront deployment
- [x] 15.1 Create `iac/iac/frontend_stack.py` as a Construct class
  - Import required CDK modules: aws_s3, aws_cloudfront, aws_cloudfront_origins, aws_s3_deployment, CfnOutput
  - Define __init__ method accepting scope, construct_id, stack_name, region
  - _Requirements: 7.1_
- [x] 15.2 Add S3 bucket for static website hosting
  - Create S3 bucket with website hosting enabled
  - Set index document to "index.html"
  - Set error document to "index.html" (for SPA routing)
  - Configure RemovalPolicy.DESTROY for dev/test
  - Enable auto_delete_objects=True for cleanup
  - Block public access but allow CloudFront access via OAI
  - _Requirements: 7.4_
- [x] 15.3 Add CloudFront Origin Access Identity (OAI)
  - Create OAI for secure S3 access
  - Grant S3 bucket read permissions to OAI
  - _Requirements: 7.4_
- [x] 15.4 Add CloudFront distribution
  - Create distribution with S3 origin using OAI
  - Set default root object to "index.html"
  - Configure custom error responses:
    - 404 → /index.html (200 status) for SPA routing
    - 403 → /index.html (200 status) for SPA routing
  - Set price class to PRICE_CLASS_200 (covers North America, Europe, Asia, Middle East, Africa, and South America)
  - Enable compression (compress=True)
  - Configure default cache behavior with caching optimized for static content
  - _Requirements: 7.4, 7.5_
- [x] 15.5 Add CfnOutputs for frontend URLs and bucket
  - Output CloudFront distribution domain name
  - Output CloudFront distribution URL (https://)
  - Output S3 bucket name for deployment scripts
  - _Requirements: 7.1_

- [x] 16. Integrate FrontendStack into TemplateStack and add deployment logic
- [x] 16.1 Integrate FrontendStack into TemplateStack
  - Import FrontendStack in `iac/iac/template_stack.py`
  - Instantiate FrontendStack after CognitoStack and API Gateway resources are created
  - Pass construct_id, stack_name, and region to FrontendStack
  - Store reference as self.frontend_stack
  - _Requirements: 7.1_
- [x] 16.2 Update generate_amplify_config.py for production deployment
  - Modify script to accept --cloudfront-url parameter for OAuth redirect URLs
  - Update OAuth redirect_sign_in and redirect_sign_out to use CloudFront URL
  - Keep localhost URLs as fallback for local development
  - Ensure script reads all required outputs: UserPoolId, UserPoolClientId, IdentityPoolId, UserPoolDomain, ApiGatewayBaseUrl
  - _Requirements: 7.2, 7.3_
- [x] 16.3 Generate amplify_outputs.json directly from CDK constructs
  - Modify `generate_amplify_config.py` to accept direct parameters instead of reading from CloudFormation:
    - Accept parameters: user_pool_id, user_pool_client_id, identity_pool_id, user_pool_domain, api_gateway_url, cloudfront_url, region
    - Generate amplify_outputs.json with these values
    - Update OAuth redirect URLs to include CloudFront URL when provided
  - In FrontendStack, create a custom resource or use CfnOutput to trigger amplify config generation:
    - Pass cognito_stack properties (user_pool.user_pool_id, user_pool_client.user_pool_client_id, etc.)
    - Pass API Gateway URL from template_stack (self.rest_api.url)
    - Pass CloudFront distribution URL from frontend_stack
    - Write amplify_outputs.json to frontend/ directory during CDK synthesis
  - Alternative approach: Use CDK custom resource with Lambda to generate file during deployment
  - _Requirements: 7.2, 7.3, 7.4_
- [x] 16.3.1 Create build and deployment script `iac/scripts/build_and_deploy_frontend.sh`
  - Bash script that runs during CDK deployment:
    1. Check if amplify_outputs.json exists in frontend/ directory
    2. Run `npm install` in frontend directory
    3. Run `npm run build` in frontend directory to create dist/
    4. Script will be called by BucketDeployment construct (task 16.5)
  - Add proper error handling and exit codes
  - Make script executable: `chmod +x iac/scripts/build_and_deploy_frontend.sh`
  - _Requirements: 7.4, 7.5_
- [x] 16.4 Update Cognito OAuth redirect URLs to include CloudFront URL
  - Modify CognitoStack to accept optional cloudfront_url parameter
  - Update callback_urls and logout_urls to include CloudFront URL when provided
  - Keep localhost URLs for local development
  - _Requirements: 1.3, 7.3_
- [x] 16.5 Add BucketDeployment construct for automatic frontend deployment
  - Import aws_s3_deployment in frontend_stack.py
  - Add BucketDeployment construct that:
    - Sources from local frontend/dist directory
    - Deploys to S3 bucket
    - Invalidates CloudFront distribution on changes
    - Prunes old files from bucket
  - Note: This requires frontend to be built BEFORE cdk deploy
  - _Requirements: 7.4, 7.5_
- [x] 16.6 Create deployment documentation
  - Document the deployment process in README or docs/DEPLOYMENT_GUIDE.md:
    1. Build frontend locally: `cd frontend && npm run build`
    2. Deploy CDK stack: `cd iac && cdk deploy`
    3. Or use helper script: `python iac/scripts/deploy_frontend.py --stack-name <name> --region <region>`
  - Document environment variables needed
  - Document how to update OAuth URLs in Cognito after first deployment
  - _Requirements: 7.1, 7.5_

- [ ] 17. Checkpoint - Ensure all core functionality works
  - Verify sign-up flow with custom attributes
  - Verify sign-in and persistent authentication
  - Verify chat message sending and receiving
  - Verify new chat functionality
  - Verify error handling for all scenarios
  - Verify responsive design on mobile and desktop
  - Ensure all tests pass, ask the user if questions arise.
