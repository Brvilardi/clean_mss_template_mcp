# Implementation Plan - Frontend Internationalization (i18n)

- [x] 1. Setup i18n infrastructure
  - Install required dependencies (i18next, react-i18next, i18next-browser-languagedetector, date-fns)
  - Create i18n directory structure
  - Create i18n configuration file
  - Initialize i18next in App.tsx
  - _Requirements: 3.1, 3.2_

- [x] 2. Create translation files and type definitions
  - Create pt-BR.json with Portuguese translations
  - Create en-US.json with English translations
  - Create TypeScript type definitions for translation keys
  - Configure TypeScript for type-safe translations
  - _Requirements: 1.2, 3.2, 7.1, 7.2_

- [x] 3. Create language management components and hooks
  - Create useLanguage custom hook
  - Create LanguageSwitcher component
  - Add LanguageSwitcher to Settings page
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 4. Create date/time formatting utilities
  - Create dateFormatter utility with locale support
  - Implement formatDate function
  - Implement formatTime function
  - Implement formatRelativeDate function
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 5. Update authentication components
  - Update SignInForm with translations
  - Update SignUpForm with translations
  - Update ConfirmSignUpForm with translations
  - Update auth error messages
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 6. Update chat components
  - Update Chat page with translations
  - Update ChatInput with translations
  - Update ChatHistory with translations
  - Update SessionIdDisplay with translations
  - Update empty state messages
  - Update loading state messages
  - Apply date/time formatting to chat messages
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 8.4_

- [x] 7. Update navigation and sidebar components
  - Update AppSidebar with translations
  - Update Dashboard with translations
  - Update Settings page with translations
  - Update aria-labels for accessibility
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 8. Update agent service to send language parameter
  - Update AgentInvocationRequest interface to include language field
  - Update sendMessage method to accept language parameter
  - Update sendMessageWithRetry to include language in request body
  - Extract ISO 639-1 language code from locale
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [x] 9. Update chat store to pass language to agent service
  - Import useLanguage hook in chatStore
  - Get current language code when sending messages
  - Pass language parameter to agentService.sendMessage
  - _Requirements: 9.1, 9.2_

- [x] 10. Update common UI components
  - Update LoadingFallback component
  - Update ErrorAlert component
  - Update Button labels throughout app
  - Update form validation messages
  - _Requirements: 1.2, 1.3_

- [ ]* 11. Write unit tests for i18n infrastructure
  - Test i18n configuration initialization
  - Test language detection from localStorage
  - Test fallback language behavior
  - _Requirements: 3.3_

- [ ]* 12. Write unit tests for LanguageSwitcher component
  - Test rendering with current language
  - Test language change triggers
  - Test dropdown options display
  - _Requirements: 2.1, 2.2_

- [ ]* 13. Write unit tests for useLanguage hook
  - Test language code extraction
  - Test language change callback
  - Test current language retrieval
  - _Requirements: 2.2, 2.4_

- [ ]* 14. Write unit tests for date formatter utilities
  - Test date formatting for pt-BR locale
  - Test date formatting for en-US locale
  - Test time formatting for both locales
  - Test relative date formatting
  - _Requirements: 8.1, 8.2, 8.3_

- [ ]* 15. Write unit tests for agent service language parameter
  - Test language parameter inclusion in requests
  - Test request without language parameter
  - Test language code format (ISO 639-1)
  - _Requirements: 9.3, 9.4_

- [ ]* 16. Write integration tests for language switching
  - Test complete flow of changing language
  - Verify all UI elements update
  - Verify persistence across page reloads
  - _Requirements: 2.2, 2.4_

- [ ]* 17. Write integration tests for agent API with language
  - Test language parameter sent correctly
  - Test language change during active session
  - _Requirements: 9.1, 9.2_

- [ ] 18. Final testing and refinement
  - Test all user flows with both languages
  - Verify date/time formatting in both locales
  - Test language persistence
  - Test agent API integration
  - Fix any issues found
  - _Requirements: All_

- [ ] 19. Documentation and deployment
  - Update README with i18n setup instructions
  - Document how to add new translations
  - Document how to add new languages
  - Deploy to staging for UAT
  - Deploy to production
  - _Requirements: All_
