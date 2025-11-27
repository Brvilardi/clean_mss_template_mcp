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
