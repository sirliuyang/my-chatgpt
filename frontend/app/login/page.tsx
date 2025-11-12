// app/login/page.tsx
'use client';

import {useState, useEffect, type FormEvent, type ChangeEvent} from 'react';
import {useRouter} from 'next/navigation';
import {login, register, AuthManager} from '@/lib/auth';
import type {LoginRequest, RegisterRequest} from '@/lib/types/auth';

type FormMode = 'login' | 'register';

export default function LoginPage() {
    const router = useRouter();
    const [mode, setMode] = useState<FormMode>('login');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isCheckingAuth, setIsCheckingAuth] = useState(true);

    // 表单数据
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        name: '',
        confirmPassword: '',
    });

    // 检查是否已登录,如果已登录则重定向到主页
    useEffect(() => {
        if (AuthManager.isAuthenticated()) {
            router.push('/');
        } else {
            setIsCheckingAuth(false);
        }
    }, [router]);

    // 处理输入变化
    const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
        const {name, value} = e.target;
        setFormData((prev) => ({...prev, [name]: value}));
        setError(null);
    };

    // 表单验证
    const validateForm = (): string | null => {
        if (!formData.email || !formData.password) {
            return 'Email and password are required';
        }

        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
            return 'Invalid email format';
        }

        if (formData.password.length < 6) {
            return 'Password must be at least 6 characters';
        }

        if (mode === 'register') {
            if (!formData.name || formData.name.trim().length === 0) {
                return 'Name is required';
            }

            if (formData.password !== formData.confirmPassword) {
                return 'Passwords do not match';
            }
        }

        return null;
    };

    // 处理登录
    const handleLogin = async (e: FormEvent) => {
        e.preventDefault();
        const validationError = validateForm();
        if (validationError) {
            setError(validationError);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const loginData: LoginRequest = {
                email: formData.email,
                password: formData.password,
            };

            await login(loginData);
            // 登录成功后跳转到主页
            router.push('/');
        } catch (err: any) {
            console.error('Login error:', err);
            const errorMsg = err.response?.data?.detail || 'Invalid email or password';
            setError(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    // 处理注册
    const handleRegister = async (e: FormEvent) => {
        e.preventDefault();
        const validationError = validateForm();
        if (validationError) {
            setError(validationError);
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const registerData: RegisterRequest = {
                email: formData.email,
                name: formData.name,
                password: formData.password,
            };

            await register(registerData);

            // 注册成功后自动登录
            const loginData: LoginRequest = {
                email: formData.email,
                password: formData.password,
            };
            await login(loginData);

            // 登录成功后跳转到主页
            router.push('/');
        } catch (err: any) {
            console.error('Register error:', err);
            const errorMsg = err.response?.data?.detail || 'Registration failed. Please try again.';
            setError(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmit = mode === 'login' ? handleLogin : handleRegister;

    // 如果正在检查认证状态,显示加载页面
    if (isCheckingAuth) {
        return (
            <div
                className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
                <div className="text-center">
                    <div className="size-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"/>
                    <p className="text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div
            className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 px-4">
            <div className="max-w-md w-full space-y-8 bg-white dark:bg-gray-800 p-8 rounded-2xl shadow-xl">
                {/* Header */}
                <div className="text-center">
                    <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                        {mode === 'login' ? 'Welcome Back' : 'Create Account'}
                    </h2>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        {mode === 'login'
                            ? 'Sign in to continue to Leon AI'
                            : 'Sign up to get started'}
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="mt-8 space-y-6">
                    <div className="space-y-4">
                        {/* Name (only for register) */}
                        {mode === 'register' && (
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Name
                                </label>
                                <input
                                    id="name"
                                    name="name"
                                    type="text"
                                    required={mode === 'register'}
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                    placeholder="John Doe"
                                />
                            </div>
                        )}

                        {/* Email */}
                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Email
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                value={formData.email}
                                onChange={handleChange}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                placeholder="you@example.com"
                            />
                        </div>

                        {/* Password */}
                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                                required
                                value={formData.password}
                                onChange={handleChange}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                placeholder="••••••••"
                            />
                        </div>

                        {/* Confirm Password (only for register) */}
                        {mode === 'register' && (
                            <div>
                                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Confirm Password
                                </label>
                                <input
                                    id="confirmPassword"
                                    name="confirmPassword"
                                    type="password"
                                    autoComplete="new-password"
                                    required={mode === 'register'}
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                    className="mt-1 block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                    placeholder="••••••••"
                                />
                            </div>
                        )}
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div
                            className="bg-red-50 dark:bg-red-900/20 border border-red-400 dark:border-red-600 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg text-sm">
                            {error}
                        </div>
                    )}

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {isLoading ? (
                            <div className="flex items-center gap-2">
                                <div className="size-4 border-2 border-white border-t-transparent rounded-full animate-spin"/>
                                <span>{mode === 'login' ? 'Signing in...' : 'Creating account...'}</span>
                            </div>
                        ) : (
                            mode === 'login' ? 'Sign In' : 'Sign Up'
                        )}
                    </button>

                    {/* Toggle Mode */}
                    <div className="text-center">
                        <button
                            type="button"
                            onClick={() => {
                                setMode(mode === 'login' ? 'register' : 'login');
                                setError(null);
                                setFormData({email: '', password: '', name: '', confirmPassword: ''});
                            }}
                            className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium"
                        >
                            {mode === 'login'
                                ? "Don't have an account? Sign up"
                                : 'Already have an account? Sign in'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}