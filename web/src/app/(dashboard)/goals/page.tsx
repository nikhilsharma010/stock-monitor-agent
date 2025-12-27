'use client'

import { useState } from 'react'
import { Plus, Target, TrendingUp, Calendar, DollarSign, Edit, Trash2 } from 'lucide-react'

export default function GoalsPage() {
    const [showCreateModal, setShowCreateModal] = useState(false)

    // Mock goals data - will be replaced with API calls
    const goals = [
        {
            id: 1,
            name: 'Retirement Fund',
            targetAmount: 500000,
            currentAmount: 390000,
            targetDate: '2040-12-31',
            monthlyContribution: 1500,
            category: 'Retirement'
        },
        {
            id: 2,
            name: 'House Down Payment',
            targetAmount: 100000,
            currentAmount: 45000,
            targetDate: '2026-12-31',
            monthlyContribution: 2200,
            category: 'Real Estate'
        }
    ]

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Financial Goals</h1>
                    <p className="text-gray-400">
                        Track your progress toward your financial milestones
                    </p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                >
                    <Plus className="h-5 w-5" />
                    <span>New Goal</span>
                </button>
            </div>

            {/* Goals Grid */}
            <div className="grid grid-cols-1 gap-6">
                {goals.map((goal) => (
                    <GoalCard key={goal.id} goal={goal} />
                ))}
            </div>

            {/* Empty State */}
            {goals.length === 0 && (
                <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-12 text-center">
                    <Target className="h-16 w-16 text-gray-600 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-white mb-2">No goals yet</h3>
                    <p className="text-gray-400 mb-6">
                        Create your first financial goal to start tracking your progress
                    </p>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-semibold transition"
                    >
                        Create Your First Goal
                    </button>
                </div>
            )}

            {/* Create Goal Modal */}
            {showCreateModal && (
                <CreateGoalModal onClose={() => setShowCreateModal(false)} />
            )}
        </div>
    )
}

function GoalCard({ goal }: any) {
    const percentage = Math.round((goal.currentAmount / goal.targetAmount) * 100)
    const remaining = goal.targetAmount - goal.currentAmount
    const monthsRemaining = Math.ceil(
        (new Date(goal.targetDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24 * 30)
    )
    const requiredMonthly = remaining / monthsRemaining
    const onTrack = goal.monthlyContribution >= requiredMonthly

    return (
        <div className="border border-slate-800 rounded-xl bg-slate-900/50 backdrop-blur-sm p-6">
            <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-3">
                    <div className="p-3 bg-indigo-600/20 rounded-lg">
                        <Target className="h-6 w-6 text-indigo-500" />
                    </div>
                    <div>
                        <h3 className="text-xl font-semibold text-white">{goal.name}</h3>
                        <p className="text-sm text-gray-400">{goal.category}</p>
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

            {/* Progress Bar */}
            <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400 text-sm">Progress</span>
                    <span className="text-white font-semibold">
                        ${goal.currentAmount.toLocaleString()} / ${goal.targetAmount.toLocaleString()}
                    </span>
                </div>
                <div className="w-full bg-slate-800 rounded-full h-4">
                    <div
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 h-4 rounded-full transition-all flex items-center justify-end pr-2"
                        style={{ width: `${percentage}%` }}
                    >
                        <span className="text-xs font-bold text-white">{percentage}%</span>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
                <StatItem
                    icon={<DollarSign className="h-4 w-4" />}
                    label="Monthly"
                    value={`$${goal.monthlyContribution.toLocaleString()}`}
                />
                <StatItem
                    icon={<Calendar className="h-4 w-4" />}
                    label="Target Date"
                    value={new Date(goal.targetDate).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                />
                <StatItem
                    icon={<TrendingUp className="h-4 w-4" />}
                    label="Status"
                    value={onTrack ? 'On Track' : 'Behind'}
                    valueColor={onTrack ? 'text-green-500' : 'text-amber-500'}
                />
            </div>

            {/* Recommendation */}
            {!onTrack && (
                <div className="mt-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg">
                    <p className="text-sm text-amber-500">
                        💡 Increase monthly contribution to ${Math.ceil(requiredMonthly).toLocaleString()} to stay on track
                    </p>
                </div>
            )}
        </div>
    )
}

function StatItem({ icon, label, value, valueColor = 'text-white' }: any) {
    return (
        <div className="flex items-center space-x-2">
            <div className="text-indigo-500">{icon}</div>
            <div>
                <div className="text-xs text-gray-400">{label}</div>
                <div className={`text-sm font-semibold ${valueColor}`}>{value}</div>
            </div>
        </div>
    )
}

function CreateGoalModal({ onClose }: { onClose: () => void }) {
    const [formData, setFormData] = useState({
        name: '',
        targetAmount: '',
        currentAmount: '',
        targetDate: '',
        monthlyContribution: '',
        category: 'Retirement'
    })

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault()
        // TODO: API call to create goal
        console.log('Creating goal:', formData)
        onClose()
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 max-w-md w-full mx-4">
                <h2 className="text-2xl font-bold text-white mb-6">Create New Goal</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Goal Name
                        </label>
                        <input
                            type="text"
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            placeholder="e.g., Retirement Fund"
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">
                            Category
                        </label>
                        <select
                            value={formData.category}
                            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                        >
                            <option>Retirement</option>
                            <option>Real Estate</option>
                            <option>Education</option>
                            <option>Emergency Fund</option>
                            <option>Investment</option>
                            <option>Other</option>
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Target Amount
                            </label>
                            <input
                                type="number"
                                value={formData.targetAmount}
                                onChange={(e) => setFormData({ ...formData, targetAmount: e.target.value })}
                                placeholder="500000"
                                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Current Amount
                            </label>
                            <input
                                type="number"
                                value={formData.currentAmount}
                                onChange={(e) => setFormData({ ...formData, currentAmount: e.target.value })}
                                placeholder="50000"
                                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                                required
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Target Date
                            </label>
                            <input
                                type="date"
                                value={formData.targetDate}
                                onChange={(e) => setFormData({ ...formData, targetDate: e.target.value })}
                                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">
                                Monthly Contribution
                            </label>
                            <input
                                type="number"
                                value={formData.monthlyContribution}
                                onChange={(e) => setFormData({ ...formData, monthlyContribution: e.target.value })}
                                placeholder="1500"
                                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-indigo-500"
                                required
                            />
                        </div>
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
                            Create Goal
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
