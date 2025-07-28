#pragma once

#include "Integrated.hpp"
#include "Commondefine.hpp"

namespace core
{
    class ICore
    {
    private:

    public:
        ICore() = default; 
        virtual ~ICore() = default;

        virtual bool SetAmrNextStep(Commondefine::AmrStep step) = 0;

        virtual bool SetRobotArmNextStep(Commondefine::RobotArmStep step) = 0;
        
    };
};

