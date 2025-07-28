#pragma once

namespace Commondefine
{
    #define _LOG_FILE_DIR_ "../../Log_file"

    #define _ROS_NODE_NAME_ std::string("robocallee_fms")

    #define _MAX_EXECUTOR_NUM_ 5

    enum AmrStep {AmrStep_num = 0};

    enum RobotArmStep {RobotArmStep_num = 0};
};


typedef struct Request
{
    std::string                 requester;
    shoesproperty               shoes_property;
    pose2d                      dest2

}Request; 
