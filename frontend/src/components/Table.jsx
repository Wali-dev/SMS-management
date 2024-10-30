import { useState, useEffect } from 'react';
import axios from 'axios';
import { MdDragIndicator } from 'react-icons/md';
import { FaPlay, FaStop } from "react-icons/fa";
import { RiRestartLine } from "react-icons/ri";
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import DisplaySelectedStats from "../components/DisplaySelectedStats"

const StatusBadge = ({ status }) => {
    const bgColor = status === true ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800';
    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${bgColor}`}>
            {status.toString()}
        </span>
    );
};

const SkeletonRow = () => {
    return (
        <div className="grid grid-cols-12 items-center border-b border-gray-200 py-2 animate-pulse">
            <div className="col-span-2">
                <div className="flex items-center">
                    <div className="w-5 h-5 bg-gray-300 rounded-full"></div>
                    <div className="ml-2 w-24 h-4 bg-gray-300 rounded"></div>
                </div>
            </div>
            <div className="col-span-2">
                <div className="w-16 h-4 bg-gray-300 rounded"></div>
            </div>
            <div className="col-span-8 flex justify-end space-x-2">
                <div className="w-20 h-8 bg-gray-300 rounded"></div>
                <div className="w-20 h-8 bg-gray-300 rounded"></div>
                <div className="w-20 h-8 bg-gray-300 rounded"></div>
            </div>
        </div>
    );
};

const TableRow = ({ pairName, activeStatus, pair_id, handleAction, index, priority }) => {
    return (
        <Draggable draggableId={pair_id.toString()} index={index}>
            {(provided, snapshot) => (
                <div onClick={() => DisplaySelectedStats(pairName)}
                    ref={provided.innerRef}
                    {...provided.draggableProps}
                    className={`grid grid-cols-12 items-center border-b border-gray-200 py-2 hover:cursor-pointer hover:bg-slate-100 ${snapshot.isDragging ? 'bg-gray-50' : 'bg-white'
                        }`}
                >
                    <div className="col-span-4 ">
                        <div className="flex items-center">
                            <div {...provided.dragHandleProps} className="cursor-grab">
                                <MdDragIndicator />
                            </div>
                            <span className="ml-4">{pairName}</span>
                            <span className=" text-xs text-gray-500">(P: {priority})</span>
                        </div>
                    </div>
                    <div className="col-span-2 flex justify-around">
                        <StatusBadge status={activeStatus} />
                        <div>animation</div>
                    </div>
                    <div className="col-span-6 flex justify-end space-x-2">
                        <button className="px-4 py-2 text-black rounded">
                            <FaPlay onClick={() => handleAction('start', pairName)} />
                        </button>
                        <button className="px-4 py-2 text-black rounded">
                            <FaStop onClick={() => handleAction('stop', pairName)} />
                        </button>
                        <button className="px-4 py-2 text-black rounded">
                            <RiRestartLine
                                className='text-xl'
                                onClick={() => handleAction('restart', pairName)}
                            />
                        </button>
                    </div>
                </div>
            )}
        </Draggable>
    );
};

const Table = (trigger) => {
    const [pairs, setPairs] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [updateError, setUpdateError] = useState('');
    const [dragCounter, setDragCounter] = useState(0); // New state for forcing re-renders
    const bearerToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjcxZTQ4MTYzMmRkNjUwOGZiMGViOTkxIiwiZXhwIjoxNzMwMzQzMjExfQ.ZErCL4neknZ-f4YcVwnrKU5VlFX_vVEHdVlVzuNASj8';

    const loadPriorities = () => {
        const stored = localStorage.getItem('pairPriorities');
        return stored ? JSON.parse(stored) : {};
    };

    const savePriorities = (priorities) => {
        localStorage.setItem('pairPriorities', JSON.stringify(priorities));
    };

    const handleAction = (action, pairName) => {
        startStop(action, pairName);
    };

    const startStop = async (action, pairName) => {
        setIsLoading(true);
        try {
            const config = {
                headers: { Authorization: `Bearer ${bearerToken}` },
            };
            const requestData = {
                pair_name: pairName,
            };

            await axios.post(`http://127.0.0.1:5000/program/${action}`, requestData, config);
        } catch (error) {
            console.error('Error performing action:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const updatePriorityInBackend = async (pair_id, priority) => {
        try {
            const config = {
                headers: { Authorization: `Bearer ${bearerToken}` },
            };
            const requestData = {
                priority: priority
            };

            await axios.patch(
                `http://127.0.0.1:5000/program/update/${pair_id}`,
                requestData,
                config
            );

            const priorities = loadPriorities();
            priorities[pair_id] = priority;
            savePriorities(priorities);

            return true;
        } catch (error) {
            console.error(`Error updating priority for pair ${pair_id}:`, error);
            throw error;
        }
    };

    const reorderPairs = (pairsArray, startIndex, endIndex) => {
        const result = Array.from(pairsArray);
        const [removed] = result.splice(startIndex, 1);
        result.splice(endIndex, 0, removed);

        return result.map((pair, index) => ({
            ...pair,
            priority: index + 1
        }));
    };

    const onDragEnd = async (result) => {
        if (!result.destination) return;

        try {
            // Calculate new order
            const newPairs = reorderPairs(
                pairs,
                result.source.index,
                result.destination.index
            );

            // Update local state immediately
            setPairs(newPairs);

            // Increment drag counter to force re-render
            setDragCounter(prev => prev + 1);

            // Update priorities in backend and localStorage
            const updatePromises = newPairs.map((pair) =>
                updatePriorityInBackend(pair.pair_id, pair.priority)
            );

            await Promise.all(updatePromises);

            // Fetch updated data to ensure consistency
            await fetchPairs();

        } catch (error) {
            setUpdateError('Failed to save the new order. Please try again.');
            console.error('Error updating priorities:', error);
            // Revert to original state if there's an error
            await fetchPairs();
        }
    };

    const fetchPairs = async () => {
        try {
            const config = {
                headers: { Authorization: `Bearer ${bearerToken}` },
            };
            const response = await axios.get(
                'http://127.0.0.1:5000/program/pairs',
                config
            );

            const priorities = loadPriorities();

            const pairsWithPriority = response.data.map(pair => ({
                ...pair,
                priority: priorities[pair.pair_id] || Number.MAX_SAFE_INTEGER
            }));

            const sortedPairs = pairsWithPriority.sort((a, b) => a.priority - b.priority);

            setPairs(sortedPairs);
            setIsLoading(false);
        } catch (error) {
            console.error('Error fetching pairs:', error);
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchPairs();
    }, [bearerToken, trigger, dragCounter]); // Added dragCounter to dependencies

    return (
        <div className="bg-white rounded-md shadow m-3 px-2">
            {updateError && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4">
                    {updateError}
                </div>
            )}

            <div className="sticky top-0 z-10 bg-white">
                <div className="grid grid-cols-12 items-center border-b border-gray-200 bg-gray-50 font-medium text-gray-500 h-10">
                    <div className="col-span-4 ml-4">Pair Title</div>
                    <div className="col-span-2">Status</div>
                    <div className="col-span-6 text-center ml-10">Operations</div>
                </div>
            </div>

            <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId="pairs">
                    {(provided) => (
                        <div
                            ref={provided.innerRef}
                            {...provided.droppableProps}
                            className="max-h-[calc(100vh-10rem)] overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100"
                        >
                            {isLoading
                                ? Array.from({ length: 5 }, (_, index) => (
                                    <SkeletonRow key={index} />
                                ))
                                : pairs.map((row, index) => (
                                    <TableRow
                                        key={`${row.pair_id}-${dragCounter}`}
                                        pairName={row.pairName}
                                        activeStatus={row.activeStatus}
                                        pair_id={row.pair_id}
                                        handleAction={handleAction}
                                        index={index}
                                        priority={row.priority}
                                    />
                                ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>
        </div>
    );
};

export default Table;