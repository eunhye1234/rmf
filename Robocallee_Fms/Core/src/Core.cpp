#include "Core.hpp"

using namespace core;
using namespace task;
using namespace Integrated;
using namespace Commondefine;
using namespace Adapter;
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

    pAmrAdapter_ = make_uptr<AmrAdapter>(self, log_);

    pRobotArmAdapter_ = make_uptr<RobotArmAdapter>(self, log_);

    log_->Log(Log::LogLevel::INFO,"Core Initialize Done");
    
    return true;
}


bool Core::SetAmrNextStep(Commondefine::AmrStep step)
{
    switch (step)
    {
    case AmrStep_num:
        break;
    
    default:
        break;
    }

    return true;
}

bool Core::SetRobotArmNextStep(Commondefine::RobotArmStep step)
{
    switch (step)
    {
    case RobotArmStep_num:
        break;
    
    default:
        break;
    }

    return true;
}

//////////
void Core::HandleRequestService(const std::shared_ptr<ReqServiceType::Request>& request,
                                  std::shared_ptr<ReqServiceType::Response>& response)
{
    RobotRequest r;
    r.requester = request->requester;
    r.shoe_model.size = request->size;
    r.shoe_model.model = request->model;
    r.shoe_model.color = request->color;
    r.dest2.x = request->x;
    r.dest2.y = request->y;

    log_->Log(Log::LogLevel::INFO, "Request received: " + r.shoe_model.model);

    if (request_manager_)
    {
        request_manager_->EnqueueRequest(r);
        reponse->accepted = true;
        // addTask(best_pinky_selector());
    }
    else
    {
        response->accepted = false;
    }
}
                    
void Core::HandleDoneService(const std::shared_ptr<DoneServiceType::Request>& request,
                                  std::shared_ptr<DoneServiceType::Response>& response)
{
    log_->Log(Log::LogLevel::INFO, "Done received from: ", request->requester);

    if (request->requester == "customer")
    {
        // taskinfo->robot_state = IDLE;
        // addTask(best_pinky_selector());
        response->accepted = true;
    }
    else if (request->requester == "employee")
    {
        // addTask(MoveTo_dest2(dest2, pinky_id));
        response->accepted = true;
    }
}