'use client'

import { useState } from 'react'
import { Search } from 'lucide-react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'

export default function StocksPage() {
    const [searchTicker, setSearchTicker] = useState('')
    const router = useRouter()

    const handleAnalyze = () => {
        if (searchTicker.trim()) {
            router.push(`/stocks/${searchTicker.trim()}`)
        }
    }

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleAnalyze()
        }
    }

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">Stock Analysis</h1>
                <p className="text-gray-400">
                    Search and analyze stocks from US and Indian markets
                </p>
            </div>

            {/* Search Bar */}
            <div className="border border-slate-800 rounded-xl p-6 bg-slate-900/50 backdrop-blur-sm">
                <div className="flex items-center space-x-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search stocks (e.g., AAPL, RELIANCE, TCS)"
                            value={searchTicker}
                            onChange={(e) => setSearchTicker(e.target.value.toUpperCase())}
                            onKeyPress={handleKeyPress}
                            className="w-full pl-12 pr-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                        />
                    </div>
                    <button
                        onClick={handleAnalyze}
                        className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
                    >
                        Analyze
                    </button>
                </div>
            </div>

            {/* Popular Stocks */}
            <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm">
                <div className="p-6 border-b border-slate-800">
                    <h2 className="text-xl font-semibold text-white">Popular Stocks</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
                    <StockCard ticker="AAPL" name="Apple Inc." market="🇺🇸" />
                    <StockCard ticker="RELIANCE.NS" name="Reliance Industries" market="🇮🇳" />
                    <StockCard ticker="TSLA" name="Tesla Inc." market="🇺🇸" />
                    <StockCard ticker="TCS.NS" name="Tata Consultancy" market="🇮🇳" />
                    <StockCard ticker="NVDA" name="NVIDIA Corp." market="🇺🇸" />
                    <StockCard ticker="INFY.NS" name="Infosys Ltd." market="🇮🇳" />
                </div>
            </div>
        </div>
    )
}

function StockCard({ ticker, name, market }: { ticker: string; name: string; market: string }) {
    return (
        <Link href={`/stocks/${ticker}`}>
            <div className="border border-slate-800 rounded-lg p-4 hover:border-slate-700 hover:bg-slate-800/50 transition cursor-pointer">
                <div className="flex items-center justify-between mb-2">
                    <div className="text-2xl">{market}</div>
                    <span className="text-indigo-500 hover:text-indigo-400 text-sm">
                        Analyze →
                    </span>
                </div>
                <div className="font-semibold text-white">{ticker}</div>
                <div className="text-sm text-gray-400">{name}</div>
            </div>
        </Link>
    )
}
