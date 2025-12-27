import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

export async function getStockAnalysis(ticker: string) {
    const response = await api.get(`/api/stocks/${ticker}`)
    return response.data
}

export async function getStockChart(ticker: string) {
    const response = await api.get(`/api/stocks/${ticker}/chart`)
    return response.data
}
