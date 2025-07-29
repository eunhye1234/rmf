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
    using ReqServiceType = robocallee_fms::srv::ShoeRequest;        

    req_service_ = this->create_service<ReqServiceType>(
        "process_request",    ///need to change the name "process_request"
        [this](const std::shared_ptr<ReqServiceType::Request> request,
        std::shared_ptr<ReqServiceType::Response> response)
        {
            Commondefine::GUIRequest r;
            r.requester = request->requester;
            r.shoes_property.size = request->size;
            r.shoes_property.model = request->model;
            r.shoes_property.color = request->color;
            r.dest2.x = request->x;
            r.dest2.y = request->y;

            if (auto icore = Icore_.lock())
            {
                bool accepted = icore->RequestCallback(r);
                response->accepted = accepted;
            }
            else
            {
                log_->Log(Log::LogLevel::INFO, "ICore expired");
                response->accepted = false;

            }
        });
}

void RosInterface::CreateDoneService()
{
    using DoneServiceType = robocallee_fms::srv::DoneMsg;

    done_service_ = this->create_service<DoneServiceType>(
        "process_done",
        [this](const std::shared_ptr<DoneServiceType::Request> request,
               std::shared_ptr<DoneServiceType::Response> response)
        {
            std::string requester;
            requester = request->requester;

            if (auto icore = Icore_.lock())
            {
                bool accepted = icore->DoneCallback(requester);
                response->accepted = accepted;
            }
            else
            {
                log_->Log(Log::LogLevel::INFO, "ICore expired");
                response->accepted = false;
            }
        });


}