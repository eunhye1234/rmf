namespace FMS { class Core; }
namespace AMR { class AmrAdapter; }

#pragma once
#include <queue>
#include <memory>
#include <thread>
#include <mutex>
#include "../Utile/Logger/include/Logger.hpp"

namespace Task
{
    class TaskManager
    {
    private:
        std::weak_ptr<FMS::Core>   Core_;
        Log::Logger::s_ptr          log_;

        std::mutex                  Dispatcherlock_;
        std::thread                 DispatcherThread_;
        bool                        isRunning_;



        //------------------------------------private Functions
        void                        DispatcherThread();
    public:
        
        using s_ptr = std::shared_ptr<TaskManager>;
        using u_ptr = std::unique_ptr<TaskManager>;

        TaskManager(std::weak_ptr<FMS::Core> Core, Log::Logger::s_ptr Log);
        ~TaskManager();
    };
};