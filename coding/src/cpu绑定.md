  一：绑定进程

#include <sched.h>

void setProcessToCPU(int _cpuID)

{

    cpu_set_t mask;

    cpu_set_t get;

    CPU_ZERO(&mask);

    CPU_SET(_cpuID, &mask);

    if (sched_setaffinity(0, sizeof(mask), &mask) < 0)

    {

        cout << "set process affinity failed\n" << endl;

    }

    CPU_ZERO(&get);

    if (sched_getaffinity(0, sizeof(get), &get) < 0)

    {

        cout << "get process affinity failed\n" << endl;

    }

}



二：绑定线程

#include <sched.h>

#include <string.h>

using namespace std;

void setThreadToCPU(int _cpuID)

{

    cpu_set_t mask;

    cpu_set_t get;

    CPU_ZERO(&mask);

    CPU_SET(_cpuID, &mask);

    if (pthread_setaffinity_np(pthread_self(), sizeof(mask), &mask) < 0)

    {

        cout << "set thread affinity failed\n" << endl;

    }

    CPU_ZERO(&get);

    if (pthread_getaffinity_np(pthread_self(), sizeof(get), &get) < 0)

    {

        cout << "get thread affinity failed\n" << endl;

    }

    else if(CPU_ISSET(_cpuID,&get)!=0)

    {

         cout << "get thread affinity _cpuID:" << _cpuID<<endl;

    }

}