// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
export interface User {
    email: string;
    name: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface RegisterRequest {
    email: string;
    name: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
    expires_in: number;
    user: User;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface RefreshTokenRequest {
    refresh_token: string;
}