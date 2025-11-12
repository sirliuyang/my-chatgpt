// components/UserMenu.tsx
'use client';

import {useState, useEffect, useRef} from 'react';
import {useRouter} from 'next/navigation';
import {AuthManager, logout} from '@/lib/auth';
import type {User} from '@/lib/types/auth';

export default function UserMenu() {
    const router = useRouter();
    const [user, setUser] = useState<User | null>(null);
    const [isOpen, setIsOpen] = useState(false);
    const menuRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // 获取用户信息
        const currentUser = AuthManager.getUser();
        setUser(currentUser);
    }, []);

    useEffect(() => {
        // 点击外部关闭菜单
        const handleClickOutside = (event: MouseEvent) => {
            if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleLogout = async () => {
        try {
            await logout();
        } catch (error) {
            console.error('Logout error:', error);
            // 即使失败也清除本地认证信息
            AuthManager.clearAuth();
        } finally {
            router.push('/login');
        }
    };

    if (!user) return null;

    return (
        <div ref={menuRef} className="relative">
            {/* User Avatar Button */}
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-gray-800 transition-colors"
            >
                <div className="size-7 rounded-sm bg-blue-600 flex items-center justify-center text-white text-sm font-semibold">
                    {user.name.charAt(0).toUpperCase()}
                </div>
                <svg
                    className={`size-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7"/>
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-gray-800 rounded-lg shadow-lg border border-gray-700 py-1 z-50">
                    {/* User Info */}
                    <div className="px-4 py-3 border-b border-gray-700">
                        <p className="text-sm font-medium text-white truncate">
                            {user.name}
                        </p>
                        <p className="text-xs text-gray-400 truncate mt-1">
                            {user.email}
                        </p>
                    </div>

                    {/* Menu Items */}
                    <div className="py-1">
                        <button
                            type="button"
                            onClick={handleLogout}
                            className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-gray-700 transition-colors flex items-center gap-3"
                        >
                            <svg className="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                                />
                            </svg>
                            <span>Log out</span>
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}