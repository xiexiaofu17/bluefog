// Modifications copyright (C) 2020 Bluefog Team. All Rights Reserved.
// Copyright 2019 Uber Technologies, Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
// ==============================================================================

#ifndef BLUEFOG_TORCH_HANDLE_MANAGER_H
#define BLUEFOG_TORCH_HANDLE_MANAGER_H

#include <atomic>
#include <memory>
#include <mutex>
#include <unordered_map>

#include "../common/common.h"

namespace bluefog {
namespace torch {

class HandleManager {
 public:
  int AllocateHandle();
  void MarkDone(int handle, const common::Status& status);
  bool PollHandle(int handle);
  std::shared_ptr<common::Status> ReleaseHandle(int handle);

 private:
  std::atomic_int last_handle_;
  std::unordered_map<int, std::shared_ptr<common::Status>> results_;
  std::mutex mutex_;
};

}  // namespace torch
}  // namespace bluefog

#endif  // BLUEFOG_TORCH_HANDLE_MANAGER_H
