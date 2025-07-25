namespace core { class Core; }

#pragma once

#include "Integrated.hpp"
#include "Interface.hpp"

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

namespace interface
{
    class RosInterface : public rclcpp::Node
    {
    private:
        Logger::s_ptr                           log_;
        Integrated::w_ptr<core::Core>           core_;
    public:
        using s_ptr = std::shared_ptr<RosInterface>;
        using u_ptr = std::shared_ptr<RosInterface>;
        using w_ptr = std::weak_ptr<RosInterface>;

        RosInterface(Logger::s_ptr log);
        ~RosInterface();

        bool Initialize(Integrated::w_ptr<core::Core> Core);
    };
};