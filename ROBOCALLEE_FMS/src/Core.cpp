#include "../include/Core.hpp"

using namespace FMS;
using namespace std;
using namespace Task;
using namespace AMR;
using namespace Log;


Core::Core()
{
    
}

Core::~Core()
{
    
}

bool Core::Initialize()
{
    //Log 생성
    log_ = make_shared<Log::Logger>(RootDir,true);

    //this 객체 shared_ptr 선언
    auto self = shared_from_this();
    pTask_ = make_shared<Task::TaskManager>(self, log_);
    for(int i = 0 ; i < AMR_COUNT; ++i)
    {
        auto ptr = make_shared<AMR::AmrAdapter>(self, i, log_);
        pAmrAdapters_.push_back(ptr);
    }

    log_->Log(Log::LogLevel::INFO,"Core Initialize 정상 수행");
    
    return true;
}