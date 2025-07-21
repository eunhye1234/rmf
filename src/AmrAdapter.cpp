#include "../include/AmrAdapter.hpp"
#include "../include/Core.hpp"

using namespace std;
using namespace AMR;

AMR::AmrAdapter::AmrAdapter(std::weak_ptr<FMS::Core> Core, int id, Log::Logger::s_ptr Log)
    :Core_(Core), log_(Log), id_(id)
{


}

AMR::AmrAdapter::~AmrAdapter()
{
    
}