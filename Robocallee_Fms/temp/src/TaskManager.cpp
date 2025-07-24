#include "../include/AmrAdapter.hpp"
#include "../include/Core.hpp"

using namespace std;
using namespace Task;

Task::TaskManager::TaskManager(std::weak_ptr<FMS::Core> Core,Log::Logger::s_ptr Log)
    :Core_(Core), log_(Log), isRunning_(true)
{
    DispatcherThread_ = thread(&TaskManager::DispatcherThread,this);
}

Task::TaskManager::~TaskManager()
{
    isRunning_ = true;
    if(DispatcherThread_.joinable())
    {
        DispatcherThread_.join();
        log_->Log(Log::LogLevel::INFO,"TaskManager Thread 정상 종료");
    }

    return;
}

void Task::TaskManager::DispatcherThread()
{
    log_->Log(Log::LogLevel::INFO,"TaskManager Thread 시작");
    
    while(isRunning_)
    {
        std::lock_guard lock(Dispatcherlock_);

        if(auto p = Core_.lock())
        {
            p->GetpAmrAdapter(0)->SetSate(10)
        }
    }

    log_->Log(Log::LogLevel::INFO,"TaskManager Thread 종료");
    return;
}