// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
import axios from 'axios';
import type {LoginRequest, LoginResponse, RegisterRequest, TokenResponse, User, RefreshTokenRequest} from './types/auth';

// 使用相对路径,通过 Next.js proxy 转发
const API_BASE_URL = '';

// 创建 axios 实例
const authClient = axios.create({
    baseURL: API_BASE_URL,
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Token 存储键名
const TOKEN_KEYS = {
    ACCESS_TOKEN: 'access_token',
    REFRESH_TOKEN: 'refresh_token',
    EXPIRES_AT: 'expires_at',
    USER: 'user',
} as const;

// ============= Token 管理 =============

export class AuthManager {
    // 保存认证信息
    static saveAuth(loginResponse: LoginResponse): void {
        const expiresAt = Date.now() + loginResponse.expires_in * 1000;

        localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, loginResponse.access_token);
        localStorage.setItem(TOKEN_KEYS.REFRESH_TOKEN, loginResponse.refresh_token);
        localStorage.setItem(TOKEN_KEYS.EXPIRES_AT, expiresAt.toString());
        localStorage.setItem(TOKEN_KEYS.USER, JSON.stringify(loginResponse.user));
    }

    // 获取 Access Token
    static getAccessToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEYS.ACCESS_TOKEN);
    }

    // 获取 Refresh Token
    static getRefreshToken(): string | null {
        if (typeof window === 'undefined') return null;
        return localStorage.getItem(TOKEN_KEYS.REFRESH_TOKEN);
    }

    // 获取用户信息
    static getUser(): User | null {
        if (typeof window === 'undefined') return null;
        const userStr = localStorage.getItem(TOKEN_KEYS.USER);
        return userStr ? JSON.parse(userStr) : null;
    }

    // 检查 Token 是否过期
    static isTokenExpired(): boolean {
        if (typeof window === 'undefined') return true;
        const expiresAt = localStorage.getItem(TOKEN_KEYS.EXPIRES_AT);
        if (!expiresAt) return true;
        return Date.now() >= parseInt(expiresAt);
    }

    // 清除所有认证信息
    static clearAuth(): void {
        if (typeof window === 'undefined') return;
        localStorage.removeItem(TOKEN_KEYS.ACCESS_TOKEN);
        localStorage.removeItem(TOKEN_KEYS.REFRESH_TOKEN);
        localStorage.removeItem(TOKEN_KEYS.EXPIRES_AT);
        localStorage.removeItem(TOKEN_KEYS.USER);
    }

    // 检查是否已登录
    static isAuthenticated(): boolean {
        const token = this.getAccessToken();
        return token !== null && !this.isTokenExpired();
    }

    // 更新 Access Token
    static updateAccessToken(accessToken: string): void {
        if (typeof window === 'undefined') return;
        localStorage.setItem(TOKEN_KEYS.ACCESS_TOKEN, accessToken);
    }
}

// ============= API 请求拦截器 =============

// 请求拦截器 - 自动添加 Token
authClient.interceptors.request.use(
    (config) => {
        const token = AuthManager.getAccessToken();
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// 响应拦截器 - 自动刷新 Token
authClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        // 如果是 401 错误且未重试过
        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            try {
                const refreshToken = AuthManager.getRefreshToken();
                if (refreshToken) {
                    const newAccessToken = await refreshAccessToken(refreshToken);
                    AuthManager.updateAccessToken(newAccessToken);
                    originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
                    return authClient(originalRequest);
                }
            } catch (refreshError) {
                // 刷新失败,清除认证信息
                AuthManager.clearAuth();
                if (typeof window !== 'undefined') {
                    window.location.href = '/login';
                }
                return Promise.reject(refreshError);
            }
        }

        return Promise.reject(error);
    }
);

// ============= 认证 API =============

// 用户注册
export async function register(data: RegisterRequest): Promise<User> {
    const response = await authClient.post<User>('/api/v1/users/register', data);
    return response.data;
}

// 用户登录
export async function login(data: LoginRequest): Promise<LoginResponse> {
    const response = await authClient.post<LoginResponse>('/api/v1/users/login', data);
    AuthManager.saveAuth(response.data);
    return response.data;
}

// 刷新 Token
export async function refreshAccessToken(refreshToken: string): Promise<string> {
    const requestData: RefreshTokenRequest = {refresh_token: refreshToken};
    const response = await authClient.post<TokenResponse>('/api/v1/users/refresh', requestData);
    return response.data.access_token;
}

// 获取当前用户信息
export async function getCurrentUser(): Promise<User> {
    const response = await authClient.get<User>('/api/v1/users/me');
    return response.data;
}

// 用户登出
export async function logout(): Promise<void> {
    try {
        await authClient.post('/api/v1/users/logout');
    } finally {
        AuthManager.clearAuth();
    }
}

// 导出配置好的 axios 实例
export {authClient};