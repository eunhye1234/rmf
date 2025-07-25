#pragma once

#include <future>
#include <type_traits>

#include "Dispatcher.hpp"
#include "RosInterface.hpp"

using namespace Integrated;

#define _MAX_EXECUTOR_NUM_ 5


namespace core
{
    class Core : public std::enable_shared_from_this<Core>
    {
    private:
        task::Dispatcher::u_ptr             pdispatcher_;
        Logger::s_ptr                       log_;
        std::mutex                          assignmtx_;
        interface::RosInterface::s_ptr      Interface_;
    public:
        using s_ptr = std::shared_ptr<Core>;
        using u_ptr = std::unique_ptr<Core>;
        using w_ptr = std::weak_ptr<Core>;
    

        Core(Logger::s_ptr log , interface::RosInterface::s_ptr Interface_);
        ~Core();

        template<typename F, typename... Args>
        auto assignTask(F&& f, Args&&... args)-> std::future<typename std::invoke_result<F, Args...>::type>;

        bool Initialize();
    };

    template<typename F, typename... Args>
    auto Core::assignTask(F&& f, Args&&... args)-> std::future<typename std::invoke_result<F, Args...>::type>
    {
        std::lock_guard lock(assignmtx_);

        using return_type = typename std::invoke_result<F, Args...>::type;

        auto task = std::make_shared<std::packaged_task<return_type()>>
        (
            std::bind(std::forward<F>(f), std::forward<Args>(args)...)
        );

        std::future<return_type> fut = task->get_future();

        pdispatcher_->Enqueue([task]() { (*task)();} );
        
        return fut;
    }
};