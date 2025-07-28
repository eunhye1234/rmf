#include "RobotArmAdapter.hpp"

using namespace Adapter;

RobotArmAdapter::RobotArmAdapter(Integrated::w_ptr<core::ICore> Icore, Logger::s_ptr log)
    :Icore_(Icore),log_(log)
{
    log_->Log(Log::LogLevel::INFO,"RobotArmAdapter 객체 생성");
}

RobotArmAdapter::~RobotArmAdapter()
{
    log_->Log(Log::LogLevel::INFO,"RobotArmAdapter 객체 소멸");
}