// TypeScript type definitions for translation keys
export interface TranslationKeys {
  common: {
    loading: string;
    error: string;
    retry: string;
    cancel: string;
    save: string;
    delete: string;
    new: string;
    send: string;
  };
  auth: {
    signIn: string;
    signUp: string;
    signOut: string;
    email: string;
    password: string;
    confirmPassword: string;
    signingIn: string;
    signingUp: string;
    confirmationCode: string;
    confirmAccount: string;
    verifyEmail: string;
    verifying: string;
    companyName: string;
    companyWebsite: string;
    creatingAccount: string;
    emailVerified: string;
    codeResent: string;
    didntReceiveCode: string;
    resendCode: string;
    resending: string;
    verificationCodeSentTo: string;
    enterSixDigitCode: string;
    enterCodeFromEmail: string;
    pleaseVerifyEmail: string;
    placeholders: {
      email: string;
      password: string;
      companyName: string;
      companyWebsite: string;
      verificationCode: string;
    };
    errors: {
      invalidEmail: string;
      passwordTooShort: string;
      passwordsDoNotMatch: string;
      invalidCredentials: string;
      userNotFound: string;
      userAlreadyExists: string;
      signInFailed: string;
      signUpFailed: string;
      verificationFailed: string;
      resendFailed: string;
      codeRequired: string;
      codeMustBeSixDigits: string;
      codeMustBeNumbers: string;
    };
  };
  chat: {
    title: string;
    newChat: string;
    placeholder: string;
    placeholderLoading: string;
    placeholderOffline: string;
    placeholderThinking: string;
    welcome: string;
    welcomeMessage: string;
    tryAsking: string;
    thinking: string;
    aiAssistant: string;
    you: string;
    today: string;
    yesterday: string;
    messagesCount: string;
    emptyState: string;
    sessionId: string;
    loadingSessionHistory: string;
    aiIsThinking: string;
    askAboutSessions: string;
    noInternetConnection: string;
    offline: string;
    sendMessage: string;
    typeYourMessage: string;
    pressEnterToSend: string;
    exampleQuestions: {
      question1: string;
      question2: string;
      question3: string;
    };
    aria: {
      messageInput: string;
      conversationHistory: string;
      welcomeMessage: string;
      errorNotification: string;
      startNewChat: string;
      assistantTyping: string;
      youAreOffline: string;
    };
  };
  sidebar: {
    dashboard: string;
    chat: string;
    settings: string;
    chatHistory: string;
    newChat: string;
    signOut: string;
    aiAssistant: string;
    aria: {
      primaryNavigation: string;
      startNewChat: string;
      signOut: string;
    };
  };
  settings: {
    language: string;
    selectLanguage: string;
    title: string;
    preferences: string;
  };
  dashboard: {
    title: string;
    welcome: string;
  };
  errors: {
    generic: string;
    networkError: string;
    tryAgain: string;
  };
}

// Extend react-i18next module for type safety
declare module 'react-i18next' {
  interface CustomTypeOptions {
    resources: {
      translation: TranslationKeys;
    };
  }
}
