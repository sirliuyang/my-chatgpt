// components/ProtectedRoute.tsx
'use client';

import React, {useEffect, useState} from 'react';
import {useRouter} from 'next/navigation';
import {AuthManager} from '@/lib/auth';

interface ProtectedRouteProps {
    children: React.ReactNode;
}

export default function ProtectedRoute({children}: ProtectedRouteProps) {
    const router = useRouter();
    const [isChecking, setIsChecking] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const checkAuth = () => {
            const authenticated = AuthManager.isAuthenticated();

            if (!authenticated) {
                // 未登录,重定向到登录页
                router.replace('/login');
            } else {
                setIsAuthenticated(true);
            }

            setIsChecking(false);
        };

        checkAuth();
    }, [router]);

    // 正在检查认证状态
    if (isChecking) {
        return (
            <div className="flex items-center justify-center h-screen bg-white dark:bg-gray-900">
                <div className="text-center">
                    <div className="size-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"/>
                    <p className="text-gray-600 dark:text-gray-400">Loading...</p>
                </div>
            </div>
        );
    }

    // 未认证,不渲染内容(因为会重定向)
    if (!isAuthenticated) {
        return null;
    }

    // 已认证,渲染子组件
    return <>{children}</>;
}