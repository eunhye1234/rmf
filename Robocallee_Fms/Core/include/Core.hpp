#include <memory>
#include "Dispatcher.hpp"

#define _MAX_EXECUTOR_NUM_ 5
#define _LOG_FILE_DIR_ "../../Log_file"

namespace core
{
    class Core : public std::enable_shared_from_this<Core>
    {
    private:
        task::Dispatcher::u_ptr             pdispatcher_;
        Logger::s_ptr                       log_;

    public:
        using s_ptr = std::shared_ptr<Core>;

        Core();
        ~Core();

        bool assignTask(Task task);
    };
};