'use client'

import { useState } from 'react'
import { Plus, FileText, TrendingUp, Lightbulb, AlertTriangle, Edit, Trash2, BarChart3 } from 'lucide-react'

export default function ThesisPage() {
    const [showCreateModal, setShowCreateModal] = useState(false)

    // Mock thesis data
    const theses = [
        {
            id: 1,
            name: 'AI Infrastructure Play',
            coreBelief: 'AI infrastructure will see explosive growth over the next 5 years. Companies providing chips, cloud compute, and data centers will benefit most.',
            catalysts: [
                'ChatGPT adoption accelerating',
                'Enterprise AI spending up 40% YoY',
                'Data center demand surging'
            ],
            risks: [
                'Chip supply constraints',
                'Regulatory crackdown on AI',
                'Market saturation'
            ],
            stocks: [
                { ticker: 'NVDA', allocation: 40, reason: 'Chipmaker - Leader' },
                { ticker: 'AMD', allocation: 20, reason: 'Chipmaker - Challenger' },
                { ticker: 'MSFT', allocation: 20, reason: 'Cloud + AI Platform' },
                { ticker: 'GOOGL', allocation: 15, reason: 'AI Research + Cloud' },
                { ticker: 'TSLA', allocation: 5, reason: 'AI Compute for Autonomy' }
            ],
            performance: 42.3,
            vsMarket: 15.2,
            createdAt: '2024-01-15'
        }
    ]

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Investment Theses</h1>
                    <p className="text-gray-400">
                        Build and track your investment ideas with AI-powered insights
                    </p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                >
                    <Plus className="h-5 w-5" />
                    <span>New Thesis</span>
                </button>
            </div>

            {/* Theses Grid */}
            <div className="grid grid-cols-1 gap-6">
                {theses.map((thesis) => (
                    <ThesisCard key={thesis.id} thesis={thesis} />
                ))}
            </div>

            {/* Empty State */}
            {theses.length === 0 && (
                <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-12 text-center">
                    <FileText className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No theses yet</h3>
                    <p className="text-gray-400 mb-6">
                        Create your first investment thesis to track your ideas
                    </p>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                        Create Your First Thesis
                    </button>
                </div>
            )}

            {/* Create Thesis Modal */}
            {showCreateModal && (
                <CreateThesisModal onClose={() => setShowCreateModal(false)} />
            )}
        </div>
    )
}

function ThesisCard({ thesis }: any) {
    const totalAllocation = thesis.stocks.reduce((sum: number, stock: any) => sum + stock.allocation, 0)

    return (
        <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
            {/* Header */}
            <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-3">
                    <div className="p-3 bg-purple-600/20 rounded-lg">
                        <FileText className="h-6 w-6 text-purple-500" />
                    </div>
                    <div>
                        <h3 className="text-xl font-semibold text-white">{thesis.name}</h3>
                        <p className="text-sm text-gray-400">Created {new Date(thesis.createdAt).toLocaleDateString()}</p>
                    </div>
                </div>
                <div className="flex items-center space-x-2">
                    <button className="p-2 hover:bg-slate-800 rounded-lg transition">
                        <Edit className="h-5 w-5 text-gray-400" />
                    </button>
                    <button className="p-2 hover:bg-slate-800 rounded-lg transition">
                        <Trash2 className="h-5 w-5 text-gray-400" />
                    </button>
                </div>
            </div>

            {/* Core Belief */}
            <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-2">Core Belief</h4>
                <p className="text-white">{thesis.coreBelief}</p>
            </div>

            {/* Catalysts & Risks */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                        <Lightbulb className="h-4 w-4 text-green-500" />
                        <span>Key Catalysts</span>
                    </h4>
                    <ul className="space-y-2">
                        {thesis.catalysts.map((catalyst: string, i: number) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start space-x-2">
                                <span className="text-green-500">•</span>
                                <span>{catalyst}</span>
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h4 className="text-sm font-semibold text-gray-400 mb-3 flex items-center space-x-2">
                        <AlertTriangle className="h-4 w-4 text-amber-500" />
                        <span>Risks to Thesis</span>
                    </h4>
                    <ul className="space-y-2">
                        {thesis.risks.map((risk: string, i: number) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start space-x-2">
                                <span className="text-amber-500">•</span>
                                <span>{risk}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* Stock Basket */}
            <div className="mb-6">
                <h4 className="text-sm font-semibold text-gray-400 mb-3">Stock Basket ({thesis.stocks.length} stocks)</h4>
                <div className="space-y-2">
                    {thesis.stocks.map((stock: any, i: number) => (
                        <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                            <div className="flex items-center space-x-3">
                                <span className="font-semibold text-white">{stock.ticker}</span>
                                <span className="text-sm text-gray-400">{stock.reason}</span>
                            </div>
                            <div className="flex items-center space-x-4">
                                <div className="w-32 bg-slate-700 rounded-full h-2">
                                    <div
                                        className="bg-indigo-500 h-2 rounded-full"
                                        style={{ width: `${stock.allocation}%` }}
                                    />
                                </div>
                                <span className="text-sm font-semibold text-white w-12 text-right">{stock.allocation}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Performance */}
            <div className="border-t border-slate-800 pt-6">
                <div className="grid grid-cols-3 gap-4">
                    <div>
                        <div className="text-sm text-gray-400 mb-1">Thesis Return</div>
                        <div className="text-2xl font-bold text-green-500">+{thesis.performance}%</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-400 mb-1">vs S&P 500</div>
                        <div className="text-2xl font-bold text-green-500">+{thesis.vsMarket}%</div>
                    </div>
                    <div>
                        <div className="text-sm text-gray-400 mb-1">Status</div>
                        <div className="text-sm font-semibold text-green-500">Outperforming</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

function CreateThesisModal({ onClose }: { onClose: () => void }) {
    const [formData, setFormData] = useState({
        name: '',
        coreBelief: '',
        catalysts: [''],
        risks: [''],
        stocks: [{ ticker: '', allocation: '', reason: '' }]
    })

    const addCatalyst = () => {
        setFormData({ ...formData, catalysts: [...formData.catalysts, ''] })
    }

    const addRisk = () => {
        setFormData({ ...formData, risks: [...formData.risks, ''] })
    }

    const addStock = () => {
        setFormData({ ...formData, stocks: [...formData.stocks, { ticker: '', allocation: '', reason: '' }] })
    }

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        console.log('Creating thesis:', formData)
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 overflow-y-auto">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-2xl w-full mx-4 my-8">
                <h2 className="text-2xl font-bold text-white mb-6">Create Investment Thesis</h2>

                <form onSubmit={handleSubmit} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Thesis Name
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="e.g., AI Infrastructure Play"
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Core Belief
                        </label>
                        <textarea
                            value={formData.coreBelief}
                            onChange={(e) => setFormData({ ...formData, coreBelief: e.target.value })}
                            placeholder="Describe your investment thesis..."
                            rows={3}
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                            required
                        />
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
                            Create Thesis
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
