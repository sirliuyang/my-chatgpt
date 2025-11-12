// @Home    : www.pi-apple.com
// @Author  : Leon
// @Email   : newyoung9@gmail.com
import type {Metadata} from 'next';
import './globals.css';
import React from "react";

export const metadata: Metadata = {
    title: 'Leon ChatGPT',
    description: 'A ChatGPT-like interface built with Next.js 16 and React 19',
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en" suppressHydrationWarning>
        <body className="antialiased">{children}</body>
        </html>
    );
}