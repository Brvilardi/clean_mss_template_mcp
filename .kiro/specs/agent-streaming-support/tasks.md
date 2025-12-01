# Implementation Plan: Agent Streaming Support

## Overview
This implementation plan adds streaming response support to the Strands re:Invent agent Lambda function. The tasks are organized to build incrementally, starting with core streaming infrastructure, then adding event filtering and formatting, followed by frontend integration, and finally testing and optimization.

---

## Phase 1: Core Streaming Infrastructure

- [ ] 1. Add streaming endpoint to FastAPI application
  - Create `/invocations/stream` POST endpoint in `src/strands-agent/entrypoint.py`
  - Implement async event generator function `generate_stream_events()`
  - Use FastAPI's `StreamingResponse` with `media_type="text/event-stream"`
  - Reuse existing authentication logic from `/invocations` endpoint
  - Extract actor_id from Cognito JWT using same logic as non-streaming endpoint
  - _Requirements: 1.1, 1.5, 5.1, 5.2, 5.3, 5.4_

- [ ] 2. Implement event filtering and SSE formatting
  - Create `should_emit_event()` function to filter agent events
  - Filter out internal lifecycle events (init_event_loop, start_event_loop, message creation)
  - Emit text data events, tool use events, tool result events, and completion events
  - Format events as SSE messages: `data: {json}\n\n`
  - Add timestamp to all events in ISO 8601 format
  - _Requirements: 1.2, 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 3. Integrate Strands stream_async() method
  - Call `agent.stream_async(user_message)` in event generator
  - Iterate over async events from stream_async()
  - Pass filtered events to SSE formatter
  - Handle async iteration properly with `async for`
  - _Requirements: 1.2, 8.1_

- [ ] 4. Implement stream completion and error handling
  - Emit "done" event with session_id, usage stats, and metadata as final event
  - Emit "error" event for exceptions during streaming
  - Close stream gracefully after done/error events
  - Handle client disconnections by detecting broken pipe
  - Add try-except blocks around stream processing
  - _Requirements: 1.3, 1.4, 7.2, 7.3_

---

## Phase 2: Event Types and Data Models

- [ ] 5. Create Pydantic models for stream events
  - Create `StreamEvent` base model with type and timestamp fields
  - Create `TextEvent` model for text generation events
  - Create `ToolCallEvent` model for tool invocation events
  - Create `ToolResultEvent` model for tool completion events
  - Create `DoneEvent` model with usage and metadata
  - Create `ErrorEvent` model with error details
  - Add models to `src/strands-agent/entrypoint.py`
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ] 6. Implement event type detection and transformation
  - Detect text content events from agent stream
  - Detect tool_use events and extract tool name, tool_id
  - Detect tool_result events and extract tool_use_id, status
  - Transform agent events into typed event models
  - Serialize event models to JSON for SSE format
  - _Requirements: 3.2, 3.3, 3.4_

---

## Phase 3: Lambda Configuration and Deployment

- [ ] 7. Enable Lambda response streaming in CDK
  - Update `iac/iac/strands_agent_stack.py`
  - Set `invoke_mode=lambda_.InvokeMode.RESPONSE_STREAM` on function URL
  - Add environment variable `AWS_LWA_INVOKE_MODE=RESPONSE_STREAM`
  - Maintain backward compatibility with existing `/invocations` endpoint
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [ ] 8. Update API Gateway configuration for streaming
  - Update API Gateway integration in `iac/iac/strands_agent_stack.py`
  - Ensure API Gateway supports streaming responses (uses Lambda proxy integration)
  - Verify CORS configuration allows streaming headers
  - Test that API Gateway properly forwards streaming responses
  - Maintain existing authentication with Cognito authorizer
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 9. Update Lambda timeout and memory configuration
  - Verify timeout is sufficient for streaming (currently 120s)
  - Verify memory allocation supports streaming (currently 3008 MB)
  - Add CloudWatch log group configuration for streaming endpoint
  - _Requirements: 2.3, 8.4_

---

## Phase 4: Observability and Monitoring

- [ ] 10. Add logging for streaming invocations
  - Log streaming invocation start with session_id, actor_id, prompt length
  - Log each event type emitted (text, tool_call, tool_result, done, error)
  - Log stream completion with duration and event counts
  - Log errors with detailed context
  - Use AWS Lambda Powertools Logger
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 11. Add metrics for streaming invocations
  - Emit `StreamingInvocationStarted` metric
  - Emit `StreamingInvocationSuccess` metric on completion
  - Emit `StreamingInvocationFailure` metric on error
  - Emit `EventsEmitted` metric with count
  - Emit `StreamingDuration` metric
  - Emit `ClientDisconnection` metric when detected
  - Use AWS Lambda Powertools Metrics
  - _Requirements: 6.2, 6.3_

- [ ] 12. Add X-Ray tracing for streaming
  - Add subsegments for stream initialization
  - Add subsegments for event processing
  - Add annotations for event counts and types
  - Add annotations for stream duration
  - Use AWS Lambda Powertools Tracer
  - _Requirements: 6.5_

---

## Phase 5: Error Handling and Resilience

- [ ] 13. Implement error event creation
  - Create `create_error_event()` helper function
  - Map exception types to user-friendly error messages
  - Add suggestions for user action based on error type
  - Sanitize error details in production (use Config.is_production())
  - Handle MCP connection errors specifically
  - _Requirements: 7.1, 7.2, 7.4, 7.5_

- [ ] 14. Add client disconnection detection
  - Detect broken pipe or connection reset errors
  - Stop agent processing immediately on disconnection
  - Log disconnection event with context
  - Clean up resources properly
  - Emit disconnection metric
  - _Requirements: 7.3_

- [ ] 15. Implement timeout handling
  - Monitor elapsed time during streaming
  - Emit error event before Lambda timeout
  - Provide partial response if available
  - Log timeout with context
  - Suggest retry or query simplification
  - _Requirements: 7.4, 8.4_

---

## Phase 6: Frontend Integration

- [ ] 16. Create TypeScript streaming client
  - Create `streamAgentResponse()` async generator function
  - Implement fetch with ReadableStream reader
  - Parse SSE format (lines starting with "data: ")
  - Yield parsed JSON events
  - Handle connection errors and retries
  - Add to `frontend/src/services/agentService.ts`
  - _Requirements: 4.1, 4.5_

- [ ] 17. Update Chat component for streaming
  - Add state for streaming status (`isStreaming`)
  - Add state for accumulated response text
  - Add state for tool status display
  - Implement `handleStreamingQuery()` function
  - Process text events by appending to response
  - Process tool_call events by updating tool status
  - Process done events by updating usage stats
  - Process error events by displaying error message
  - Update `frontend/src/pages/Chat.tsx`
  - _Requirements: 4.2, 4.3, 4.4_

- [ ] 18. Add streaming UI indicators
  - Add loading indicator during streaming
  - Add tool usage indicators (e.g., "Using search_sessions...")
  - Add typing animation for streaming text
  - Disable input during streaming
  - Re-enable input on completion or error
  - Update `frontend/src/components/chat/ChatInput.tsx`
  - _Requirements: 4.3, 4.4_

---

## Phase 7: Testing

- [ ]* 19. Write unit tests for event filtering
  - Test `should_emit_event()` with various event types
  - Verify internal events are filtered out
  - Verify user-facing events are emitted
  - Test edge cases (empty events, malformed events)
  - Add to `tests/test_strands_agent/test_streaming.py`
  - _Requirements: 3.1_

- [ ]* 20. Write unit tests for event formatting
  - Test SSE format generation
  - Test JSON serialization of event models
  - Test timestamp generation
  - Test event model validation
  - Add to `tests/test_strands_agent/test_streaming.py`
  - _Requirements: 3.2, 3.3, 3.4, 3.5_

- [ ]* 21. Write unit tests for error handling
  - Test error event creation
  - Test error message sanitization
  - Test suggestion generation
  - Test exception type mapping
  - Add to `tests/test_strands_agent/test_streaming.py`
  - _Requirements: 7.1, 7.2, 7.5_

- [ ]* 22. Write integration tests for streaming endpoint
  - Test successful streaming invocation
  - Test authentication validation
  - Test session context preservation
  - Test error propagation
  - Mock agent.stream_async() for controlled testing
  - Add to `tests/test_strands_agent/test_streaming_integration.py`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 5.1, 5.2, 5.3, 5.4_

- [ ]* 23. Write property-based tests
  - **Property 1: Authentication Consistency** - For any streaming request, authentication should produce same result as non-streaming endpoint
  - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**
  - Generate random valid/invalid tokens
  - Verify both endpoints produce same auth results
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 24. Write property-based tests
  - **Property 2: Event Ordering** - For any agent invocation, text events should be emitted in generation order
  - **Validates: Requirements 1.2, 3.2**
  - Generate random prompts
  - Verify text events maintain order
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 25. Write property-based tests
  - **Property 3: Stream Completion** - For any successful invocation, stream should emit "done" event as final event
  - **Validates: Requirements 1.3, 3.4**
  - Generate random successful invocations
  - Verify all streams end with done event
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 26. Write property-based tests
  - **Property 4: Error Propagation** - For any error during streaming, error event should be emitted and stream should close gracefully
  - **Validates: Requirements 1.4, 7.2**
  - Generate random error scenarios
  - Verify error events are emitted
  - Verify streams close without hanging
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 27. Write property-based tests
  - **Property 5: Session Context Preservation** - For any streaming request with session_id, agent should maintain same context as non-streaming
  - **Validates: Requirements 1.5, 5.4**
  - Generate random session_ids
  - Verify context is preserved
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 28. Write property-based tests
  - **Property 6: Event Format Consistency** - For any emitted event, structure should conform to defined schema
  - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**
  - Generate random events
  - Verify all required fields present
  - Verify field types match schema
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 29. Write property-based tests
  - **Property 7: No Data Loss** - For any text generated by agent, all chunks should be emitted without loss or duplication
  - **Validates: Requirements 1.2, 8.1**
  - Generate random text responses
  - Verify all text appears in stream
  - Verify no duplication
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

- [ ]* 30. Write property-based tests
  - **Property 8: Observability Completeness** - For any streaming invocation, metrics and logs should be emitted for start, events, completion, and errors
  - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
  - Generate random invocations
  - Verify all observability events present
  - Add to `tests/test_strands_agent/test_streaming_properties.py`

---

## Phase 8: Documentation and Deployment

- [ ] 31. Update API documentation
  - Document `/invocations/stream` endpoint in `docs/API_REFERENCE.md`
  - Add request/response examples
  - Document SSE format
  - Document event types
  - Add authentication requirements
  - _Requirements: All_

- [ ] 32. Update deployment guide
  - Add streaming configuration steps to `docs/DEPLOYMENT_GUIDE.md`
  - Document Lambda Web Adapter configuration
  - Document environment variables
  - Add troubleshooting section
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 33. Final checkpoint - Verify all functionality
  - Deploy to staging environment
  - Test streaming endpoint manually
  - Test frontend integration
  - Verify metrics and logs in CloudWatch
  - Verify X-Ray traces
  - Test error scenarios
  - Test client disconnection handling
  - Verify backward compatibility with non-streaming endpoint
  - _Requirements: All_

---

## Notes

- **Testing Strategy**: This plan includes both unit tests and property-based tests. Unit tests verify specific behaviors, while property-based tests verify universal properties across many inputs.
- **Optional Tasks**: Tasks marked with `*` are optional and focus on comprehensive testing. Core functionality can be delivered without these tasks.
- **Incremental Development**: Each phase builds on the previous one, allowing for incremental testing and validation.
- **Backward Compatibility**: The existing `/invocations` endpoint remains unchanged, ensuring no disruption to current users.
