# Implementation Plan

- [x] 1. Create BFF Lambda function for chat history
  - Create `src/strands-agent/list_sessions_handler.py` with Lambda handler
  - Implement get_session_events() function to call AgentCore Memory API
  - Implement list_events() function with pagination
  - Parse and format events into messages
  - Handle JWT token validation for actor_id (using cognito:username)
  - Support query parameter ?session_id=xxx to fetch specific session events
  - Add error handling and logging
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.3, 4.4, 4.5, 7.2_

- [ ]* 1.1 Write unit tests for BFF Lambda
  - Test get_session_events API call with pagination
  - Test event parsing and formatting
  - Test JWT token extraction (cognito:username and sub)
  - Test query parameter handling
  - Test error handling
  - _Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 4.5_

- [x] 2. Add BFF Lambda to CDK infrastructure
  - Add list_sessions_function to strands_agent_stack.py
  - Configure environment variables (MEMORY_ID)
  - Add IAM permissions for bedrock-agentcore:ListEvents and GetEvent
  - Create /sessions API Gateway resource with GET method
  - Add Cognito authorizer integration
  - Add CORS configuration
  - _Requirements: 7.1_

- [x] 3. Rename Lambda handler to chat_history_handler
  - Rename `src/strands-agent/list_sessions_handler.py` to `chat_history_handler.py`
  - Update function name from `list_sessions_with_messages` to `get_chat_history`
  - Update CDK stack reference from `list_sessions_handler.lambda_handler` to `chat_history_handler.lambda_handler`
  - Update CDK function name from `list_sessions_function` to `chat_history_function`
  - Update all docstrings and comments to use "chat history" terminology
  - _Requirements: 7.1_

- [ ] 4. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Create frontend ChatHistoryService
  - Create `frontend/src/services/chatHistoryService.ts`
  - Implement getSessionEvents(sessionId) method with API Gateway integration
  - Add authentication token handling from Amplify
  - Implement error handling with user-friendly messages
  - Add retry logic with exponential backoff
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 5.1 Write unit tests for ChatHistoryService
  - Test API call construction with session_id query parameter
  - Test authentication token inclusion
  - Test response parsing
  - Test error handling
  - Test retry logic
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 6. Update chatStore with chat history management
  - Add chatHistory state array to store session metadata
  - Add loadChatHistory() action to fetch available sessions
  - Add loadSessionMessages(sessionId) action to fetch messages for a session
  - Add switchSession(sessionId) action to change active session
  - Keep sendMessage auto-generating session_id if new
  - Add session ordering by last_activity (most recent first)
  - Maintain localStorage for current session only (not full history)
  - _Requirements: 1.1, 1.3, 5.1, 5.2, 6.1, 6.3, 6.5_

- [ ]* 6.1 Write unit tests for chatStore history management
  - Test loadChatHistory action
  - Test loadSessionMessages action
  - Test switchSession action
  - Test session creation on first message
  - Test session ordering
  - _Requirements: 1.1, 1.3, 5.1, 5.2, 6.1, 6.5_

- [x] 7. Create ChatHistoryList component
  - Create `frontend/src/components/chat/ChatHistoryList.tsx`
  - Display all sessions from chatStore.chatHistory
  - Show truncated session hash (first 8 characters + "...")
  - Highlight active session with different background
  - Handle click to call chatStore.switchSession()
  - Show loading spinner while fetching
  - Show empty state when no sessions
  - Show message count or last message preview per session
  - _Requirements: 1.4, 1.5, 5.1, 5.4_

- [x] 8. Create SessionIdDisplay component
  - Create `frontend/src/components/chat/SessionIdDisplay.tsx`
  - Display current session hash in header
  - Show truncated hash by default (first 12 characters)
  - Implement copy-to-clipboard with navigator.clipboard API
  - Show tooltip with full hash on hover
  - Add visual feedback (checkmark icon) after copy
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 9. Update Chat page to integrate chat history
  - Update `frontend/src/pages/Chat.tsx`
  - Call chatStore.loadChatHistory() on component mount
  - Add ChatHistoryList to sidebar
  - Add SessionIdDisplay to header
  - Handle session switching to load messages via loadSessionMessages()
  - Show loading state during session load
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.3_

- [x] 10. Update AppSidebar to show chat history
  - Update `frontend/src/components/layout/AppSidebar.tsx`
  - Add "New Chat" button to create new session
  - Display ChatHistoryList component
  - Add section header "Chat History"
  - _Requirements: 1.4, 5.1_

- [ ] 11. Add error handling and user feedback
  - Update ChatHistoryService to throw user-friendly errors
  - Display error toast for failed session loads
  - Show retry button in ChatHistoryList on error
  - Display offline indicator when network unavailable
  - Handle session not found gracefully (404 from API)
  - _Requirements: 3.5, 4.6, 7.5_

- [ ] 12. Final Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Update Amplify configuration
  - Add /sessions endpoint to amplify_outputs.json generation script
  - Verify API Gateway endpoint URL for chat_history_handler
  - Update CORS to allow frontend domain
  - Test API integration end-to-end with ?session_id parameter
  - _Requirements: 7.1_
