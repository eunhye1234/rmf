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