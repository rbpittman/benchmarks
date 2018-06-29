/*

nvmlReturn_t nvmlDeviceGetHandleByIndex (unsigned
int index, nvmlDevice_t *device)
Parameters
index
The index of the target GPU, >= 0 and < accessibleDevices
device
Reference in which to return the device handle
Returns
‣ NVML_SUCCESS if device has been set
‣ NVML_ERROR_UNINITIALIZED if the library has not been successfully initialized
‣ NVML_ERROR_INVALID_ARGUMENT if index is invalid or device is NULL
Modules
www.nvidia.com
NVML vR384 | 47
‣ NVML_ERROR_INSUFFICIENT_POWER if any attached devices have improperly
attached external power cables
‣ NVML_ERROR_NO_PERMISSION if the user doesn't have permission to talk to this
device
‣ NVML_ERROR_IRQ_ISSUE if NVIDIA kernel detected an interrupt issue with the
attached GPUs
‣ NVML_ERROR_GPU_IS_LOST if the target GPU has fallen off the bus or is
otherwise inaccessible
‣ NVML_ERROR_UNKNOWN on any unexpected error



nvmlReturn_t nvmlDeviceGetFieldValues (nvmlDevice_t
device, int valuesCount, nvmlFieldValue_t *values)
Parameters
device
The device handle of the GPU to request field values for
valuesCount
Number of entries in values that should be retrieved
values
Array of valuesCount structures to hold field values. Each value's fieldId must be
populated prior to this call
Returns
‣ NVML_SUCCESS if any values in values were populated. Note that you must check
the nvmlReturn field of each value for each individual status
‣ NVML_ERROR_INVALID_ARGUMENT if device is invalid or values is NULL


Queryable field for nvlink counts
#define NVML_FI_DEV_NVLINK_LINK_COUNT



nvmlReturn_t nvmlDeviceGetNvLinkState (nvmlDevice_t
device, unsigned int link, nvmlEnableState_t *isActive)
Parameters
device
The identifier of the target device
link
Specifies the NvLink link to be queried
isActive
nvmlEnableState_t where NVML_FEATURE_ENABLED indicates that the link is
active and NVML_FEATURE_DISABLED indicates it is inactive
Returns
‣ NVML_SUCCESS if isActive has been set
‣ NVML_ERROR_UNINITIALIZED if the library has not been successfully initialized
Modules
www.nvidia.com
NVML vR384 | 127
‣ NVML_ERROR_INVALID_ARGUMENT if device or link is invalid or isActive is
NULL
‣ NVML_ERROR_NOT_SUPPORTED if the device doesn't support this feature
‣ NVML_ERROR_UNKNOWN on any unexpected error





nvmlReturn_t nvmlDeviceSetNvLinkUtilizationControl
(nvmlDevice_t device, unsigned int link, unsigned
int counter, nvmlNvLinkUtilizationControl_t *control,
unsigned int reset)
Parameters
device
The identifier of the target device
link
Specifies the NvLink link to be queried
counter
Specifies the counter that should be set (0 or 1).
control
A reference to the nvmlNvLinkUtilizationControl_t to set
Modules
www.nvidia.com
NVML vR384 | 131
reset
Resets the counters on set if non-zero
Returns
‣ NVML_SUCCESS if the control has been set successfully
‣ NVML_ERROR_UNINITIALIZED if the library has not been successfully initialized
‣ NVML_ERROR_INVALID_ARGUMENT if device, counter, link, or control is
invalid
‣ NVML_ERROR_NOT_SUPPORTED if the device doesn't support this feature
‣ NVML_ERROR_UNKNOWN on any unexpected error


nvmlReturn_t nvmlDeviceGetNvLinkUtilizationControl
(nvmlDevice_t device, unsigned int link, unsigned int
counter, nvmlNvLinkUtilizationControl_t *control)
Parameters
device
The identifier of the target device
link
Specifies the NvLink link to be queried
counter
Specifies the counter that should be set (0 or 1).
control
A reference to the nvmlNvLinkUtilizationControl_t to place information
Returns
‣ NVML_SUCCESS if the control has been set successfully
‣ NVML_ERROR_UNINITIALIZED if the library has not been successfully initialized
‣ NVML_ERROR_INVALID_ARGUMENT if device, counter, link, or control is
invalid
‣ NVML_ERROR_NOT_SUPPORTED if the device doesn't support this feature
‣ NVML_ERROR_UNKNOWN on any unexpected errornvmlReturn_t nvmlDeviceGetNvLinkUtilizationControl

*/

#include "nvml.h"
#include <stdio.h>

#define MAX_NUM_DEVICES 32

#define NVML_CHECK(error) nvml_check(error,__FILE__,__LINE__)

void nvml_check(nvmlReturn_t error, const char * filename, unsigned int line_num) {
  if(error == NVML_SUCCESS) {
    //success
  } else {
    fprintf(stderr, "NVML error code %d in file %s line %d\n", (int) error, filename, line_num);
  }
}

int main() {
  NVML_CHECK(nvmlInit());
  
  nvmlDevice_t devices[MAX_NUM_DEVICES];
  unsigned int num_devices = 0;
  while(nvmlDeviceGetHandleByIndex (num_devices, devices + num_devices) == NVML_SUCCESS) {
    num_devices++;
  }

  if(num_devices == 0) {
    fprintf(stderr, "Error: No devices found\n");
    nvmlShutdown();
    return(1);
  }

  unsigned int * num_links = new unsigned int[num_devices];

  nvmlFieldValue_t field_value = NVML_FI_DEV_NVLINK_LINK_COUNT;
  for(int i = 0; i < num_devices; i++) {
    NVML_CHECK(nvmlDeviceGetFieldValues (devices[i], 1, &field_value));
    
  }

  
  delete[] num_links;
  nvmlShutdown();
  return(0);
}
