
// #pragma once
// #include "Integrated.hpp"

// namespace interface
// {
//     class Interface
//     {
//     protected:
//         Integrated::w_ptr<core::Core>       core_;
    
//     public:
//         using s_ptr = std::shared_ptr<Interface>;
//         using u_ptr = std::unique_ptr<Interface>;
//         using w_ptr = std::weak_ptr<Interface>;

//         virtual ~Interface();

//         virtual bool Initialize(Integrated::w_ptr<core::Core> Core) = 0;
//     };
// };