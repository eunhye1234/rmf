namespace FMS { class Core; }
namespace Task { class TaskManager; }

#pragma once
#include <memory>
#include <thread>
#include <mutex>
#include "../Utile/Logger/include/Logger.hpp"

namespace AMR
{
    class AmrAdapter
    {
    private:
        std::weak_ptr<FMS::Core>   Core_;
        Log::Logger::s_ptr          log_;
        const int                   id_;

    public:
        using s_ptr = std::shared_ptr<AmrAdapter>;
        using u_ptr = std::unique_ptr<AmrAdapter>;

        AmrAdapter(std::weak_ptr<FMS::Core> Core, int id, Log::Logger::s_ptr Log);
        ~AmrAdapter();

        bool SetSate(int a);
    };
};