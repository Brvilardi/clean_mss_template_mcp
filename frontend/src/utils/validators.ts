import { z } from 'zod';

export const emailSchema = z
  .string()
  .min(1, 'Email is required')
  .email('Invalid email address');

export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Must contain uppercase letter')
  .regex(/[a-z]/, 'Must contain lowercase letter')
  .regex(/[0-9]/, 'Must contain number')
  .regex(/[^A-Za-z0-9]/, 'Must contain special character');

export const urlSchema = z
  .string()
  .min(1, 'Website is required')
  .url('Invalid URL')
  .refine(
    (url) => url.startsWith('http://') || url.startsWith('https://'),
    'URL must start with http:// or https://'
  );

export const companyNameSchema = z
  .string()
  .min(2, 'Company name must be at least 2 characters')
  .max(100, 'Company name must be less than 100 characters');

export const signUpSchema = z
  .object({
    email: emailSchema,
    password: passwordSchema,
    confirmPassword: z.string().min(1, 'Confirm your password'),
    companyName: companyNameSchema,
    companyWebsite: urlSchema,
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

export const signInSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Password is required'),
});

export type SignUpFormData = z.infer<typeof signUpSchema>;
export type SignInFormData = z.infer<typeof signInSchema>;
