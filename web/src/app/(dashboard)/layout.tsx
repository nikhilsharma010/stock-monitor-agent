import { UserButton } from '@clerk/nextjs'
import Link from 'next/link'
import { BarChart3, Home, TrendingUp, Target, FileText, Bell, Settings } from 'lucide-react'

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="min-h-screen bg-slate-950 flex">
            {/* Sidebar */}
            <aside className="w-64 border-r border-slate-800 bg-slate-900/50 backdrop-blur-sm">
                <div className="p-6">
                    <div className="flex items-center space-x-2 mb-8">
                        <BarChart3 className="h-8 w-8 text-indigo-500" />
                        <span className="text-xl font-bold text-white">Alpha Intelligence</span>
                    </div>

                    <nav className="space-y-2">
                        <NavLink href="/dashboard" icon={<Home className="h-5 w-5" />}>
                            Dashboard
                        </NavLink>
                        <NavLink href="/stocks" icon={<TrendingUp className="h-5 w-5" />}>
                            Stocks
                        </NavLink>
                        <NavLink href="/goals" icon={<Target className="h-5 w-5" />}>
                            Goals
                        </NavLink>
                        <NavLink href="/thesis" icon={<FileText className="h-5 w-5" />}>
                            Thesis
                        </NavLink>
                        <NavLink href="/alerts" icon={<Bell className="h-5 w-5" />}>
                            Alerts
                        </NavLink>
                        <NavLink href="/settings" icon={<Settings className="h-5 w-5" />}>
                            Settings
                        </NavLink>
                    </nav>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col">
                {/* Header */}
                <header className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-sm">
                    <div className="flex items-center justify-between px-8 py-4">
                        <div className="flex-1">
                            {/* Search will go here */}
                        </div>
                        <div className="flex items-center space-x-4">
                            <UserButton afterSignOutUrl="/" />
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <main className="flex-1 overflow-auto p-8">
                    {children}
                </main>
            </div>
        </div>
    )
}

function NavLink({ href, icon, children }: { href: string; icon: React.ReactNode; children: React.ReactNode }) {
    return (
        <Link
            href={href}
            className="flex items-center space-x-3 px-4 py-3 rounded-lg text-gray-400 hover:text-white hover:bg-slate-800/50 transition"
        >
            {icon}
            <span>{children}</span>
        </Link>
    )
}
