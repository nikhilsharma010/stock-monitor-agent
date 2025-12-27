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

    if (error || !data) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <div className="text-red-500 text-xl">Error loading stock data</div>
            </div>
        )
    }

    const quote = data.quote || {}
    const financials = data.financials || {}
    const metrics = data.metrics || {}

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
                    <p className="text-gray-400">{quote.shortName || 'Company Name'}</p>
                </div>
                <div className="text-right">
                    <div className="text-3xl font-bold text-white">
                        ${quote.regularMarketPrice?.toFixed(2) || '0.00'}
                    </div>
                    <div className={`text-lg ${(quote.regularMarketChange || 0) >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {(quote.regularMarketChange || 0) >= 0 ? '+' : ''}
                        {quote.regularMarketChange?.toFixed(2) || '0.00'}
                        ({(quote.regularMarketChangePercent || 0).toFixed(2)}%)
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <StatBox
                    label="Market Cap"
                    value={formatMarketCap(quote.marketCap)}
                    icon={<Building className="h-5 w-5" />}
                />
                <StatBox
                    label="P/E Ratio"
                    value={financials.trailingPE?.toFixed(2) || 'N/A'}
                    icon={<DollarSign className="h-5 w-5" />}
                />
                <StatBox
                    label="52W High"
                    value={`$${quote.fiftyTwoWeekHigh?.toFixed(2) || '0'}`}
                    icon={<TrendingUp className="h-5 w-5" />}
                />
                <StatBox
                    label="52W Low"
                    value={`$${quote.fiftyTwoWeekLow?.toFixed(2) || '0'}`}
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
                            <MetricRow label="Revenue" value={formatLargeNumber(financials.totalRevenue)} />
                            <MetricRow label="Profit Margin" value={`${(financials.profitMargins * 100)?.toFixed(2) || '0'}%`} />
                            <MetricRow label="EPS" value={financials.trailingEps?.toFixed(2) || 'N/A'} />
                            <MetricRow label="Dividend Yield" value={`${(financials.dividendYield * 100)?.toFixed(2) || '0'}%`} />
                            <MetricRow label="Beta" value={financials.beta?.toFixed(2) || 'N/A'} />
                            <MetricRow label="Volume" value={formatLargeNumber(quote.regularMarketVolume)} />
                        </div>
                    </div>

                    {/* Performance Card */}
                    {metrics && (
                        <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
                            <h2 className="text-xl font-semibold text-white mb-4">Performance</h2>
                            <div className="space-y-3">
                                <PerformanceBar label="1 Week" value={metrics['1w'] || 0} />
                                <PerformanceBar label="1 Month" value={metrics['1m'] || 0} />
                                <PerformanceBar label="3 Months" value={metrics['3m'] || 0} />
                                <PerformanceBar label="1 Year" value={metrics['1y'] || 0} />
                            </div>
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
                            <InfoRow label="Sector" value={quote.sector || 'N/A'} />
                            <InfoRow label="Industry" value={quote.industry || 'N/A'} />
                            <InfoRow label="Exchange" value={quote.exchange || 'N/A'} />
                            <InfoRow label="Currency" value={quote.currency || 'USD'} />
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

function formatMarketCap(value: number) {
    if (!value) return 'N/A'
    if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toLocaleString()}`
}

function formatLargeNumber(value: number) {
    if (!value) return 'N/A'
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    return `$${value.toLocaleString()}`
}
