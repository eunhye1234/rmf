#include "Core.hpp"
#include "Interface.hpp"
#include "RosInterface.hpp"

using namespace core;
using namespace task;
using namespace std;

Core::Core(Logger::s_ptr log, interface::RosInterface::s_ptr Interface)
    :log_(log) , Interface_(Interface)
{
    log_->Log(Log::LogLevel::INFO,"Core 객체 생성");
}

Core::~Core()
{
    log_->Log(Log::LogLevel::INFO,"Core 정상 종료");
}

bool Core::Initialize()
{
    //this 객체 shared_ptr 선언
    auto self = shared_from_this();

    pdispatcher_ = make_uptr<Dispatcher>(_MAX_EXECUTOR_NUM_, log_);
    
    log_->Log(Log::LogLevel::INFO,"Core Initialize Done");
    return true;
}
