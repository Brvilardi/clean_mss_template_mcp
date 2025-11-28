import { z } from 'zod';
import i18n from '../i18n/config';

// Helper function to get translation
const t = (key: string) => i18n.t(key);

// List of common free email providers to exclude
const FREE_EMAIL_PROVIDERS = [
  'gmail.com',
  'yahoo.com',
  'hotmail.com',
  'outlook.com',
  'live.com',
  'aol.com',
  'icloud.com',
  'mail.com',
  'protonmail.com',
  'zoho.com',
  'yandex.com',
  'gmx.com',
];

export const emailSchema = z
  .string()
  .min(1, { message: t('validation.emailRequired') })
  .email({ message: t('validation.invalidEmail') })
  .refine(
    (email) => {
      const domain = email.split('@')[1]?.toLowerCase();
      return domain && !FREE_EMAIL_PROVIDERS.includes(domain);
    },
    { message: t('validation.corporateEmailRequired') }
  );

export const passwordSchema = z
  .string()
  .min(8, { message: t('validation.passwordMinLength') })
  .regex(/[A-Z]/, { message: t('validation.passwordUppercase') })
  .regex(/[a-z]/, { message: t('validation.passwordLowercase') })
  .regex(/[0-9]/, { message: t('validation.passwordNumber') })
  .regex(/[^A-Za-z0-9]/, { message: t('validation.passwordSpecialChar') });

export const urlSchema = z
  .string()
  .min(1, { message: t('validation.websiteRequired') })
  .refine(
    (url) => {
      // Remove protocol if present
      const cleanUrl = url.replace(/^https?:\/\//, '');
      // Basic domain validation
      const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z]{2,})+$/;
      return domainRegex.test(cleanUrl);
    },
    { message: t('validation.invalidDomain') }
  );

export const companyNameSchema = z
  .string()
  .min(2, { message: t('validation.companyNameMinLength') })
  .max(100, { message: t('validation.companyNameMaxLength') });

export const signUpSchema = z
  .object({
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, { message: t('validation.confirmPasswordRequired') }),
    companyName: companyNameSchema,
    companyWebsite: urlSchema,
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: t('validation.passwordsDoNotMatch'),
    path: ['confirmPassword'],
  });

export const signInSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, { message: t('validation.passwordRequired') }),
});

export type SignUpFormData = z.infer<typeof signUpSchema>;
export type SignInFormData = z.infer<typeof signInSchema>;
