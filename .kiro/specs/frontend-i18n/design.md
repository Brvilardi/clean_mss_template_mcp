# Design Document - Frontend Internationalization (i18n)

## Overview

This document outlines the technical design for implementing internationalization (i18n) in the re:Invent Planner frontend application. The solution will use react-i18next, the industry-standard i18n framework for React applications, to provide seamless language switching between Portuguese (pt-BR) and English (en-US).

The design follows a modular approach with centralized translation management, type-safe translation keys, and automatic locale-based formatting for dates and times.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Application                        │
│                                                              │
│  ┌────────────────┐         ┌──────────────────┐           │
│  │   Components   │────────▶│  useTranslation  │           │
│  │                │         │      Hook        │           │
│  └────────────────┘         └──────────────────┘           │
│                                      │                       │
│                                      ▼                       │
│                          ┌──────────────────────┐           │
│                          │   i18next Instance   │           │
│                          │                      │           │
│                          │  - Language State    │           │
│                          │  - Translation Files │           │
│                          │  - Locale Formatting │           │
│                          └──────────────────────┘           │
│                                      │                       │
│                                      ▼                       │
│                          ┌──────────────────────┐           │
│                          │  Browser Storage     │           │
│                          │  (localStorage)      │           │
│                          └──────────────────────┘           │
└─────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │   Agent API          │
                          │   (with language     │
                          │    parameter)        │
                          └──────────────────────┘
```

### Component Structure

```
frontend/src/
├── i18n/
│   ├── config.ts                 # i18next configuration
│   ├── locales/
│   │   ├── pt-BR.json           # Portuguese translations
│   │   └── en-US.json           # English translations
│   └── types.ts                 # TypeScript type definitions
├── components/
│   ├── LanguageSwitcher.tsx     # Language selection component
│   └── [existing components]    # Updated with translations
├── hooks/
│   └── useLanguage.ts           # Custom hook for language management
└── services/
    └── agentService.ts          # Updated to send language parameter
```

## Components and Interfaces

### 1. i18n Configuration (`i18n/config.ts`)

```typescript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import ptBR from './locales/pt-BR.json';
import enUS from './locales/en-US.json';

const resources = {
  'pt-BR': { translation: ptBR },
  'en-US': { translation: enUS }
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'pt-BR',
    defaultNS: 'translation',
    interpolation: {
      escapeValue: false
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage']
    }
  });

export default i18n;
```

### 2. Translation Files Structure

**pt-BR.json:**
```json
{
  "common": {
    "loading": "Carregando...",
    "error": "Erro",
    "retry": "Tentar novamente",
    "cancel": "Cancelar",
    "save": "Salvar",
    "delete": "Excluir"
  },
  "auth": {
    "signIn": "Entrar",
    "signUp": "Criar conta",
    "signOut": "Sair",
    "email": "E-mail",
    "password": "Senha",
    "confirmPassword": "Confirmar senha",
    "signingIn": "Entrando...",
    "errors": {
      "invalidEmail": "E-mail inválido",
      "passwordTooShort": "Senha muito curta"
    }
  },
  "chat": {
    "title": "re:Invent Planner",
    "newChat": "Nova Conversa",
    "placeholder": "Pergunte sobre sessões do re:Invent...",
    "welcome": "Bem-vindo ao re:Invent Planner",
    "welcomeMessage": "Pergunte-me qualquer coisa sobre sessões, palestrantes ou ajuda para montar sua agenda personalizada.",
    "tryAsking": "Experimente perguntar:",
    "thinking": "Pensando...",
    "aiAssistant": "Assistente IA",
    "you": "Você",
    "today": "Hoje",
    "yesterday": "Ontem",
    "messagesCount": "{{count}} mensagens"
  },
  "sidebar": {
    "dashboard": "Painel",
    "chat": "Chat",
    "settings": "Configurações",
    "chatHistory": "Histórico de Conversas"
  },
  "settings": {
    "language": "Idioma",
    "selectLanguage": "Selecione o idioma"
  }
}
```

**en-US.json:**
```json
{
  "common": {
    "loading": "Loading...",
    "error": "Error",
    "retry": "Retry",
    "cancel": "Cancel",
    "save": "Save",
    "delete": "Delete"
  },
  "auth": {
    "signIn": "Sign In",
    "signUp": "Sign Up",
    "signOut": "Sign Out",
    "email": "Email",
    "password": "Password",
    "confirmPassword": "Confirm Password",
    "signingIn": "Signing in...",
    "errors": {
      "invalidEmail": "Invalid email",
      "passwordTooShort": "Password too short"
    }
  },
  "chat": {
    "title": "re:Invent Planner",
    "newChat": "New Chat",
    "placeholder": "Ask about re:Invent sessions...",
    "welcome": "Welcome to re:Invent Planner",
    "welcomeMessage": "Ask me anything about AWS re:Invent sessions, speakers, or help building your personalized schedule.",
    "tryAsking": "Try asking:",
    "thinking": "Thinking...",
    "aiAssistant": "AI Assistant",
    "you": "You",
    "today": "Today",
    "yesterday": "Yesterday",
    "messagesCount": "{{count}} messages"
  },
  "sidebar": {
    "dashboard": "Dashboard",
    "chat": "Chat",
    "settings": "Settings",
    "chatHistory": "Chat History"
  },
  "settings": {
    "language": "Language",
    "selectLanguage": "Select language"
  }
}
```

### 3. Language Switcher Component

```typescript
import { useTranslation } from 'react-i18next';
import { Globe } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const LANGUAGES = [
  { code: 'pt-BR', name: 'Português', flag: '🇧🇷' },
  { code: 'en-US', name: 'English', flag: '🇺🇸' }
];

export function LanguageSwitcher() {
  const { i18n } = useTranslation();

  const handleLanguageChange = (languageCode: string) => {
    i18n.changeLanguage(languageCode);
  };

  return (
    <Select value={i18n.language} onValueChange={handleLanguageChange}>
      <SelectTrigger className="w-[180px]">
        <Globe className="mr-2 h-4 w-4" />
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {LANGUAGES.map((lang) => (
          <SelectItem key={lang.code} value={lang.code}>
            <span className="mr-2">{lang.flag}</span>
            {lang.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

### 4. Custom Language Hook

```typescript
import { useTranslation } from 'react-i18next';
import { useCallback } from 'react';

export function useLanguage() {
  const { i18n, t } = useTranslation();

  const changeLanguage = useCallback((languageCode: string) => {
    i18n.changeLanguage(languageCode);
  }, [i18n]);

  const getCurrentLanguage = useCallback(() => {
    return i18n.language;
  }, [i18n]);

  const getLanguageCode = useCallback(() => {
    // Extract ISO 639-1 code (pt from pt-BR, en from en-US)
    return i18n.language.split('-')[0];
  }, [i18n]);

  return {
    t,
    currentLanguage: i18n.language,
    languageCode: getLanguageCode(),
    changeLanguage,
    getCurrentLanguage
  };
}
```

### 5. Updated Agent Service

```typescript
// Add language parameter to request interface
export interface AgentInvocationRequest {
  input: {
    prompt: string;
  };
  session_id?: string;
  language?: string; // ISO 639-1 code (pt, en)
}

// Update sendMessage method
static async sendMessage(
  prompt: string,
  sessionId?: string,
  language?: string
): Promise<AgentInvocationResponse> {
  return this.sendMessageWithRetry(prompt, sessionId, language, 0);
}

// Update internal retry method
private static async sendMessageWithRetry(
  prompt: string,
  sessionId: string | undefined,
  language: string | undefined,
  retryCount: number
): Promise<AgentInvocationResponse> {
  // ... existing code ...

  const request: AgentInvocationRequest = {
    input: { prompt },
    ...(sessionId && { session_id: sessionId }),
    ...(language && { language })
  };

  // ... rest of the method ...
}
```

### 6. Date/Time Formatting Utilities

```typescript
// utils/dateFormatter.ts
import { format, formatDistanceToNow } from 'date-fns';
import { ptBR, enUS } from 'date-fns/locale';

const LOCALE_MAP = {
  'pt-BR': ptBR,
  'en-US': enUS
};

export function formatDate(date: Date, locale: string): string {
  const dateLocale = LOCALE_MAP[locale as keyof typeof LOCALE_MAP] || enUS;
  return format(date, 'P', { locale: dateLocale });
}

export function formatTime(date: Date, locale: string): string {
  const dateLocale = LOCALE_MAP[locale as keyof typeof LOCALE_MAP] || enUS;
  const timeFormat = locale === 'pt-BR' ? 'HH:mm' : 'h:mm a';
  return format(date, timeFormat, { locale: dateLocale });
}

export function formatRelativeDate(date: Date, locale: string, t: (key: string) => string): string {
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return t('chat.today');
  } else if (date.toDateString() === yesterday.toDateString()) {
    return t('chat.yesterday');
  } else {
    return formatDate(date, locale);
  }
}
```

## Data Models

### Translation Key Structure

```typescript
// i18n/types.ts
export interface TranslationKeys {
  common: {
    loading: string;
    error: string;
    retry: string;
    cancel: string;
    save: string;
    delete: string;
  };
  auth: {
    signIn: string;
    signUp: string;
    signOut: string;
    email: string;
    password: string;
    confirmPassword: string;
    signingIn: string;
    errors: {
      invalidEmail: string;
      passwordTooShort: string;
    };
  };
  chat: {
    title: string;
    newChat: string;
    placeholder: string;
    welcome: string;
    welcomeMessage: string;
    tryAsking: string;
    thinking: string;
    aiAssistant: string;
    you: string;
    today: string;
    yesterday: string;
    messagesCount: string;
  };
  sidebar: {
    dashboard: string;
    chat: string;
    settings: string;
    chatHistory: string;
  };
  settings: {
    language: string;
    selectLanguage: string;
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
```

### Language Preference Storage

```typescript
// Stored in localStorage
interface LanguagePreference {
  language: string; // e.g., 'pt-BR' or 'en-US'
  timestamp: number;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Language persistence
*For any* language selection, when a user changes the language and reloads the application, the selected language should be restored from localStorage
**Validates: Requirements 2.4**

### Property 2: Translation key existence
*For any* translation key used in the application, the key should exist in both pt-BR.json and en-US.json translation files
**Validates: Requirements 3.3**

### Property 3: Language parameter transmission
*For any* agent API request, when a language is set in the application, the request should include the corresponding ISO 639-1 language code (pt or en)
**Validates: Requirements 9.1, 9.3**

### Property 4: Immediate UI update
*For any* language change, all visible UI text should update immediately without requiring a page reload
**Validates: Requirements 2.2**

### Property 5: Locale-based date formatting
*For any* date displayed in the application, the format should match the selected locale (DD/MM/YYYY for pt-BR, MM/DD/YYYY for en-US)
**Validates: Requirements 8.1**

### Property 6: Locale-based time formatting
*For any* time displayed in the application, the format should match the selected locale (24-hour for pt-BR, 12-hour for en-US)
**Validates: Requirements 8.2**

### Property 7: Fallback language
*For any* missing translation key, the system should display the English (en-US) translation as fallback
**Validates: Requirements 3.3**

## Error Handling

### Translation Errors

1. **Missing Translation Key**
   - Fallback to English translation
   - Log warning in development mode
   - Display key name in development, fallback text in production

2. **Invalid Language Code**
   - Fallback to default language (pt-BR)
   - Log error
   - Continue with fallback language

3. **Failed Language Change**
   - Keep current language
   - Show error message to user
   - Log error for debugging

### API Integration Errors

1. **Language Parameter Not Sent**
   - Agent API should handle missing language parameter gracefully
   - Default to English on backend if not provided
   - Log warning

2. **Invalid Language Code Sent**
   - Backend should validate and use fallback
   - Return error in response if needed

## Testing Strategy

### Unit Tests

1. **i18n Configuration Tests**
   - Test initialization with correct default language
   - Test language detection from localStorage
   - Test fallback language behavior

2. **Language Switcher Component Tests**
   - Test rendering with current language
   - Test language change triggers
   - Test dropdown options display

3. **useLanguage Hook Tests**
   - Test language code extraction
   - Test language change callback
   - Test current language retrieval

4. **Date Formatter Tests**
   - Test date formatting for pt-BR locale
   - Test date formatting for en-US locale
   - Test time formatting for both locales
   - Test relative date formatting

5. **Agent Service Tests**
   - Test language parameter inclusion in requests
   - Test request without language parameter
   - Test language code format (ISO 639-1)

### Integration Tests

1. **End-to-End Language Switching**
   - Test complete flow of changing language
   - Verify all UI elements update
   - Verify persistence across page reloads

2. **Agent API Integration**
   - Test language parameter sent correctly
   - Test agent responses in correct language
   - Test language change during active session

### Type Safety Tests

1. **Translation Key Type Checking**
   - Verify TypeScript catches invalid translation keys
   - Test autocomplete for translation keys
   - Test type errors for missing keys

## Implementation Notes

### Dependencies

```json
{
  "dependencies": {
    "i18next": "^23.7.0",
    "react-i18next": "^13.5.0",
    "i18next-browser-languagedetector": "^7.2.0",
    "date-fns": "^3.0.0"
  }
}
```

### Performance Considerations

1. **Lazy Loading**: Translation files are loaded synchronously on app init (small size)
2. **Caching**: i18next caches translations in memory
3. **Bundle Size**: Each translation file ~5-10KB (minimal impact)

### Accessibility

1. **Language Switcher**: Properly labeled with aria-label
2. **Screen Readers**: Announce language changes
3. **Keyboard Navigation**: Full keyboard support for language switcher

### Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- localStorage support required
- ES6+ features used (transpiled by Vite)

## Migration Strategy

### Phase 1: Setup Infrastructure
1. Install i18n dependencies
2. Create i18n configuration
3. Create initial translation files
4. Set up TypeScript types

### Phase 2: Component Updates
1. Update authentication components
2. Update chat components
3. Update sidebar and navigation
4. Update settings page

### Phase 3: API Integration
1. Update agentService to send language parameter
2. Update chatStore to pass language
3. Test API integration

### Phase 4: Testing & Refinement
1. Add unit tests
2. Add integration tests
3. Test all user flows
4. Fix any issues

### Phase 5: Deployment
1. Deploy to staging
2. User acceptance testing
3. Deploy to production
4. Monitor for issues
