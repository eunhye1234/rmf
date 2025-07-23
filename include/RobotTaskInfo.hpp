#include <string>
using namespace std;

struct RobotTaskInfo
{
    int robot_id;
    string robot_state = "IDLE";
    string job_state = "Wait";
    float battery = 100.0;
    string current_position;
    string dest1;
    string dest2;
    string dest3;
    string task_name;
    string customer_name;

};