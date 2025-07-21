#include <iostream>
#include <memory>

#include "include/Core.hpp"
using namespace FMS;

int main()
{
    std::shared_ptr<FMS::Core> Core = std::make_shared<FMS::Core>();
    Core->Initialize();
}