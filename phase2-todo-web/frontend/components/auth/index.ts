/**
 * Authentication Components
 * Secure authentication forms and route guards with Better Auth integration
 */

export { LoginForm, type LoginFormProps } from './LoginForm'
export { RegisterForm, type RegisterFormProps } from './RegisterForm'
export {
  AuthGuard,
  withAuthGuard,
  useRequireAuth,
  AuthCheck,
  type AuthGuardProps,
  type AuthCheckProps,
} from './AuthGuard'
