#include "TaskManager.hpp"
#include "AmrAdapter.hpp"
#include "../Utile/Logger/include/Logger.hpp"

#include <vector>
#include <iostream>
#include <memory>

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
    };
};