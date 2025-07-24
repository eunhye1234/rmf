#pragma once

#include <memory>
#include <vector>
#include <string>
#include <functional>
#include <mutex>
#include <chrono>
#include <condition_variable>

#include "Logger.hpp"
using namespace Log;


template<typename T>
using vec = std::vector<T>;

using Task = std::function<void()>;