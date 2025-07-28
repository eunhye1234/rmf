#pragma once

#include "Integrated.hpp"

namespace core
{
    class ICore
    {
    private:

    public:
        ICore() = default; 
        virtual ~ICore() = default;

        virtual bool SetAmrNextStep(Integrated::AmrStep step) = 0;

        virtual bool SetRobotArmNextStep(Integrated::RobotArmStep step) = 0;
    };
};

