import type {Metadata} from "next";
import {Inter} from "next/font/google";
import "./globals.css";
import React from "react";

const inter = Inter({subsets: ["latin"]});

export const metadata: Metadata = {
    title: "Gen AI Chat",
    description: "A ChatGPT-like frontend",
};

export default function RootLayout({
                                       children,
                                   }: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
        <body className={`${inter.className} bg-gray-100 dark:bg-gray-900`}>
        {children}
        </body>
        </html>
    );
}