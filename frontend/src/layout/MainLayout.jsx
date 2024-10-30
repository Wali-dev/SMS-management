
import DisplayAndaddPairs from "../components/DisplayAndaddPairs"
import Navbar from "../components/Navbar"
import DisplayOverAllstats from "../components/DisplayOverAllstats"
import DisplaySelectedStats from "../components/DisplaySelectedStats"


const MainLayout = () => {
    return (
        <div className="grid grid-cols-12 h-screen">
            <div className="col-span-6 bg-slate-300">
                <Navbar />
                <DisplayAndaddPairs />
            </div>
            <div className="col-span-6">
                <div className="h-2/4">
                    <DisplayOverAllstats />
                </div>
                <div className="h-2/4">
                    <DisplaySelectedStats />
                </div>
            </div>

        </div>
    )
}

export default MainLayout