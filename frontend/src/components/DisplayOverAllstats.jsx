import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import { AlertTriangle, CheckCircle, Loader2, MessageCircle, XCircle } from 'lucide-react';

const DisplayOverAllStats = () => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Token configuration
    const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzQzMjExfQ.ZErCL4neknZ-f4YcVwnrKU5VlFX_vVEHdVlVzuNASj8";

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:5000/stats/aggregate', {
                    headers: {
                        'Authorization': `Bearer ${TOKEN}`,
                        'Content-Type': 'application/json'
                    }
                });
                setStats(response.data.stats);
                setLoading(false);
            } catch (err) {
                console.error('Error fetching stats:', err);
                setError(err.response?.data?.message || 'Failed to fetch statistics');
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) return <div className="p-4">Loading statistics...</div>;
    if (error) return <Alert variant="destructive"><AlertTitle>Error</AlertTitle><AlertDescription>{error}</AlertDescription></Alert>;
    if (!stats) return null;

    const isDangerous = stats.overall_failure_rate > 12;
    const isHealthy = stats.overall_success_rate > 50;

    // Data for the pie chart
    const pieData = [
        { name: 'Success', value: stats.overall_success_rate },
        { name: 'Failure', value: stats.overall_failure_rate }
    ];

    return (
        <div className={`p-6 rounded-lg ${isDangerous ? 'bg-red-50' : isHealthy ? 'bg-green-50' : 'bg-gray-50'}`}>
            {/* Status Alert */}
            <Alert className={` flex justify-between mb-6 ${isDangerous ? 'bg-red-100 text-red-900' : 'bg-green-100 text-green-900'}`}>
                <div><AlertTriangle className={isDangerous ? 'text-red-600' : 'hidden'} />
                    <CheckCircle className={!isDangerous ? 'text-green-600' : 'hidden'} />
                    <AlertTitle className="text-lg font-semibold">
                        {isDangerous ? 'High Failure Rate Detected' : 'System Operating Normally'}
                    </AlertTitle>
                    <AlertDescription>
                        {isDangerous
                            ? 'Current failure rate exceeds acceptable threshold of 12%'
                            : 'All metrics within acceptable ranges'}
                    </AlertDescription></div>

                <div className='flex justify-center items-center text-lg'>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />

                    <span className='font-bold'>Live</span>
                </div>
            </Alert>
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 mb-6">
                {/* Success Rate Card */}
                <Card className={`${isHealthy ? 'border-green-500' : 'border-red-500'} border-2`}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                        <CheckCircle className={`w-4 h-4 ${isHealthy ? 'text-green-500' : 'text-red-500'}`} />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.overall_success_rate.toFixed(2)}%</div>
                    </CardContent>
                </Card>

                {/* Failure Rate Card */}
                <Card className={`${isDangerous ? 'border-red-500' : 'border-green-500'} border-2`}>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Failure Rate</CardTitle>
                        <XCircle className={`w-4 h-4 ${isDangerous ? 'text-red-500' : 'text-green-500'}`} />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.overall_failure_rate.toFixed(2)}%</div>
                    </CardContent>
                </Card>
                {/* Total Messages Card */}
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between pb-2">
                        <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
                        <MessageCircle className="w-4 h-4 text-blue-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_sms_sent.toLocaleString()}</div>
                        <p className="text-xs text-gray-500 mt-1">
                            Failed: {stats.total_sms_failed.toLocaleString()}
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Pie Chart */}
            {/* <Card className="w-full">
                <CardHeader>
                    <CardTitle>Success vs Failure Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={5}
                                dataKey="value"
                            >
                                <Cell fill={isHealthy ? "#22c55e" : "#ef4444"} />
                                <Cell fill={isDangerous ? "#ef4444" : "#22c55e"} />
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card> */}
        </div>
    );
};

export default DisplayOverAllStats;