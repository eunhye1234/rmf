#include "TaskManager.hpp"
#include "AmrAdapter.hpp"
#include "../Utile/Logger/include/Logger.hpp"
#include "RobotTaskInfo.hpp"

#include <vector>
#include <iostream>
#include <memory>
#include <queue>
#include <mutex>
#include <condition_variable>

#define RootDir "RoboCalleeFMS"
#define AMR_COUNT 3

namespace FMS
{

    class Core : public std::enable_shared_from_this<Core>
    {
    

    private:
        Task::TaskManager::s_ptr                        pTask_;
        std::vector<AMR::AmrAdapter::s_ptr>             pAmrAdapters_;
        Log::Logger::s_ptr                              log_;

        queue<shared_ptr<RobotTaskInfo>>                mainTaskQueue_;
        queue<shared_ptr<RobotTaskInfo>>                tempTaskQueue_;
        mutex                                           queueMutex_;
        condition_variable                              queueCondVar_;

    public:
        Core();
        ~Core();

        const Task::TaskManager::s_ptr  GetTask() const {return pTask_;} 
        const AMR::AmrAdapter::s_ptr GetpAmrAdapter(int index) const 
        {
            if(index > pAmrAdapters_.size() || pAmrAdapters_.empty()) return nullptr;

            return pAmrAdapters_[index];
        }

        bool Initialize();
        
        using StructPtr = shared_ptr<RobotTaskInfo>;
        bool PushTask(StructPtr& task);
        bool PopTask(StructPtr& popped_task);


    };
};