'use client'

import { useState } from 'react'
import { Plus, Search, Bell, TrendingUp, TrendingDown, X, Edit } from 'lucide-react'
import Link from 'next/link'

export default function WatchlistPage() {
    const [showAddModal, setShowAddModal] = useState(false)
    const [showAlertModal, setShowAlertModal] = useState(false)
    const [selectedStock, setSelectedStock] = useState<any>(null)

    // Mock watchlist data
    const [watchlist, setWatchlist] = useState([
        {
            ticker: 'AAPL',
            name: 'Apple Inc.',
            price: 273.40,
            change: -0.41,
            percentChange: -0.15,
            market: '🇺🇸',
            alerts: [
                { type: 'above', price: 280, active: true },
                { type: 'below', price: 260, active: true }
            ]
        },
        {
            ticker: 'RELIANCE.NS',
            name: 'Reliance Industries',
            price: 2450,
            change: -30,
            percentChange: -1.2,
            market: '🇮🇳',
            alerts: []
        },
        {
            ticker: 'TSLA',
            name: 'Tesla Inc.',
            price: 245.67,
            change: 12.34,
            percentChange: 5.1,
            market: '🇺🇸',
            alerts: [
                { type: 'above', price: 250, active: true }
            ]
        }
    ])

    const removeStock = (ticker: string) => {
        setWatchlist(watchlist.filter(stock => stock.ticker !== ticker))
    }

    const openAlertModal = (stock: any) => {
        setSelectedStock(stock)
        setShowAlertModal(true)
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Watchlist</h1>
                    <p className="text-gray-400">
                        Track your favorite stocks and set price alerts
                    </p>
                </div>
                <button
                    onClick={() => setShowAddModal(true)}
                    className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                >
                    <Plus className="h-5 w-5" />
                    <span>Add Stock</span>
                </button>
            </div>

            {/* Watchlist Table */}
            <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="border-b border-slate-800">
                            <tr className="text-left">
                                <th className="px-6 py-4 text-sm font-semibold text-gray-400">Stock</th>
                                <th className="px-6 py-4 text-sm font-semibold text-gray-400">Price</th>
                                <th className="px-6 py-4 text-sm font-semibold text-gray-400">Change</th>
                                <th className="px-6 py-4 text-sm font-semibold text-gray-400">Alerts</th>
                                <th className="px-6 py-4 text-sm font-semibold text-gray-400">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {watchlist.map((stock) => (
                                <tr key={stock.ticker} className="border-b border-slate-800 hover:bg-slate-800/30 transition">
                                    <td className="px-6 py-4">
                                        <Link href={`/stocks/${stock.ticker}`} className="flex items-center space-x-3 hover:text-indigo-400 transition">
                                            <span className="text-2xl">{stock.market}</span>
                                            <div>
                                                <div className="font-semibold text-white">{stock.ticker}</div>
                                                <div className="text-sm text-gray-400">{stock.name}</div>
                                            </div>
                                        </Link>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="font-semibold text-white">
                                            {stock.market === '🇮🇳' ? '₹' : '$'}{stock.price.toLocaleString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className={`flex items-center space-x-1 ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                                            {stock.change >= 0 ? <TrendingUp className="h-4 w-4" /> : <TrendingDown className="h-4 w-4" />}
                                            <span className="font-semibold">
                                                {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)} ({stock.percentChange.toFixed(2)}%)
                                            </span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        {stock.alerts.length > 0 ? (
                                            <div className="flex items-center space-x-2">
                                                <Bell className="h-4 w-4 text-indigo-500" />
                                                <span className="text-sm text-gray-400">{stock.alerts.length} active</span>
                                            </div>
                                        ) : (
                                            <span className="text-sm text-gray-500">No alerts</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-2">
                                            <button
                                                onClick={() => openAlertModal(stock)}
                                                className="p-2 hover:bg-slate-700 rounded-lg transition"
                                                title="Set Alert"
                                            >
                                                <Bell className="h-4 w-4 text-gray-400" />
                                            </button>
                                            <button
                                                onClick={() => removeStock(stock.ticker)}
                                                className="p-2 hover:bg-slate-700 rounded-lg transition"
                                                title="Remove"
                                            >
                                                <X className="h-4 w-4 text-gray-400" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Empty State */}
            {watchlist.length === 0 && (
                <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-12 text-center">
                    <Search className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No stocks in watchlist</h3>
                    <p className="text-gray-400 mb-6">
                        Add stocks to your watchlist to track them easily
                    </p>
                    <button
                        onClick={() => setShowAddModal(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                        Add Your First Stock
                    </button>
                </div>
            )}

            {/* Add Stock Modal */}
            {showAddModal && (
                <AddStockModal onClose={() => setShowAddModal(false)} />
            )}

            {/* Alert Modal */}
            {showAlertModal && selectedStock && (
                <AlertModal stock={selectedStock} onClose={() => setShowAlertModal(false)} />
            )}
        </div>
    )
}

function AddStockModal({ onClose }: { onClose: () => void }) {
    const [ticker, setTicker] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        console.log('Adding stock:', ticker)
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md w-full mx-4">
                <h2 className="text-2xl font-bold text-white mb-6">Add Stock to Watchlist</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Stock Ticker
                        </label>
                        <input
                            type="text"
                            value={ticker}
                            onChange={(e) => setTicker(e.target.value.toUpperCase())}
                            placeholder="e.g., AAPL, RELIANCE.NS, TSLA"
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                            required
                        />
                        <p className="text-sm text-gray-500 mt-2">
                            For Indian stocks, add .NS (NSE) or .BO (BSE) suffix
                        </p>
                    </div>

                    <div className="flex space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-3 border border-slate-700 hover:border-slate-600 text-white rounded-lg font-semibold transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
                        >
                            Add to Watchlist
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

function AlertModal({ stock, onClose }: { stock: any; onClose: () => void }) {
    const [alertType, setAlertType] = useState<'above' | 'below'>('above')
    const [targetPrice, setTargetPrice] = useState('')

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        console.log('Creating alert:', { ticker: stock.ticker, type: alertType, price: targetPrice })
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md w-full mx-4">
                <h2 className="text-2xl font-bold text-white mb-2">Set Price Alert</h2>
                <p className="text-gray-400 mb-6">{stock.ticker} - Current: ${stock.price}</p>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Alert Type
                        </label>
                        <div className="grid grid-cols-2 gap-3">
                            <button
                                type="button"
                                onClick={() => setAlertType('above')}
                                className={`px-4 py-3 rounded-lg font-semibold transition ${alertType === 'above'
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-slate-800 text-gray-400 hover:bg-slate-700'
                                    }`}
                            >
                                Price Above
                            </button>
                            <button
                                type="button"
                                onClick={() => setAlertType('below')}
                                className={`px-4 py-3 rounded-lg font-semibold transition ${alertType === 'below'
                                        ? 'bg-indigo-600 text-white'
                                        : 'bg-slate-800 text-gray-400 hover:bg-slate-700'
                                    }`}
                            >
                                Price Below
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Target Price
                        </label>
                        <input
                            type="number"
                            step="0.01"
                            value={targetPrice}
                            onChange={(e) => setTargetPrice(e.target.value)}
                            placeholder={alertType === 'above' ? '280.00' : '260.00'}
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                            required
                        />
                    </div>

                    {/* Existing Alerts */}
                    {stock.alerts.length > 0 && (
                        <div className="pt-4 border-t border-slate-800">
                            <h3 className="text-sm font-semibold text-gray-400 mb-3">Active Alerts</h3>
                            <div className="space-y-2">
                                {stock.alerts.map((alert: any, i: number) => (
                                    <div key={i} className="flex items-center justify-between p-3 bg-slate-800 rounded-lg">
                                        <span className="text-sm text-white">
                                            {alert.type === 'above' ? '↑' : '↓'} ${alert.price}
                                        </span>
                                        <button className="text-red-500 hover:text-red-400">
                                            <X className="h-4 w-4" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="flex space-x-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-3 border border-slate-700 hover:border-slate-600 text-white rounded-lg font-semibold transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="flex-1 px-4 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
                        >
                            Create Alert
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
