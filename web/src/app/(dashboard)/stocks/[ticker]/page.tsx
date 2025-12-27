'use client'

import { useParams } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { getStockAnalysis } from '@/lib/api'
import { ArrowLeft, TrendingUp, TrendingDown, DollarSign, Users, Building } from 'lucide-react'
import Link from 'next/link'

export default function StockDetailPage() {
    const params = useParams()
    const ticker = params.ticker as string

    const { data, isLoading, error } = useQuery({
        queryKey: ['stock', ticker],
        queryFn: () => getStockAnalysis(ticker),
    })

    if (isLoading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-white text-xl">Loading {ticker}...</div>
            </div>
        )
    }

    if (error || !data || data.error) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <div className="text-red-500 text-xl mb-2">Error loading stock data</div>
                    <div className="text-gray-400">{data?.error || 'Unknown error'}</div>
                </div>
            </div>
        )
    }

    const quote = data.quote || {}
    const financials = data.financials || {}
    const metrics = data.metrics || {}
    const profile = data.profile || {}

    const price = quote.current_price || 0
    const change = quote.change || 0
    const percentChange = quote.percent_change || 0

    return (
        <div className="space-y-8">
            {/* Back Button */}
            <Link href="/stocks" className="flex items-center space-x-2 text-gray-400 hover:text-white transition">
                <ArrowLeft className="h-5 w-5" />
                <span>Back to Stocks</span>
            </Link>

            {/* Stock Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-4xl font-bold text-white mb-2">{ticker}</h1>
                    <p className="text-gray-400">{profile.name || 'Company Name'}</p>
                </div>
                <div className="text-right">
                    <div className="text-3xl font-bold text-white">
                        ${price.toFixed(2)}
                    </div>
                    <div className={`text-lg ${change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {change >= 0 ? '+' : ''}{change.toFixed(2)} ({percentChange.toFixed(2)}%)
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatBox
                    label="Market Cap"
                    value={financials.market_cap || 'N/A'}
                    icon={<Building className="h-5 w-5" />}
                />
                <StatBox
                    label="P/E Ratio"
                    value={financials.pe_ratio || 'N/A'}
                    icon={<DollarSign className="h-5 w-5" />}
                />
                <StatBox
                    label="52W High"
                    value={financials['52_week_high'] ? `$${financials['52_week_high']}` : 'N/A'}
                    icon={<TrendingUp className="h-5 w-5" />}
                />
                <StatBox
                    label="52W Low"
                    value={financials['52_week_low'] ? `$${financials['52_week_low']}` : 'N/A'}
                    icon={<TrendingDown className="h-5 w-5" />}
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column - Financials */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Financials Card */}
                    <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Key Metrics</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <MetricRow label="Beta" value={financials.beta || 'N/A'} />
                            <MetricRow label="P/S Ratio" value={financials.ps_ratio || 'N/A'} />
                            <MetricRow label="Net Margin" value={financials.net_margin ? `${financials.net_margin}%` : 'N/A'} />
                            <MetricRow label="Operating Margin" value={financials.operating_margin ? `${financials.operating_margin}%` : 'N/A'} />
                            <MetricRow label="Revenue Growth" value={financials.revenue_growth ? `${financials.revenue_growth}%` : 'N/A'} />
                            <MetricRow label="EPS Growth" value={financials.eps_growth ? `${financials.eps_growth}%` : 'N/A'} />
                        </div>
                    </div>

                    {/* Performance Card */}
                    {metrics && (
                        <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Performance</h2>
                            <div className="space-y-3">
                                {metrics['5d_pct'] !== undefined && (
                                    <PerformanceBar label="5 Days" value={metrics['5d_pct']} />
                                )}
                                {metrics['1m_pct'] !== undefined && (
                                    <PerformanceBar label="1 Month" value={metrics['1m_pct']} />
                                )}
                            </div>
                        </div>
                    )}

                    {/* Company Description */}
                    {profile.description && (
                        <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">About</h2>
                            <p className="text-gray-400 text-sm leading-relaxed">
                                {profile.description.slice(0, 500)}...
                            </p>
                        </div>
                    )}
                </div>

                {/* Right Column - Actions */}
                <div className="space-y-6">
                    <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Actions</h2>
                        <div className="space-y-3">
                            <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-semibold transition">
                                Add to Watchlist
                            </button>
                            <button className="w-full border border-slate-700 hover:border-slate-600 text-white py-3 rounded-lg font-semibold transition">
                                Set Alert
                            </button>
                            <button className="w-full border border-slate-700 hover:border-slate-600 text-white py-3 rounded-lg font-semibold transition">
                                Add to Goal
                            </button>
                        </div>
                    </div>

                    {/* Company Info */}
                    <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                        <h2 className="text-xl font-semibold text-white mb-4">Company Info</h2>
                        <div className="space-y-2 text-sm">
                            <InfoRow label="Sector" value={profile.sector || 'N/A'} />
                            <InfoRow label="Industry" value={profile.finnhubIndustry || 'N/A'} />
                            {profile.website && (
                                <div className="pt-2">
                                    <a href={profile.website} target="_blank" rel="noopener noreferrer" className="text-indigo-500 hover:text-indigo-400">
                                        Visit Website →
                                    </a>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function StatBox({ label, value, icon }: any) {
    return (
        <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/50">
            <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">{label}</span>
                <div className="text-indigo-500">{icon}</div>
            </div>
            <div className="text-xl font-bold text-white">{value}</div>
        </div>
    )
}

function MetricRow({ label, value }: any) {
    return (
        <div className="flex justify-between py-2 border-b border-slate-800">
            <span className="text-gray-400">{label}</span>
            <span className="text-white font-semibold">{value}</span>
        </div>
    )
}

function PerformanceBar({ label, value }: any) {
    const isPositive = value >= 0
    const percentage = Math.min(Math.abs(value), 100)

    return (
        <div>
            <div className="flex justify-between mb-1">
                <span className="text-gray-400 text-sm">{label}</span>
                <span className={`text-sm font-semibold ${isPositive ? 'text-green-500' : 'text-red-500'}`}>
                    {isPositive ? '+' : ''}{value.toFixed(2)}%
                </span>
            </div>
            <div className="w-full bg-slate-800 rounded-full h-2">
                <div
                    className={`h-2 rounded-full ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    )
}

function InfoRow({ label, value }: any) {
    return (
        <div className="flex justify-between">
            <span className="text-gray-400">{label}:</span>
            <span className="text-white">{value}</span>
        </div>
    )
}
