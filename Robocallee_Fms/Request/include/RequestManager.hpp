// #include "Integrated.hpp"
#include "Commondefine.hpp"

#include "ICore.hpp"

namespace Manager
{
    class RequestManager
    {
    private:
        Integrated::w_ptr<core::Icore>              Icore_;
        Logger::s_ptr                               log_;
        std::queue<RobotRequest>                    request_queue_;
        std::mutex                                  reqeust_mtx_;

    public:
        using u_ptr = Integrated::u_ptr<RequestManager>;

        RequestManager(Integrated::w_ptr<core::ICore> Icore, Logger::s_ptr log);
        ~RequestManager();

        void EnqueueRequest(const RobotRequest& r);
        bool PopRequest(RobotRequest& r);
        
    };

};