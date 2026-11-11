import { format } from 'date-fns';
import { ptBR, enUS } from 'date-fns/locale';

const LOCALE_MAP = {
  'pt-BR': ptBR,
  'en-US': enUS
} as const;

type SupportedLocale = keyof typeof LOCALE_MAP;

/**
 * Formats a date according to the specified locale
 * @param date - The date to format
 * @param locale - The locale to use for formatting (pt-BR or en-US)
 * @returns Formatted date string (DD/MM/YYYY for pt-BR, MM/DD/YYYY for en-US)
 */
export function formatDate(date: Date, locale: string): string {
  const dateLocale = LOCALE_MAP[locale as SupportedLocale] || enUS;
  return format(date, 'P', { locale: dateLocale });
}

/**
 * Formats a time according to the specified locale
 * @param date - The date to format
 * @param locale - The locale to use for formatting (pt-BR or en-US)
 * @returns Formatted time string (24-hour for pt-BR, 12-hour for en-US)
 */
export function formatTime(date: Date, locale: string): string {
  const dateLocale = LOCALE_MAP[locale as SupportedLocale] || enUS;
  const timeFormat = locale === 'pt-BR' ? 'HH:mm' : 'h:mm a';
  return format(date, timeFormat, { locale: dateLocale });
}

/**
 * Formats a date relative to today (Today, Yesterday, or formatted date)
 * @param date - The date to format
 * @param locale - The locale to use for formatting
 * @param t - Translation function for "today" and "yesterday"
 * @returns Relative date string or formatted date
 */
export function formatRelativeDate(
  date: Date,
  locale: string,
  t: (key: string) => string
): string {
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
