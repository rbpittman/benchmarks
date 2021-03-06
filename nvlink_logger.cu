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
#include <unistd.h>
#include <signal.h>
#include <sys/time.h>
#include <vector>
using namespace std;
#define MAX_NUM_DEVICES 32
#define NUM_CONTROLS 1

#define NVML_CHECK(error) nvml_check(error,__FILE__,__LINE__)


//This value is not defined in the nvml.h header for cuda-9.0, but is
//included in the docs...
#define NVML_FI_DEV_NVLINK_LINK_COUNT 91

//Nvlink counter to use (0 or 1)
#define GET_BYTES 0
#define GET_PACKETS 1

void nvml_check(nvmlReturn_t error, const char * filename, unsigned int line_num) {
  if(error == NVML_SUCCESS) {
    //success
  } else {
    fprintf(stderr, "NVML error code %d in file %s line %d\n", (int) error, filename, line_num);
  }
}

double get_time() {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return(tv.tv_sec + (tv.tv_usec/1000000.));
}

FILE * file_handle = NULL;
bool kill_process = false;

void sig_term_handler(int signum, siginfo_t *info, void *ptr) {
  printf("Caught kill signal, closing data file\n");
  kill_process = true;
}

void catch_sigterm() {
  static struct sigaction _sigact;

  memset(&_sigact, 0, sizeof(_sigact));
  _sigact.sa_sigaction = sig_term_handler;
  _sigact.sa_flags = SA_SIGINFO;

  sigaction(SIGTERM, &_sigact, NULL);
  sigaction(SIGINT, &_sigact, NULL);
}

void write_header(FILE * file_handle, int num_devices, unsigned int * num_links) {
  fprintf(file_handle, "time(sec)");
  for(int gpu_i = 0; gpu_i < num_devices; gpu_i++) {
    for(int link_i = 0; link_i < num_links[gpu_i]; link_i++) {
      fprintf(file_handle, ",GPU%d_L%d", gpu_i, link_i);
    }
  }
  fprintf(file_handle, "\n");
}

//Writes times to first col, data to rest of cols. Uses num_cols for
//the length of each row in data. 
void write_data(FILE * file_handle, vector<double> & times, vector<unsigned long long *> & data, int num_cols) {
  unsigned long long * data_row;
  for(int i = 0; i < data.size(); ++i) {
    data_row = data.at(i);
    fprintf(file_handle, "%f", times.at(i));
    for(int j = 0; j < num_cols; j++) {
      fprintf(file_handle, ",%llu", data_row[j]);
    }
    fprintf(file_handle, "\n");
  }
}


  //==================//
 //==     MAIN     ==//
//==================//

int main(int argc, char ** argv) {
  useconds_t delay = 1000000;//micro seconds
  if(argc >= 2) {
    delay = (useconds_t) (atof(argv[1]) * 1000000);
  }
  printf("Delay %d microseconds\n", delay);
  
  NVML_CHECK(nvmlInit());
  
  nvmlDevice_t devices[MAX_NUM_DEVICES];
  unsigned int num_devices = 0;
  while(nvmlDeviceGetHandleByIndex (num_devices, devices + num_devices) == NVML_SUCCESS) {
    num_devices++;
  }
  //Only log first gpu
  // num_devices = 1;
  
  if(num_devices == 0) {
    fprintf(stderr, "Error: No devices found\n");
    nvmlShutdown();
    return(1);
  }

  unsigned int * num_links = new unsigned int[num_devices];
  
  nvmlFieldValue_t field_value;
  field_value.fieldId = NVML_FI_DEV_NVLINK_LINK_COUNT;
  unsigned int total_links = 0;
  for(int i = 0; i < num_devices; i++) {
    NVML_CHECK(nvmlDeviceGetFieldValues (devices[i], 1, &field_value));
    num_links[i] = field_value.value.uiVal;
    total_links += field_value.value.uiVal;
  }
  
  // char str[200];
  // nvmlSystemGetNVMLVersion(str, 200);
  // printf("%s\n", str);
  nvmlEnableState_t enabled_state;
  for(int gpu_i = 0; gpu_i < num_devices; gpu_i++) {
    for(int link_i = 0; link_i < num_links[gpu_i]; link_i++) {
      NVML_CHECK(nvmlDeviceGetNvLinkState(devices[gpu_i], link_i, &enabled_state));
      if(enabled_state != NVML_FEATURE_ENABLED) {
	fprintf(stderr, "Link not enabled\n");
	return(1);
      }
    }
  }
  
  nvmlNvLinkUtilizationControl_t controls[NUM_CONTROLS];
  controls[0].pktfilter = NVML_NVLINK_COUNTER_PKTFILTER_ALL;//All types of packets
  controls[0].units     = NVML_NVLINK_COUNTER_UNIT_BYTES;
  if(NUM_CONTROLS > 1) {
    controls[1].pktfilter = NVML_NVLINK_COUNTER_PKTFILTER_ALL;//All types of packets
    controls[1].units     = NVML_NVLINK_COUNTER_UNIT_CYCLES;
  }
  
  
  for(int control_idx = 0; control_idx < NUM_CONTROLS; control_idx++) {
    for(int gpu_i = 0; gpu_i < num_devices; gpu_i++) {
      for(int link_i = 0; link_i < num_links[gpu_i]; link_i++) {
	//Set utilization counter for device gpu_i, link_i, specified
	//COUNTER, with all packets and units of bytes control, and true
	//reset counter to 0. 
	NVML_CHECK(nvmlDeviceSetNvLinkUtilizationControl(devices[gpu_i], link_i,
							 control_idx, controls + control_idx, 1));
      }
    }
  }
  
  int col = 0;
  unsigned long long rx, tx;
  unsigned long long * data_row;
  double start_time = -1.0;
  double curr_time;
  vector<double> times;
  vector<unsigned long long *> data[NUM_CONTROLS];
  
  catch_sigterm();
  while(!kill_process) {
    curr_time = get_time();
    if(start_time == -1.0) {
      start_time = curr_time;
    }
    for(int control_idx = 0; control_idx < NUM_CONTROLS; control_idx++) {
      col = 0;
      data_row = new unsigned long long[total_links];
      for(int gpu_i = 0; gpu_i < num_devices; gpu_i++) {
	for(int link_i = 0; link_i < num_links[gpu_i]; link_i++) {
	  NVML_CHECK(nvmlDeviceGetNvLinkUtilizationCounter(devices[gpu_i], link_i, control_idx, &rx, &tx));
	  if(controls[control_idx].units == NVML_NVLINK_COUNTER_UNIT_BYTES)
	    data_row[col++] = 8 * tx;//convert bytes to bits
	  else
	    data_row[col++] = tx;
	}
      }
      data[control_idx].push_back(data_row);
    }
    times.push_back(curr_time-start_time);
    usleep(delay);
  }
  
  //Write data for control 1
  file_handle = fopen("nvlink_usage_bits.csv", "w");
  if(file_handle == NULL) {
    fprintf(stderr, "Could not open output file\n");
    return(1);
  }
  
  write_header(file_handle, num_devices, num_links);
  write_data(file_handle, times, data[0], total_links);
  fclose(file_handle);

  if(NUM_CONTROLS > 1) {
    file_handle = fopen("nvlink_usage_cycles.csv", "w");
    if(file_handle == NULL) {
      fprintf(stderr, "Could not open output file\n");
      return(1);
    }
    
    write_header(file_handle, num_devices, num_links);
    write_data(file_handle, times, data[1], total_links);
    fclose(file_handle);
  }
  
  for(int control_idx = 0; control_idx < NUM_CONTROLS; control_idx++) {
    for(int i = 0; i < data[control_idx].size(); i++) {
      delete[] data[control_idx].at(i);
    }
  }
  delete[] num_links;
  nvmlShutdown();
  return(0);
}
