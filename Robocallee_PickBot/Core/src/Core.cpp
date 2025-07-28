#include "Core.hpp"

using namespace core;
using namespace Integrated;
using namespace Commondefine;
using namespace RA;
using namespace cv;

Core::Core(Logger::s_ptr log , Integrated::w_ptr<interface::RosInterface> Interface)
    :log_(log) , Interface_(Interface)
{
    log_->Log(INFO,"Core Initialize...");
    bool flag = false;

    RobotArm_ = make_uptr<RA::RobotArm>();
    flag = RobotArm_->Connet(JETCOBOT,BAUDRATE);
    if(!flag) log_->Log(FATAL,"Robot Arm 초기화 Fail");

    video_ = make_uptr<VideoCapture>();
    flag = video_->open(_CAM_INDEX_, CAP_V4L2);
    if(!flag) log_->Log(FATAL,"VideoCapture 초기화 Fail");

    calib_ = make_uptr<Calib::Calibrator>(_CALIB_FILE_DIR_);
}

Core::~Core()
{
    
}