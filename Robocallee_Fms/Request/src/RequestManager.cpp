#include "RequestManager.hpp"

using namespace Manager;

Manager::RequestManager(Integrated::w_ptr<core::ICore> Icore, Logger::s_ptr log)
    :Icore_(Icore), log_(log)
{
    log_->Log(Log::LogLevel::INFO, "RequestManager 객체 생성");
}

Manager::~RequestManager()
{
    log_->Log(Log::LogLevel::INFO, "RequestManager 객체 소멸");
}

void EnqueueRequest(const RobotRequest& r)
{
    std::lock_guard<std::mutex> lock(request_mtx_);
    request_queue_.push(r);
}

bool PopRequest(RobotRequest& r)
{
    std::lock_guard<std::mutex> lock(request_mtx_);
    if (request_queue_.empty()) return false;
    
    r = request_queue_.front();
    request_queue_.pop();
    return true

}