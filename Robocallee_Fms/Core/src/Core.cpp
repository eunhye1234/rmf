#include "Core.hpp"

using namespace core;
using namespace task;
using namespace std;


Core::Core()
{
    log_ = make_shared<Logger>(_LOG_FILE_DIR_, true);
    pdispatcher_ = make_unique<Dispatcher>(_MAX_EXECUTOR_NUM_, log_);
}

Core::~Core()
{

}

bool Core::assignTask(Task task)
{
    return pdispatcher_->Enqueue(std::move(task));
}