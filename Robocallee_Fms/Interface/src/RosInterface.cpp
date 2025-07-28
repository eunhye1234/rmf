#include "RosInterface.hpp"

using namespace interface;
using namespace Integrated;

RosInterface::RosInterface(Logger::s_ptr log)
: Node(_ROS_NODE_NAME_), log_(log)
{

}

RosInterface::~RosInterface(){}

bool RosInterface::Initialize(Integrated::w_ptr<core::ICore> Icore)
{
    Icore_ = Icore;
    


    return true;
}

void RosInterface::CreateRequestService()  //////
{
    using ReqServiceType = robocallee_fms::srv::ProcessRequest;         /////need to change the name "ProcessRequest"

    req_service_ = this->create_service<ReqServiceType>(
        "process_request",    ///need to change the name "process_request"
        [this](const std::shared_ptr<ReqServiceType::Request> request,
        std::shared_ptr<ReqServiceType::Response> response)
        {
            if (auto icore = Icore_.lock())
            {
                icore->HandleRequestService(request, response);
            }
            else
            {
                RCLCPP_ERROR(this->get_logger(), "ICore expired");
                response->accepted = false;

            }
        });
}

void RosInterface::CreateDoneService()
{
    using DoneServiceType = robocallee_fms::srv::ProcessDone;

    done_service == this->create_service<DoneServiceType>(
        "process_done",
        [this](const std::shared_ptr<DoneServiceType::Request> request,
               std::shared_ptr<DoneServiceType::Response> response)
        {
            if (auto icore = Icore_.lock())
            {
                icore->HandleDoneService(request, response);
            }
            else
            {
                RCLCPP_ERROR(this->get_logger(), "ICore expired");
                response->accepted = false;
            }
        });


}