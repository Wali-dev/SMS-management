import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "./ui/card";
import { Button } from "./ui/button";
import { CheckCircle, XCircle, MessageCircle, Trash2, Edit } from "lucide-react";
import { Loader2 } from "lucide-react";
import axios from "axios";
import { useEffect, useState } from "react";

const DisplaySelectedStats = () => {
    const [stats, setStats] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isHealthy, setIsHealthy] = useState(false);
    const [isDangerous, setIsDangerous] = useState(false);
    const pair_id = "67222e5c875809f5ea383eec";
    const pairName = "test_pair_2";

    useEffect(() => {
        const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzQzMjExfQ.ZErCL4neknZ-f4YcVwnrKU5VlFX_vVEHdVlVzuNASj8";
        axios
            .get(`http://127.0.0.1:5000/stats/${pairName}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
            .then((response) => {
                setStats(response.data.stats);
                setIsHealthy(response.data.stats.total_rate_of_success > 90);
                setIsDangerous(response.data.stats.total_rate_of_failure > 10);
                setIsLoading(false);
            })
            .catch((error) => {
                console.error("Error fetching stats:", error);
                setIsLoading(false);
            });
    }, [pair_id, pairName]);

    const handleDelete = () => {
        const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzQzMjExfQ.ZErCL4neknZ-f4YcVwnrKU5VlFX_vVEHdVlVzuNASj8";
        axios
            .delete(`http://127.0.0.1:5000/stats/${pairName}`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
            .then((response) => {
                console.log("Stats deleted successfully");
                setStats(null);
            })
            .catch((error) => {
                console.error("Error deleting stats:", error);
            });
    };

    const handleUpdate = () => {
        const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzQzMjExfQ.ZErCL4neknZ-f4YcVwnrKU5VlFX_vVEHdVlVzuNASj8";
        axios
            .put(`http://127.0.0.1:5000/stats/${pairName}`, stats, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            })
            .then((response) => {
                console.log("Stats updated successfully");
                setStats(response.data.stats);
            })
            .catch((error) => {
                console.error("Error updating stats:", error);
            });
    };

    return (
        <div className="h-full border m-4">
            {isLoading ? (
                <div className="flex justify-center items-center text-lg h-full">
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    <span className="font-bold">Loading...</span>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                    <Card className="col-span-full">
                        <CardHeader>
                            <CardTitle className="text-lg font-medium">Country Pair: {pairName}</CardTitle>
                        </CardHeader>
                        <CardFooter className="flex justify-end">
                            <Button
                                variant="danger"
                                onClick={handleDelete}
                                className="mr-2"
                            >
                                <Trash2 className="mr-2" />
                                Delete
                            </Button>
                            <Button
                                variant="primary"
                                onClick={handleUpdate}
                            >
                                <Edit className="mr-2" />
                                Update
                            </Button>
                        </CardFooter>
                    </Card>

                    {/* Success Rate Card */}
                    <Card
                        className={`${isHealthy ? "border-green-500" : "border-red-500"} border-2 p-4`}
                    >
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                            <CheckCircle
                                className={`w-4 h-4 ${isHealthy ? "text-green-500" : "text-red-500"}`}
                            />
                        </CardHeader>
                        <CardContent>
                            <div className="text-lg font-bold">{stats.total_rate_of_success.toFixed(2)}%</div>
                        </CardContent>
                    </Card>

                    {/* Failure Rate Card */}
                    <Card
                        className={`${isDangerous ? "border-red-500" : "border-green-500"} border-2 p-4`}
                    >
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium">Failure Rate</CardTitle>
                            <XCircle
                                className={`w-4 h-4 ${isDangerous ? "text-red-500" : "text-green-500"}`}
                            />
                        </CardHeader>
                        <CardContent>
                            <div className="text-lg font-bold">{stats.total_rate_of_failure.toFixed(2)}%</div>
                        </CardContent>
                    </Card>
                    {/* Total Messages Card */}
                    <Card className="p-4">
                        <CardHeader className="flex flex-row items-center justify-between pb-2">
                            <CardTitle className="text-sm font-medium">Total Messages</CardTitle>
                            <MessageCircle className="w-4 h-4 text-blue-500" />
                        </CardHeader>
                        <CardContent>
                            <div className="text-lg font-bold">{stats.total_sms_sent.toLocaleString()}</div>
                            <p className="text-xs text-gray-500 mt-1">
                                Failed: {stats.total_sms_failed.toLocaleString()}
                            </p>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
};

export default DisplaySelectedStats;