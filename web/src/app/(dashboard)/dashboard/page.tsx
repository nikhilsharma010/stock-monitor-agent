import { TrendingUp, TrendingDown, DollarSign, Target } from 'lucide-react'

export default function DashboardPage() {
    // Temporarily removed auth for deployment

    return (
        <div className="space-y-8">
            {/* Welcome Header */}
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                    Welcome back! 👋
                </h1>
                <p className="text-gray-400">
                    Here's your market overview for today
                </p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <StatCard
                    title="Portfolio Value"
                    value="$125,450"
                    change="+2.3%"
                    isPositive={true}
                    icon={<DollarSign className="h-6 w-6" />}
                />
                <StatCard
                    title="Today's P&L"
                    value="+$2,340"
                    change="+1.9%"
                    isPositive={true}
                    icon={<TrendingUp className="h-6 w-6" />}
                />
                <StatCard
                    title="Active Goals"
                    value="2"
                    change="On track"
                    isPositive={true}
                    icon={<Target className="h-6 w-6" />}
                />
                <StatCard
                    title="Watchlist"
                    value="12"
                    change="3 alerts"
                    isPositive={false}
                    icon={<TrendingDown className="h-6 w-6" />}
                />
            </div>

            {/* Watchlist */}
            <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-xl font-semibold text-white">Your Watchlist</h2>
                </div>
                <div className="p-6">
                    <div className="space-y-4">
                        <WatchlistItem ticker="AAPL" name="Apple Inc." price="$182.45" change="+2.3%" isPositive={true} market="🇺🇸" />
                        <WatchlistItem ticker="RELIANCE.NS" name="Reliance Industries" price="₹2,450" change="-1.2%" isPositive={false} market="🇮🇳" />
                        <WatchlistItem ticker="TSLA" name="Tesla Inc." price="$245.67" change="+5.1%" isPositive={true} market="🇺🇸" />
                        <WatchlistItem ticker="TCS.NS" name="Tata Consultancy Services" price="₹3,890" change="+0.8%" isPositive={true} market="🇮🇳" />
                    </div>
                </div>
            </div>

            {/* Goals Progress */}
            <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-xl font-semibold text-white">Financial Goals</h2>
                </div>
                <div className="p-6 space-y-6">
                    <GoalProgress
                        name="Retirement Fund"
                        current={390000}
                        target={500000}
                        percentage={78}
                    />
                    <GoalProgress
                        name="House Down Payment"
                        current={45000}
                        target={100000}
                        percentage={45}
                    />
                </div>
            </div>
        </div>
    )
}

function StatCard({ title, value, change, isPositive, icon }: any) {
    return (
        <div className="border border-slate-800 rounded-xl p-6 bg-slate-900/50 backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
                <span className="text-gray-400 text-sm">{title}</span>
                <div className="text-indigo-500">{icon}</div>
            </div>
            <div className="text-2xl font-bold text-white mb-1">{value}</div>
            <div className={`text-sm ${isPositive ? 'text-green-500' : 'text-amber-500'}`}>
                {change}
            </div>
        </div>
    )
}

function WatchlistItem({ ticker, name, price, change, isPositive, market }: any) {
    return (
        <div className="flex items-center justify-between p-4 rounded-lg hover:bg-slate-800/50 transition cursor-pointer">
            <div className="flex items-center space-x-4">
                <div className="text-2xl">{market}</div>
                <div>
                    <div className="font-semibold text-white">{ticker}</div>
                    <div className="text-sm text-gray-400">{name}</div>
                </div>
            </div>
            <div className="text-right">
                <div className="font-semibold text-white">{price}</div>
                <div className={`text-sm ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {change}
                </div>
            </div>
        </div>
    )
}

function GoalProgress({ name, current, target, percentage }: any) {
    return (
        <div>
            <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">{name}</span>
                <span className="text-gray-400 text-sm">
                    ${current.toLocaleString()} / ${target.toLocaleString()}
                </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-3">
                <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all"
                    style={{ width: `${percentage}%` }}
                />
            </div>
            <div className="text-right text-sm text-gray-400 mt-1">{percentage}%</div>
        </div>
    )
}
